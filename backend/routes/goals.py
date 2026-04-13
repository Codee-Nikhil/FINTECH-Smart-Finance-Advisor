from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from database import db
from models import Goal

goals_bp = Blueprint('goals', __name__)


# ── GET ALL GOALS ─────────────────────────────────────────────────
@goals_bp.route('/', methods=['GET'])
@jwt_required()
def get_goals():
    user_id = int(get_jwt_identity())
    goals   = Goal.query.filter_by(user_id=user_id).order_by(Goal.created_at.desc()).all()
    return jsonify({'goals': [g.to_dict() for g in goals]}), 200


# ── ADD GOAL ──────────────────────────────────────────────────────
@goals_bp.route('/', methods=['POST'])
@jwt_required()
def add_goal():
    user_id = int(get_jwt_identity())
    data    = request.get_json()

    if not data.get('name') or not data.get('target'):
        return jsonify({'error': 'Goal name and target amount are required'}), 400

    goal = Goal(
        user_id     = user_id,
        name        = data['name'].strip(),
        target      = float(data['target']),
        saved       = float(data.get('saved', 0)),
        goal_type   = data.get('goal_type', 'other'),
        target_date = data.get('target_date', ''),
    )
    db.session.add(goal)
    db.session.commit()

    return jsonify({'message': 'Goal added successfully', 'goal': goal.to_dict()}), 201


# ── UPDATE GOAL ───────────────────────────────────────────────────
@goals_bp.route('/<int:goal_id>', methods=['PUT'])
@jwt_required()
def update_goal(goal_id):
    user_id = int(get_jwt_identity())
    goal    = Goal.query.get_or_404(goal_id)

    if goal.user_id != user_id:
        return jsonify({'error': 'Unauthorized'}), 403

    data = request.get_json()
    if 'name'        in data: goal.name        = data['name'].strip()
    if 'target'      in data: goal.target      = float(data['target'])
    if 'saved'       in data: goal.saved       = float(data['saved'])
    if 'goal_type'   in data: goal.goal_type   = data['goal_type']
    if 'target_date' in data: goal.target_date = data['target_date']

    db.session.commit()
    return jsonify({'message': 'Goal updated', 'goal': goal.to_dict()}), 200


# ── ADD TO SAVINGS (quick update) ─────────────────────────────────
@goals_bp.route('/<int:goal_id>/add-savings', methods=['PUT'])
@jwt_required()
def add_savings(goal_id):
    user_id = int(get_jwt_identity())
    goal    = Goal.query.get_or_404(goal_id)

    if goal.user_id != user_id:
        return jsonify({'error': 'Unauthorized'}), 403

    data   = request.get_json()
    amount = float(data.get('amount', 0))
    goal.saved = min(goal.saved + amount, goal.target)

    db.session.commit()
    return jsonify({'message': f'Added ₹{amount} to {goal.name}', 'goal': goal.to_dict()}), 200


# ── DELETE GOAL ───────────────────────────────────────────────────
@goals_bp.route('/<int:goal_id>', methods=['DELETE'])
@jwt_required()
def delete_goal(goal_id):
    user_id = int(get_jwt_identity())
    goal    = Goal.query.get_or_404(goal_id)

    if goal.user_id != user_id:
        return jsonify({'error': 'Unauthorized'}), 403

    db.session.delete(goal)
    db.session.commit()
    return jsonify({'message': 'Goal deleted'}), 200
