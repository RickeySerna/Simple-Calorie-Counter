from flask import Blueprint, request, jsonify
from datetime import datetime
from calendar import monthrange
from sqlalchemy import and_, update
from sqlalchemy.orm import sessionmaker
from Models import *
import math

food_log_bp = Blueprint('food_log_bp', __name__)

@food_log_bp.route('/api/foodlog', methods=['POST'])
def add_food_item():
    print("WE ARE IN THE FOODLOG POST ROUTE")
    data = request.get_json()
    print("Received data:", data)

    # UPDATE: Because this is the POST route, we know we're creating an entirely new FoodLog. With that, no need to search for anything anymore.
    # Just create the new FoodLog object with the data we got from the frontend and commit it to the DB. Done.
    new_food_log = FoodLog(data)
    db.session.add(new_food_log)
    db.session.commit()
    print("Added new food item:", new_food_log)
    return jsonify({'message': 'FoodLog created successfully', 'id': new_food_log.id, 'new_food_log': new_food_log.to_dict()}), 201

@food_log_bp.route('/api/foodlog/search', methods=['GET'])
def search_for_foodlogs_in_month():
    # Grabbing the date string from the query parameters.
    date = request.args.get('date')
    print(f"The date string passed to the /search endpoint: {date}")
    print(f"The type of the date string passed to the /search endpoint: {type(date)}")

    # Error checking to make sure a date string was passed.
    if not date:
        return jsonify({"ERROR": "Search endpoint requires a date string."}), 400

    # Indexing the year and month from the date string. This will be passed into the FoodLog query.
    year = int(date[0:4])
    month = int(date[5:7])

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

    # Using calendar and the date strings we created to get the number of days in the month the user searched in.
    daysInTheMonth = monthrange(year, month)[1]
    
    # Create an initial dictionary with keys set to "day" and values set to None.
    food_logs_data = {day: None for day in range(1, daysInTheMonth + 1)}

    # Now replace the Nones in the dictionary with FoodLog objects where they exist - still ordered by day.
    for log in food_logs:
        food_logs_data[log.day] = log.to_dict()

    print(f"food_logs_data being returned to the frontend: {food_logs_data}")

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
def update_foodlog(id):
    print("About to replace an existing FoodLog...")

    data = request.get_json()
    print(f"Data from frontend in PUT call: {data}")

    try:
        food_log = FoodLog.query.filter_by(id=id).first()
        if not food_log:
            return jsonify({"ERROR": "FoodLog not found"}), 404
    except Exception as e:
        return jsonify({"DATABASE ERROR": str(e)}), 400

    print(f"The FoodLog pulled from SQLalchemy with the id: {food_log}")

    db.session.delete(food_log)

    updatedFoodLog = FoodLog(data["foodLog"])
    updatedFoodLog.id = id

    db.session.add(updatedFoodLog)
    db.session.commit()

    print("All done, FoodLog replaced.")

    return jsonify({'message': 'FoodLog successfully updated', 'updated_food_log': updatedFoodLog.to_dict()}), 201

# Removing the int constraint here to allow for better error handling.
@food_log_bp.route('/api/foodlog/<id>', methods=['DELETE'])
def delete_food_item(id):    
    print(f"Attempting to delete FoodItem with ID: {id}")

    # The endpoint will not take ANY input passed in the URL.
    # To make sure that value passed is an int, we try casting it to an int.
    try:
        id = int(id)
    # If that fails, which it will for anything but an integer, this is raised and the request just returns a 400 error.
    except ValueError:
        return jsonify({"ERROR": "ID passed is not a valid FoodItem ID."}), 400

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