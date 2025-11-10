from flask import Blueprint, request, jsonify
from extensions import mongo
from flask_jwt_extended import jwt_required, get_jwt_identity
from bson import ObjectId

profile_bp = Blueprint('profile', __name__)

# === GET user profile by email (query param) ===
@profile_bp.route('/users', methods=['GET'])
@jwt_required()
def get_profile():
    """Get user profile info by email (query parameter)"""
    try:
        
        user_id = get_jwt_identity()

        users_collection = mongo.db.users
        user = users_collection.find_one({"_id": ObjectId(user_id)})
        if not user:
            return jsonify({"error": "User not found"}), 404

        response_data = {
            "username": user.get("username", ""),
            "email": user.get("email", ""),
            "firstName": user.get("firstName", ""),
            "lastName": user.get("lastName", ""),
            "bio": user.get("bio", "")
        }
        return jsonify(response_data), 200

    except Exception as e:
        return jsonify({"err": str(e)}), 500

"""
# === POST update profile for logged-in user ===
@profile_bp.route('/profile12', methods=['POST'])
@jwt_required()
def update_profile():
    try:
        user_id = get_jwt_identity()

        # Validate user_id is a valid ObjectId
        if not ObjectId.is_valid(user_id):
            return jsonify({"error": "Invalid user ID"}), 400

        data = request.get_json()
        if not data:
            return jsonify({"error": "No data provided"}), 400

        # Build the update dict, excluding None values
        update_data = {
            k: v for k, v in {
                "username": data.get("username"),
                "firstName": data.get("firstName"),
                "lastName": data.get("lastName"),
                "bio": data.get("bio")
            }.items() if v is not None
        }

        if not update_data:
            return jsonify({"error": "No valid fields to update"}), 400

        result = mongo.db.users.update_one(
            {"_id": ObjectId(user_id)},
            {"$set": update_data}
        )

        if result.matched_count == 0:
            return jsonify({"error": "User not found"}), 404

        # Fetch updated user data
        updated_user = mongo.db.users.find_one({"_id": ObjectId(user_id)})

        return jsonify({
            "message": "Profile updated successfully",
            "user": {
                "username": updated_user.get("username", ""),
                "email": updated_user.get("email", ""),
                "firstName": updated_user.get("firstName", ""),
                "lastName": updated_user.get("lastName", ""),
                "bio": updated_user.get("bio", "")
            }
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

"""


@profile_bp.route('/debug')
def debug_route():
    test_id = "688df56813f7841525f104ff"  # Replace with real ID
    
    users_collection = mongo.db.users
    user = users_collection.find_one({"_id": ObjectId(test_id)})
    return user