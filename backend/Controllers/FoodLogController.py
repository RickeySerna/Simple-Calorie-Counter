from flask import Blueprint, request, jsonify
from datetime import datetime
from Models import *

food_log_bp = Blueprint('food_log_bp', __name__)

@food_log_bp.route('/api/foodlog', methods=['POST'])
def add_food_item():
    print("WE ARE IN THE FOODLOG POST ROUTE")
    data = request.get_json()
    print("Received data:", data)

    # Define the year, month, and day from the date attribute in the data object.
    # TODO: Would probably be better to just do this in the frontend and include it in the data object. Will do that later.
    year = int(data.get("date")[0:4])
    month = int(data.get("date")[5:7])
    day = int(data.get("date")[8:10])

    # Now use the above vars to query the database to see if this log already exists.
    food_log = FoodLog.query.filter_by(year=year, month=month, day=day).first()
    # TODO: If the FoodLog already exists, just add a new FoodItem. Need to add that logic. Should be a PUT or PATCH instead of a POST.
    if food_log:
        return

    # If not, create a new FoodLog instance and pass the entire data object in.
    # It will be initialized with a list in the food_items attribute with a single FoodItem object.
    new_food_log = FoodLog(data)
    db.session.add(new_food_log)
    db.session.commit()
    print("Added new food item:", new_food_log)

    return jsonify({'message': 'Food log added successfully', 'id': new_food_log.id}), 201

@food_log_bp.route('/api/foodlog', methods=['GET'])
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

@food_log_bp.route('/api/foodlog/<int:id>', methods=['PUT'])
def update_food_item(id):
    data = request.get_json()
    item = FoodItem.query.get_or_404(id)
    print(f"Data with update values: {data}")
    print(f"Item to update: {item}")

    item.name = data['name']
    item.sub_description = data['sub_description']
    item.weight_value = data['weight']
    item.weight_unit = data['weightUnit']
    item.macros.calories = data['calories']
    item.macros.protein = data['protein']
    item.macros.carbs = data['carbs']
    item.macros.fat = data['fat']

    db.session.commit()
    return jsonify({'message': 'Food item updated successfully'})

@food_log_bp.route('/api/foodlog/<int:id>', methods=['PATCH'])
def update_food_item_partially(id):
    data = request.get_json()
    item = FoodItem.query.get_or_404(id)
    print(f"Data with update values: {data}")
    print(f"Item to update: {item}")

    if 'name' in data:
        item.name = data['name']
    if 'sub_description' in data:
        item.sub_description = data['sub_description']
    if 'weight' in data:
        item.weight_value = data['weight']
    if 'weightUnit' in data:
        item.weight_unit = data['weightUnit']
    if 'calories' in data:
        item.macros.calories = data['calories']
    if 'protein' in data:
        item.macros.protein = data['protein']
    if 'carbs' in data:
        item.macros.carbs = data['carbs']
    if 'fat' in data:
        item.macros.fat = data['fat']
    
    db.session.commit()
    return jsonify({'message': 'Food item partially updated successfully'})

@food_log_bp.route('/api/foodlog/<int:id>', methods=['DELETE'])
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