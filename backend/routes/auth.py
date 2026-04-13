from flask import Blueprint, request, jsonify
from flask_jwt_extended import (
    create_access_token, create_refresh_token,
    jwt_required, get_jwt_identity
)
from database import db
from models import User

auth_bp = Blueprint('auth', __name__)


# ── REGISTER ──────────────────────────────────────────────────────
@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()

    # Validate required fields
    required = ['name', 'email', 'password']
    for field in required:
        if not data.get(field):
            return jsonify({'error': f'{field} is required'}), 400

    name      = data['name'].strip()
    email     = data['email'].strip().lower()
    password  = data['password']
    city_type = data.get('city_type', 'metro')

    if len(password) < 6:
        return jsonify({'error': 'Password must be at least 6 characters'}), 400

    # Check duplicate email
    if User.query.filter_by(email=email).first():
        return jsonify({'error': 'An account with this email already exists'}), 409

    # Create user
    user = User(name=name, email=email, city_type=city_type)
    user.set_password(password)

    db.session.add(user)
    db.session.commit()

    access_token  = create_access_token(identity=str(user.id))
    refresh_token = create_refresh_token(identity=str(user.id))

    return jsonify({
        'message':       'Account created successfully! Welcome to FinTech.',
        'user':          user.to_dict(),
        'access_token':  access_token,
        'refresh_token': refresh_token,
    }), 201


# ── LOGIN ─────────────────────────────────────────────────────────
@auth_bp.route('/login', methods=['POST'])
def login():
    data  = request.get_json()
    email = data.get('email', '').strip().lower()
    password = data.get('password', '')

    if not email or not password:
        return jsonify({'error': 'Email and password are required'}), 400

    user = User.query.filter_by(email=email).first()

    if not user or not user.check_password(password):
        return jsonify({'error': 'Invalid email or password'}), 401

    access_token  = create_access_token(identity=str(user.id))
    refresh_token = create_refresh_token(identity=str(user.id))

    return jsonify({
        'message':       f'Welcome back, {user.name}!',
        'user':          user.to_dict(),
        'access_token':  access_token,
        'refresh_token': refresh_token,
    }), 200


# ── REFRESH TOKEN ─────────────────────────────────────────────────
@auth_bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    user_id      = get_jwt_identity()
    access_token = create_access_token(identity=user_id)
    return jsonify({'access_token': access_token}), 200


# ── GET PROFILE ───────────────────────────────────────────────────
@auth_bp.route('/profile', methods=['GET'])
@jwt_required()
def get_profile():
    user_id = int(get_jwt_identity())
    user    = User.query.get_or_404(user_id)
    return jsonify({'user': user.to_dict()}), 200


# ── UPDATE PROFILE ────────────────────────────────────────────────
@auth_bp.route('/profile', methods=['PUT'])
@jwt_required()
def update_profile():
    user_id = int(get_jwt_identity())
    user    = User.query.get_or_404(user_id)
    data    = request.get_json()

    if 'name'      in data: user.name      = data['name'].strip()
    if 'city_type' in data: user.city_type = data['city_type']

    # Password change
    if data.get('new_password'):
        if not data.get('current_password'):
            return jsonify({'error': 'Current password is required to set new password'}), 400
        if not user.check_password(data['current_password']):
            return jsonify({'error': 'Current password is incorrect'}), 401
        if len(data['new_password']) < 6:
            return jsonify({'error': 'New password must be at least 6 characters'}), 400
        user.set_password(data['new_password'])

    db.session.commit()
    return jsonify({'message': 'Profile updated successfully', 'user': user.to_dict()}), 200
