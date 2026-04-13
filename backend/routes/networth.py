from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from database import db
from models import User
from datetime import datetime

networth_bp = Blueprint('networth', __name__)


# We store net worth as a JSON snapshot in a simple model
# Using a quick approach: store in a new table via raw SQL or reuse existing pattern

from database import db

class NetWorthEntry(db.Model):
    __tablename__ = 'networth_entries'
    id         = db.Column(db.Integer, primary_key=True)
    user_id    = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    category   = db.Column(db.String(100), nullable=False)  # e.g. 'Bank Savings'
    entry_type = db.Column(db.String(10), nullable=False)   # 'asset' or 'liability'
    amount     = db.Column(db.Float, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            'id':         self.id,
            'category':   self.category,
            'entry_type': self.entry_type,
            'amount':     self.amount,
        }


# ── GET NET WORTH ─────────────────────────────────────────────────
@networth_bp.route('/', methods=['GET'])
@jwt_required()
def get_networth():
    user_id    = int(get_jwt_identity())
    entries    = NetWorthEntry.query.filter_by(user_id=user_id).all()
    assets     = [e for e in entries if e.entry_type == 'asset']
    liabilities = [e for e in entries if e.entry_type == 'liability']
    total_assets      = sum(e.amount for e in assets)
    total_liabilities = sum(e.amount for e in liabilities)
    net_worth         = total_assets - total_liabilities

    return jsonify({
        'entries':           [e.to_dict() for e in entries],
        'assets':            [e.to_dict() for e in assets],
        'liabilities':       [e.to_dict() for e in liabilities],
        'total_assets':      total_assets,
        'total_liabilities': total_liabilities,
        'net_worth':         net_worth,
    }), 200


# ── ADD ENTRY ─────────────────────────────────────────────────────
@networth_bp.route('/', methods=['POST'])
@jwt_required()
def add_entry():
    user_id = int(get_jwt_identity())
    data    = request.get_json()

    if not data.get('category') or not data.get('entry_type'):
        return jsonify({'error': 'Category and entry_type are required'}), 400

    if data['entry_type'] not in ['asset', 'liability']:
        return jsonify({'error': 'entry_type must be asset or liability'}), 400

    entry = NetWorthEntry(
        user_id    = user_id,
        category   = data['category'].strip(),
        entry_type = data['entry_type'],
        amount     = float(data.get('amount', 0)),
    )
    db.session.add(entry)
    db.session.commit()
    return jsonify({'message': 'Entry added', 'entry': entry.to_dict()}), 201


# ── UPDATE ENTRY ──────────────────────────────────────────────────
@networth_bp.route('/<int:entry_id>', methods=['PUT'])
@jwt_required()
def update_entry(entry_id):
    user_id = int(get_jwt_identity())
    entry   = NetWorthEntry.query.get_or_404(entry_id)
    if entry.user_id != user_id:
        return jsonify({'error': 'Unauthorized'}), 403
    data = request.get_json()
    if 'amount'   in data: entry.amount   = float(data['amount'])
    if 'category' in data: entry.category = data['category'].strip()
    db.session.commit()
    return jsonify({'message': 'Entry updated', 'entry': entry.to_dict()}), 200


# ── DELETE ENTRY ──────────────────────────────────────────────────
@networth_bp.route('/<int:entry_id>', methods=['DELETE'])
@jwt_required()
def delete_entry(entry_id):
    user_id = int(get_jwt_identity())
    entry   = NetWorthEntry.query.get_or_404(entry_id)
    if entry.user_id != user_id:
        return jsonify({'error': 'Unauthorized'}), 403
    db.session.delete(entry)
    db.session.commit()
    return jsonify({'message': 'Entry deleted'}), 200
