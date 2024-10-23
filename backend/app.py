from flask import Flask, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route('/api/calories', methods=['GET'])
def get_calories():
    data = {
        'calories': 2000
    }
    return jsonify(data)

if __name__ == '__main__':
    app.run(debug=True)