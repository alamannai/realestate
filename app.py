from flask import Flask, request, jsonify
from flask_pymongo import PyMongo
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from flask_cors import CORS

from dotenv import load_dotenv
import os


# Load environment variables from .env
load_dotenv() 

app = Flask(__name__)
CORS(app, origins="http://localhost:8080") 

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
        "role": "",
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
    
    return jsonify({"message": "Login successful!", "access_token": access_token, "role": user["role"], "email": user["email"]}), 200

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
    
    
@app.route('/profile/<email>', methods=['GET'])
def get_profile(email):
    user = users_collection.find_one({"email": email})
    if not user:
        return jsonify({'error': 'User not found'}), 404

    return jsonify({
        "username": user.get("username"),
        "email": user.get("email"),
        "firstName": user.get("firstName"),
        "lastName": user.get("lastName"),
        "bio": user.get("bio")
    })

@app.route('/profile/<email>', methods=['POST'])
def update_profile(email):
    data = request.get_json()
    update_data = {
        "username": data.get("username"),
        "firstName": data.get("firstName"),
        "lastName": data.get("lastName"),
        "bio": data.get("bio")
    }
    
    print("Update data:", update_data)  # <-- Add this

    result = users_collection.update_one({"email": email}, {"$set": update_data})
    if result.matched_count == 0:
        return jsonify({"error": "User not found"}), 404

    updated_user = users_collection.find_one({"email": email})
    return jsonify({
        "message": "Profile updated",
        "user": {
            "username": updated_user.get("username"),
            "email": updated_user.get("email"),
            "firstName": updated_user.get("firstName"),
            "lastName": updated_user.get("lastName"),
            "bio": updated_user.get("bio")
        }
    }), 200


if __name__ == '__main__':
    app.run(debug=True)
