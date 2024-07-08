from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from .models import db, User

auth = Blueprint('auth', __name__)

@auth.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    hashed_password = generate_password_hash(data['password'], method='sha256')
    new_user = User(username=data['username'], password=hashed_password, monday_api_token=data['monday_api_token'])
    db.session.add(new_user)
    db.session.commit()
    return jsonify({'message': 'registered successfully'}), 201

@auth.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    user = User.query.filter_by(username=data['username']).first()
    if not user or not check_password_hash(user.password, data['password']):
        return jsonify({'message': 'Invalid credentials'}), 401
    access_token = create_access_token(identity={'username': user.username, 'monday_api_token': user.monday_api_token})
    return jsonify({'access_token': access_token}), 200

@auth.route('/check', methods=['GET'])
@jwt_required()
def check():
    current_user = get_jwt_identity()
    return jsonify(logged_in_as=current_user), 200
