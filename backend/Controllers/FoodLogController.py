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
    # Grabbing the date string from the query parameters.
    date = request.args.get('date')

    # Error checking to make sure a date string was passed.
    if not date:
        return jsonify({"ERROR": "Search endpoint requires a date string."}), 400

    # Indexing the year and month from the date string. This will be passed into the FoodLog query.
    year = date[0:4]
    month = date[5:7]

    print(f"Searching for FoodLogs from this month: {month}, in this year: {year}")

    # Wrapping this in a try-except to catch any errors that might come up when querying the database.
    try:
        # Using the filter() method from SQLalchemy to grab FoodLog objects with the same month and year as the date we received.
        food_logs = FoodLog.query.filter(
            and_(
                FoodLog.year == year,
                FoodLog.month == month,
            )
        ).all()
    except Exception as e:
        return jsonify({"DATABASE ERROR": str(e)}), 400

    food_logs_data = [log.to_dict() for log in food_logs]

    return jsonify(food_logs_data), 200

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

@food_log_bp.route('/api/foodlog/', methods=['PATCH'])
def add_FoodItem_to_existing_FoodLog():
    print("About to add FoodItem to existing FoodLog...")

    data = request.get_json()
    print(f"Data from frontend in PATCH call: {data}")

    # Grabbing the date from the data.
    date = data.get('date')

    # Grabbing the date fields we need to pass into the query using indexing.
    year = int(date[0:4])
    month = int(date[5:7])
    day = int(date[8:10])

    print(f"Pulling the FoodLog with this date: year - {year}, month - {month}, day - {day}")

    # Wrapping this in a try-except to catch any errors that might come up when querying the database.
    try:
        # Using the filter() method from SQLalchemy to grab the FoodLog object.
        food_logs = FoodLog.query.filter(
            and_(
                FoodLog.year == year,
                FoodLog.month == month,
                FoodLog.day == day
            )
        ).all()
    except Exception as e:
        return jsonify({"DATABASE ERROR": str(e)}), 400

    # Turning our FoodLog into a dictionary using the built-in to_dict() method to access its FoodItem array.
    FoodLogToUpdate = [log.to_dict() for log in food_logs]

    print(f"Here's the FoodLog object we're adding to: {FoodLogToUpdate}")
    print(f"ID of the log we're updating: {FoodLogToUpdate[0]["id"]}")

    # Creating the new FoodItem to be added into the FoodLog.
    new_food_item = FoodItem(data)
    # FoodItem's __init__ method will set most everything as we need from the data object, but it doesn't have access to the ID of its FoodLog.
    # To solve that, we just manually set that value here as the ID of the FoodLog we pulled from the DB.
    new_food_item.food_log_id = FoodLogToUpdate[0]["id"]

    # Adding the new FoodItem to the DB.
    db.session.add(new_food_item)
    db.session.commit()

    print("All done, new FoodItem added.")

    return jsonify({'message': 'New FoodItem successfully added to existing FoodLog'}), 201

@food_log_bp.route('/api/foodlog/<int:id>', methods=['DELETE'])
def delete_food_item(id):    
    print(f"Attempting to delete FoodItem with ID: {id}")

    # Grabbing the FoodItem to delete.
    # UPDATE: No longer using get_or_404() here. That method worked fine, but it would just immediately throw a 404 if no FoodItem was found.
    # This would ignore the logic I have below. With this, it either returns the FoodItem if there is one, or None if not. Now the logic below works.
    item = FoodItem.query.filter_by(id=id).first()
    print(f"The item pulled from the query: {item}")

    # Attempting to delete the FoodItem.
    if item:
        # Wrapping this in a try-except to catch any potential database errors.
        try:
            db.session.delete(item)
            db.session.commit()
            print(f"Deleted FoodItem with ID: {id}")
            return jsonify({'message': 'FoodItem deleted successfully.'}), 200
        # If there is an error with the DB for whatever reason, we return it and a 400 response.
        except Exception as e:
            return jsonify({"DATABASE ERROR": str(e)}), 400
    # If no FoodItem was found in the DB with that ID, return a 404 and a message explaining that.
    else:
        print(f"FoodItem with ID: {id} not found")
        return jsonify({'message': 'FoodItem not found.'}), 404

# Defining a separate DELETE route with no ID purely for error checking.
# If an empty string is passed, Flask interprets that as '/api/foodlog/', which does not fit the above route and hence the initial error isn't thrown.
# So we define this route and if ANY request comes here, it's immediately refused with the appropriate error response.
@food_log_bp.route('/api/foodlog/', methods=['DELETE'])
def delete_food_item_no_id():
    return jsonify({"ERROR": "DELETE endpoint requires a FoodItem ID."}), 400