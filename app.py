from flask import Flask, request, jsonify
from flask_pymongo import PyMongo
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity

from dotenv import load_dotenv
import os


# Load environment variables from .env
load_dotenv() 

app = Flask(__name__)

# MongoDB Atlas connection (replace with your actual connection string)
app.config["MONGO_URI"] = os.getenv("MONGO_URI")

# Secret key for JWT
app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY")

# Initialize extensions
mongo = PyMongo(app)
bcrypt = Bcrypt(app)
jwt = JWTManager(app)

# Collection for storing users
users_collection = mongo.db.users

### USER REGISTRATION ###
@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()

    # Check if email or username already exists
    if users_collection.find_one({"email": data["email"]}) or users_collection.find_one({"username": data["username"]}):
        return jsonify({"message": "User already exists"}), 400

    # Hash password
    hashed_password = bcrypt.generate_password_hash(data["password"]).decode('utf-8')

    # Create new user
    users_collection.insert_one({
        "username": data["username"],
        "email": data["email"],
        "password": hashed_password
    })

    return jsonify({"message": "User registered successfully!"}), 201

### USER LOGIN ###
@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    
    # Find user by email
    user = users_collection.find_one({"email": data["email"]})
    if not user:
        return jsonify({"message": "Invalid credentials"}), 401

    # Check password
    if not bcrypt.check_password_hash(user["password"], data["password"]):
        return jsonify({"message": "Invalid credentials"}), 401

    # Create JWT token
    access_token = create_access_token(identity=str(user["_id"]))
    
    return jsonify({"message": "Login successful!", "access_token": access_token}), 200

### PROTECTED ROUTE (REQUIRES LOGIN) ###
@app.route('/profile', methods=['GET'])
@jwt_required()
def profile():
    user_id = get_jwt_identity()
    user = users_collection.find_one({"_id": mongo.db.ObjectId(user_id)})

    if not user:
        return jsonify({"message": "User not found"}), 404

    return jsonify({
        "username": user["username"],
        "email": user["email"]
    }), 200

if __name__ == '__main__':
    app.run(debug=True)
