from flask import Blueprint, request, jsonify
from datetime import datetime
from sqlalchemy import and_
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

    # If FoodLog exists, just add a new FoodItem to it
    if food_log:
        # Create a new FoodItem object.
        new_food_item = FoodItem(data)

        # Set the food_log_id foreign key as the ID from the FoodLog we pulled. 
        new_food_item.food_log_id = food_log.id

        db.session.add(new_food_item)
        db.session.commit()
        print("Added new food item to the existing FoodLog: ", new_food_item)
        return jsonify({'message': 'FoodItem added to existing FoodLog successfully', 'id': new_food_item.id}), 201
        # TODO: This works for now, but there's likely a better way to handle this in the frontend. Gonna make a big update to the frontend later.
        # The frontend will pull ALL existing FoodLogs for the month right off the bat. Then when the user hits submit, it'll check if that date has a FoodLog already.
        # If it does, just do a PATCH request to add the new FoodItem. If not, create the FoodLog.
    else:
        # If not, create a new FoodLog instance and pass the entire data object in.
        # It will be initialized with a list in the food_items attribute with a single FoodItem object.
        new_food_log = FoodLog(data)
        db.session.add(new_food_log)
        db.session.commit()
        print("Added new food item:", new_food_log)
        return jsonify({'message': 'FoodLog created successfully', 'id': new_food_log.id}), 201

@food_log_bp.route('/api/foodlog/search', methods=['GET'])
def search_for_foodlogs_in_month():
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    return jsonify({'start_date': start_date, 'end_date': end_date}), 200

@food_log_bp.route('/api/foodlog/', methods=['GET'])
def get_food_items_by_date():
    date_str = request.args.get('date')
    print(f"Date in server: {date_str}")

    year = int(date_str[0:4])
    month = int(date_str[5:7])
    day = int(date_str[8:10])

    food_logs = FoodLog.query.filter(
        and_(
            FoodLog.year == year,
            FoodLog.month == month,
        )
    ).all()

    food_logs_data = [{
        'id': log.id,
        'year': log.year,
        'month': log.month,
        'day': log.day,
        'total_calories': log.total_calories,
        'total_protein': log.total_protein,
        'total_carbs': log.total_carbs,
        'total_fat': log.total_fat,
        'food_items': [{
            'id': item.id,
            'food_log_id': item.food_log_id,
            'year': item.year,
            'month': item.month,
            'day': item.day,
            'name': item.name,
            'sub_description': item.sub_description,
            'weight_value': item.weight_value,
            'weight_unit': item.weight_unit,
            'macros': {
                'id': item.macros.id,
                'calories': item.macros.calories,
                'protein': item.macros.protein,
                'carbs': item.macros.carbs,
                'fat': item.macros.fat
            } if item.macros else None
        } for item in log.food_items]
    } for log in food_logs]
    
    return jsonify(food_logs_data), 200

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