from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from database import db
from models import User, Budget, Goal, ChatLog
from google import genai
from google.genai import types
import os

advisor_bp = Blueprint('advisor', __name__)


def build_system_prompt(user, budgets, goals):
    latest    = budgets[0] if budgets else None
    income    = latest.income if latest else 0
    expenses  = latest.expenses if latest else []
    total_exp = sum(e.actual for e in expenses)
    savings   = income - total_exp
    rate      = round((savings / income) * 100, 1) if income else 0

    cat_lines = '\n'.join(
        f"  - {e.category}: Rs.{e.actual}"
        + (f" (budget: Rs.{e.budget_amt})" if e.budget_amt else "")
        for e in expenses if e.actual > 0
    ) or '  No expenses recorded yet'

    goal_lines = '\n'.join(
        f"  - {g.name}: Rs.{g.saved} saved of Rs.{g.target} target"
        + (f" (by {g.target_date})" if g.target_date else "")
        for g in goals
    ) or '  No goals set yet'

    return f"""You are FinTech, a warm and expert Indian personal finance advisor.

USER PROFILE:
- Name: {user.name}
- City type: {user.city_type}

CURRENT FINANCES:
- Monthly Income: Rs.{income:,.0f}
- Total Monthly Expenses: Rs.{total_exp:,.0f}
- Monthly Savings: Rs.{savings:,.0f}
- Savings Rate: {rate}%

EXPENSE BREAKDOWN:
{cat_lines}

FINANCIAL GOALS:
{goal_lines}

INSTRUCTIONS:
- Personalise every response using the user's actual numbers above.
- Suggest Indian instruments: SIP, PPF, ELSS, NPS, FD, RD, NSC.
- Mention tax benefits under 80C and 80D where relevant.
- Use Indian number formatting (rupees, lakhs, crores).
- Be warm, practical and encouraging.
- Keep responses under 200 words unless asked for more detail.
- Use bullet points for lists and bold for key numbers."""


# ── CHAT ──────────────────────────────────────────────────────────
@advisor_bp.route('/chat', methods=['POST'])
@jwt_required()
def chat():
    user_id = int(get_jwt_identity())
    data    = request.get_json()
    message = data.get('message', '').strip()

    if not message:
        return jsonify({'error': 'Message cannot be empty'}), 400

    user    = User.query.get_or_404(user_id)
    budgets = Budget.query.filter_by(user_id=user_id).order_by(Budget.year.desc(), Budget.id.desc()).limit(3).all()
    goals   = Goal.query.filter_by(user_id=user_id).all()

    recent_logs = (ChatLog.query
                   .filter_by(user_id=user_id)
                   .order_by(ChatLog.created_at.asc())
                   .limit(10).all())

    # Save user message
    db.session.add(ChatLog(user_id=user_id, role='user', message=message))
    db.session.flush()

    try:
        api_key = os.getenv('GEMINI_API_KEY') or current_app.config.get('GEMINI_API_KEY', '')
        if not api_key:
            return jsonify({'error': 'Gemini API key not configured. Add GEMINI_API_KEY to your .env file'}), 500

        client = genai.Client(api_key=api_key)

        # Build conversation history
        history = []
        for log in recent_logs:
            role = 'user' if log.role == 'user' else 'model'
            history.append(types.Content(role=role, parts=[types.Part(text=log.message)]))

        # Add current message
        history.append(types.Content(role='user', parts=[types.Part(text=message)]))

        response = client.models.generate_content(
            model='gemini-2.0-flash',
            config=types.GenerateContentConfig(
                system_instruction=build_system_prompt(user, budgets, goals),
                max_output_tokens=1000,
                temperature=0.7,
            ),
            contents=history,
        )

        reply = response.text

        # Save assistant reply
        db.session.add(ChatLog(user_id=user_id, role='assistant', message=reply))
        db.session.commit()

        return jsonify({'reply': reply, 'role': 'assistant'}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'AI service error: {str(e)}'}), 500


# ── GET CHAT HISTORY ──────────────────────────────────────────────
@advisor_bp.route('/history', methods=['GET'])
@jwt_required()
def get_history():
    user_id = int(get_jwt_identity())
    logs    = (ChatLog.query
               .filter_by(user_id=user_id)
               .order_by(ChatLog.created_at.asc())
               .limit(50).all())
    return jsonify({'history': [log.to_dict() for log in logs]}), 200


# ── CLEAR CHAT HISTORY ────────────────────────────────────────────
@advisor_bp.route('/history', methods=['DELETE'])
@jwt_required()
def clear_history():
    user_id = int(get_jwt_identity())
    ChatLog.query.filter_by(user_id=user_id).delete()
    db.session.commit()
    return jsonify({'message': 'Chat history cleared'}), 200
