from flask import Blueprint, request, jsonify
from datetime import datetime
from Models import *

food_item_bp = Blueprint('food_item_bp', __name__)

@food_item_bp.route('/api/fooditems', methods=['POST'])
def add_food_item():
    data = request.get_json()
    print("Received data:", data)

    new_food_item = FoodItem(data)
    db.session.add(new_food_item)
    db.session.commit()
    print("Added new food item:", new_food_item)

    return jsonify({'message': 'Food item added successfully', 'id': new_food_item.id}), 201

@food_item_bp.route('/api/fooditems', methods=['GET'])
def get_food_items_by_date():
    date_str = request.args.get('date')
    print(f"Date in server: {date_str}")
    
    date_obj = datetime.strptime(date_str, '%Y-%m-%d').date()
    items = FoodItem.query.filter_by(date=date_obj).all()
    # LOOK THIS UP MORE ^
    
    if not items:
        return jsonify([])
    
    food_data = [{
        'id': item.id,
        'name': item.name,
        'sub_description': item.sub_description,
        'weight_value': item.weight_value,
        'weight_unit': item.weight_unit,
        'macros': {
            'calories': item.macros.calories,
            'protein': item.macros.protein,
            'carbs': item.macros.carbs,
            'fat': item.macros.fat
        } if item.macros else None,
        'result': item.generate_result_string(item)
    } for item in items]
    
    return jsonify(food_data)

@food_item_bp.route('/api/fooditems/<int:id>', methods=['PUT'])
def update_food_item(id):
    data = request.get_json()
    print(f"Data with update values: {data}")

    # Wrapping this in a try-except to catch any errors that might come up when querying the database.
    try:
        # Using the filter() method from SQLalchemy to grab the FoodLog object.
        item = FoodItem.query.filter(
            FoodItem.id == id
        ).first()
    except Exception as e:
        return jsonify({"DATABASE ERROR": str(e)}), 400

    print(f"Item to update in fooditems PUT: {item}")

    if item:
        try:
            # Now that the attribute names match between the front and back end, we can do this dynamically.
            # So loop through the data dictionary.
            for key in data:
                # First check if the macros object inside of the FoodItem has the key we're looking at.
                if hasattr(item.macros, key):
                    # If it does, replace the replace it's value with the value from the data object.
                    setattr(item.macros, key, data[key])
                else:
                    # If it doesn't, then replace the value in the toplevel FoodItem object instead.
                    setattr(item, key, data[key])

            db.session.commit()
            return jsonify({'message': 'FoodItem updated successfully', 'updated_item': item.to_dict()}), 200
        except Exception as e:
            return jsonify({"ERROR": str(e)}), 400
    else:
        print(f"FoodItem with ID: {id} not found")
        return jsonify({'message': 'FoodItem not found.'}), 404

@food_item_bp.route('/api/fooditems/<int:id>', methods=['PATCH'])
def update_food_item_partially(id):
    data = request.get_json()
    print(f"Data with update values: {data}")

    # Wrapping this in a try-except to catch any errors that might come up when querying the database.
    try:
        # Using the filter() method from SQLalchemy to grab the FoodLog object.
        item = FoodItem.query.filter(
            FoodItem.id == id
        ).first()
    except Exception as e:
        return jsonify({"DATABASE ERROR": str(e)}), 400

    print(f"Item to update in fooditems PUT: {item}")

    if item:
        try:
            # Now that the attribute names match between the front and back end, we can do this dynamically.
            # So loop through the data dictionary.
            for key in data:
                # First check if the macros object inside of the FoodItem has the key we're looking at.
                if hasattr(item.macros, key):
                    # If it does, replace the replace it's value with the value from the data object.
                    setattr(item.macros, key, data[key])
                else:
                    # If it doesn't, then replace the value in the toplevel FoodItem object instead.
                    setattr(item, key, data[key])

            db.session.commit()
            return jsonify({'message': 'FoodItem updated successfully', 'updated_item': item.to_dict()}), 200
        except Exception as e:
            return jsonify({"ERROR": str(e)}), 400
    else:
        print(f"FoodItem with ID: {id} not found")
        return jsonify({'message': 'FoodItem not found.'}), 404

@food_item_bp.route('/api/fooditems/<int:id>', methods=['DELETE'])
def delete_food_item(id):
    print(f"Attempting to delete FoodItem with ID: {id}")

    # Grabbing the FoodItem to delete or grabbing a 404 if it's not found.
    item = FoodItem.query.get_or_404(id)

    # Deleting!
    if item:
        db.session.delete(item)
        db.session.commit()
        print(f"Deleted FoodItem with ID: {id}")
        return jsonify({'message': 'Food item deleted successfully'})
    # Or throwing a 404.
    else:
        print(f"FoodItem with ID: {id} not found")
        return jsonify({'message': 'Food item not found'}), 404