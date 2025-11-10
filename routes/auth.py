from flask import Blueprint, request, jsonify
from app import mongo, bcrypt, jwt
from models import User
from flask_jwt_extended import create_access_token

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    users_collection = mongo.db.users

    # Check if email or username already exists
    if users_collection.find_one({"email": data["email"]}) or users_collection.find_one({"username": data["username"]}):
        return jsonify({"message": "User already exists"}), 400

    # Hash password
    hashed_password = bcrypt.generate_password_hash(data["password"]).decode('utf-8')

    # Create new user
    users_collection.insert_one({
        "username": data["username"],
        "email": data["email"],
        "firstName": "",
        "lastName": "",
        "role": "",
        "password": hashed_password
    })

    return jsonify({"message": "User registered successfully!"}), 201

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    users_collection = mongo.db.users
    
    # Find user by email
    user = users_collection.find_one({"email": data["email"]})
    if not user:
        return jsonify({"message": "Invalid credentials"}), 401

    # Check password
    if not bcrypt.check_password_hash(user["password"], data["password"]):
        return jsonify({"message": "Invalid credentials"}), 401

    # Create JWT token
    access_token = create_access_token(identity=str(user["_id"]))
    
    return jsonify({
        "message": "Login successful!", 
        "access_token": access_token, 
        "role": user["role"], 
        "email": user["email"]
    }), 200