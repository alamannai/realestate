# routes/messages.py
from flask import Blueprint, request, jsonify
from app import mongo  # Import MongoDB connection
from datetime import datetime, timezone  

messages_bp = Blueprint('messages', __name__, url_prefix='/api/messages')

@messages_bp.route('/', methods=['POST'])
def send_message():
    data = request.get_json()
    
    # Insert message into MongoDB
    message = {
        "sender": data.get("sender"),
        "receiver": data.get("receiver"),
        "text": data.get("text"),
        "timestamp": datetime.now(timezone.utc)
    }
    
    mongo.db.messages.insert_one(message)
    return jsonify({"status": "Message sent!"}), 201

@messages_bp.route('/<receiver_id>', methods=['GET'])
def get_messages(receiver_id):
    messages = list(mongo.db.messages.find({"receiver": receiver_id}))
    
    # Convert ObjectId to string for JSON serialization
    for msg in messages:
        msg["_id"] = str(msg["_id"])
    
    return jsonify(messages), 200