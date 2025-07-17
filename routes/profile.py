from flask import Blueprint, request, jsonify
from app import mongo
from flask_jwt_extended import jwt_required, get_jwt_identity

profile_bp = Blueprint('profile', __name__)

@profile_bp.route('/profile', methods=['GET'])
@jwt_required()
def protected_profile():
    user_id = get_jwt_identity()
    user = mongo.db.users.find_one({"_id": mongo.db.ObjectId(user_id)})

    if not user:
        return jsonify({"message": "User not found"}), 404

    return jsonify({
        "username": user["username"],
        "email": user["email"]
    }), 200
    
@profile_bp.route('/profile/<email>', methods=['GET'])
def get_profile(email):
    user = mongo.db.users.find_one({"email": email})
    if not user:
        return jsonify({'error': 'User not found'}), 404

    return jsonify({
        "username": user.get("username"),
        "email": user.get("email"),
        "firstName": user.get("firstName"),
        "lastName": user.get("lastName"),
        "bio": user.get("bio")
    })

@profile_bp.route('/profile/<email>', methods=['POST'])
def update_profile(email):
    data = request.get_json()
    update_data = {
        "username": data.get("username"),
        "firstName": data.get("firstName"),
        "lastName": data.get("lastName"),
        "bio": data.get("bio")
    }

    result = mongo.db.users.update_one({"email": email}, {"$set": update_data})
    if result.matched_count == 0:
        return jsonify({"error": "User not found"}), 404

    updated_user = mongo.db.users.find_one({"email": email})
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