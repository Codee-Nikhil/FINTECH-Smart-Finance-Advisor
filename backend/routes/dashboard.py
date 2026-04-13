from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import User, Budget, Goal
from datetime import datetime

dashboard_bp = Blueprint('dashboard', __name__)


@dashboard_bp.route('/summary', methods=['GET'])
@jwt_required()
def get_summary():
    user_id = int(get_jwt_identity())
    user    = User.query.get_or_404(user_id)

    month = request.args.get('month', datetime.now().strftime('%B'))
    year  = int(request.args.get('year', datetime.now().year))

    budget = Budget.query.filter_by(user_id=user_id, month=month, year=year).first()
    goals  = Goal.query.filter_by(user_id=user_id).all()

    if not budget:
        return jsonify({
            'user': user.to_dict(),
            'income': 0, 'total_expenses': 0,
            'savings': 0, 'savings_rate': 0,
            'health_score': 0, 'goals': [],
            'expenses': [], 'month': month, 'year': year,
        }), 200

    income    = budget.income
    total_exp = sum(e.actual for e in budget.expenses)
    savings   = income - total_exp
    rate      = round((savings / income) * 100, 1) if income else 0

    # Health score calculation
    score = 0
    if rate >= 30: score += 40
    elif rate >= 20: score += 30
    elif rate >= 10: score += 15
    elif rate > 0: score += 5

    rent_exp = next((e for e in budget.expenses if 'rent' in e.category.lower() or 'housing' in e.category.lower()), None)
    if rent_exp and income:
        rent_pct = rent_exp.actual / income
        if rent_pct <= 0.25: score += 20
        elif rent_pct <= 0.35: score += 10
    else:
        score += 20

    budgeted    = [e for e in budget.expenses if e.budget_amt > 0]
    over_budget = [e for e in budgeted if e.actual > e.budget_amt]
    if budgeted:
        compliance = 1 - len(over_budget) / len(budgeted)
        score += round(compliance * 25)
    else:
        score += 15

    if goals: score += 15
    score = min(score, 100)

    # History: last 6 months
    history_budgets = (Budget.query
                       .filter_by(user_id=user_id)
                       .order_by(Budget.year.desc(), Budget.id.desc())
                       .limit(6).all())

    monthly_trend = [
        {
            'month':    b.month,
            'year':     b.year,
            'income':   b.income,
            'expenses': sum(e.actual for e in b.expenses),
            'savings':  b.income - sum(e.actual for e in b.expenses),
        }
        for b in reversed(history_budgets)
    ]

    return jsonify({
        'user':           user.to_dict(),
        'month':          month,
        'year':           year,
        'income':         income,
        'total_expenses': total_exp,
        'savings':        savings,
        'savings_rate':   rate,
        'health_score':   score,
        'expenses':       [e.to_dict() for e in budget.expenses],
        'goals':          [g.to_dict() for g in goals],
        'monthly_trend':  monthly_trend,
    }), 200
