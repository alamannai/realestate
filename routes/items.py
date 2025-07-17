# routes/items.py
from flask import Blueprint, request, jsonify
from models import ItemCreate, ItemType
from app import mongo
from bson import ObjectId

items_bp = Blueprint('items', __name__, url_prefix='/api/items')

def validate_objectid(id_str: str):
    try:
        return ObjectId(id_str)
    except:
        raise ValueError("Invalid ID format")

@items_bp.route('/', methods=['POST'])
def create_item():
    try:
        item = ItemCreate.model_validate(request.get_json())
        result = mongo.db.items.insert_one(item.model_dump())
        return jsonify({
            "message": "Item created",
            "id": str(result.inserted_id)
        }), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@items_bp.route('/<item_type>', methods=['GET'])
def get_items(item_type: str):
    try:
        ItemType(item_type)  # Validate enum
        items = list(mongo.db.items.find({"type": item_type}))
        return jsonify([{
            **item, 
            "_id": str(item["_id"])
        } for item in items]), 200
    except ValueError as e:
        return jsonify({
            "error": f"Invalid type. Must be one of: {list(ItemType)}"
        }), 400