from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from werkzeug.security import generate_password_hash, check_password_hash

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.json

    fullName = data.get('fullName')
    email = data.get('email')
    password = data.get('password')

    if not fullName or not email or not password:
        return jsonify({ "error": "Name, Email, password are required" }), 400
    
    existing_user = current_app.mongo.db.users.find_one({ 'email': email })
    if existing_user:
        return jsonify({ "error": "User already exists" }), 400
    
    hashed_pwd = generate_password_hash(password)
    current_app.mongo.db.users.insert_one({
        "fullName": fullName,
        "email": email,
        "password": hashed_pwd
    })

    access_token = create_access_token(identity=email)

    return jsonify({ 
        'message': 'User created successfully',
        'access-token': access_token
    }), 201

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.json

    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return jsonify({ "error": "Email and password are required" }), 400
    
    user = current_app.mongo.db.users.find_one({ 'email': email })
    if not user or not check_password_hash(user['password'], password):
        return jsonify({ "error": "Invalid credentials" }), 401
    
    access_token = create_access_token(identity=email)

    return jsonify({
        "access_token": access_token
    }), 200
    
@auth_bp.route('/profile', methods=['GET'])
@jwt_required()
def profile():
    current_user = get_jwt_identity()
    user = current_app.mongo.db.users.find_one({ 'email': current_user }, { 'password': 0 })
    return jsonify({
        'message': "success",
        'user': user
    }), 200

