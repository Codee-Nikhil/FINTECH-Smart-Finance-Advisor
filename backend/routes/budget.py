from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from database import db
from models import Budget, Expense
from datetime import datetime

budget_bp = Blueprint('budget', __name__)

DEFAULT_CATEGORIES = [
    'Rent / Housing', 'Food & Groceries', 'Transport',
    'Utilities', 'Entertainment', 'Healthcare',
    'Education / EMI', 'Clothing', 'Personal Care', 'Miscellaneous'
]


def get_or_create_budget(user_id, month, year):
    budget = Budget.query.filter_by(user_id=user_id, month=month, year=year).first()
    if not budget:
        budget = Budget(user_id=user_id, month=month, year=year)
        db.session.add(budget)
        db.session.flush()
        # Add default categories
        for cat in DEFAULT_CATEGORIES:
            expense = Expense(budget_id=budget.id, category=cat, actual=0, budget_amt=0)
            db.session.add(expense)
        db.session.commit()
    return budget


# ── GET BUDGET ────────────────────────────────────────────────────
@budget_bp.route('/', methods=['GET'])
@jwt_required()
def get_budget():
    user_id = int(get_jwt_identity())
    month   = request.args.get('month', datetime.now().strftime('%B'))
    year    = int(request.args.get('year', datetime.now().year))

    budget = get_or_create_budget(user_id, month, year)
    return jsonify({'budget': budget.to_dict()}), 200


# ── UPDATE INCOME ─────────────────────────────────────────────────
@budget_bp.route('/income', methods=['PUT'])
@jwt_required()
def update_income():
    user_id = int(get_jwt_identity())
    data    = request.get_json()
    month   = data.get('month', datetime.now().strftime('%B'))
    year    = int(data.get('year', datetime.now().year))
    income  = float(data.get('income', 0))

    budget = get_or_create_budget(user_id, month, year)
    budget.income = income
    db.session.commit()

    return jsonify({'message': 'Income updated', 'income': income}), 200


# ── UPDATE EXPENSE ────────────────────────────────────────────────
@budget_bp.route('/expense/<int:expense_id>', methods=['PUT'])
@jwt_required()
def update_expense(expense_id):
    user_id = int(get_jwt_identity())
    data    = request.get_json()

    expense = Expense.query.get_or_404(expense_id)

    # Security: make sure this expense belongs to this user
    if expense.budget.user_id != user_id:
        return jsonify({'error': 'Unauthorized'}), 403

    if 'actual'     in data: expense.actual     = float(data['actual'])
    if 'budget_amt' in data: expense.budget_amt = float(data['budget_amt'])

    db.session.commit()
    return jsonify({'message': 'Expense updated', 'expense': expense.to_dict()}), 200


# ── ADD CUSTOM CATEGORY ───────────────────────────────────────────
@budget_bp.route('/expense', methods=['POST'])
@jwt_required()
def add_expense():
    user_id = int(get_jwt_identity())
    data    = request.get_json()
    month   = data.get('month', datetime.now().strftime('%B'))
    year    = int(data.get('year', datetime.now().year))

    if not data.get('category'):
        return jsonify({'error': 'Category name is required'}), 400

    budget  = get_or_create_budget(user_id, month, year)
    expense = Expense(
        budget_id  = budget.id,
        category   = data['category'].strip(),
        actual     = float(data.get('actual', 0)),
        budget_amt = float(data.get('budget_amt', 0)),
    )
    db.session.add(expense)
    db.session.commit()

    return jsonify({'message': 'Category added', 'expense': expense.to_dict()}), 201


# ── DELETE CUSTOM CATEGORY ────────────────────────────────────────
@budget_bp.route('/expense/<int:expense_id>', methods=['DELETE'])
@jwt_required()
def delete_expense(expense_id):
    user_id = int(get_jwt_identity())
    expense = Expense.query.get_or_404(expense_id)

    if expense.budget.user_id != user_id:
        return jsonify({'error': 'Unauthorized'}), 403

    db.session.delete(expense)
    db.session.commit()
    return jsonify({'message': 'Category deleted'}), 200


# ── GET ALL MONTHS (history) ──────────────────────────────────────
@budget_bp.route('/history', methods=['GET'])
@jwt_required()
def get_history():
    user_id = int(get_jwt_identity())
    budgets = Budget.query.filter_by(user_id=user_id).order_by(Budget.year.desc(), Budget.id.desc()).all()
    return jsonify({'history': [b.to_dict() for b in budgets]}), 200


# ── SAVE ENTIRE BUDGET AT ONCE (bulk save from frontend) ──────────
@budget_bp.route('/save', methods=['POST'])
@jwt_required()
def save_budget():
    user_id  = int(get_jwt_identity())
    data     = request.get_json()
    month    = data.get('month', datetime.now().strftime('%B'))
    year     = int(data.get('year', datetime.now().year))
    income   = float(data.get('income', 0))
    expenses = data.get('expenses', [])   # list of {category, actual, budget_amt}

    budget = get_or_create_budget(user_id, month, year)
    budget.income = income

    # Update or create each expense row
    for exp_data in expenses:
        cat     = exp_data.get('category', '').strip()
        actual  = float(exp_data.get('actual', 0))
        budget_amt = float(exp_data.get('budget_amt', 0))

        existing = Expense.query.filter_by(budget_id=budget.id, category=cat).first()
        if existing:
            existing.actual     = actual
            existing.budget_amt = budget_amt
        else:
            db.session.add(Expense(budget_id=budget.id, category=cat, actual=actual, budget_amt=budget_amt))

    db.session.commit()
    return jsonify({'message': 'Budget saved successfully', 'budget': budget.to_dict()}), 200
