import os
from flask import Flask
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from decimal import Decimal, getcontext
from Models import db
from Controllers import blueprints

# Specifying the domain (currently just localhost) we'll be receiving request from to avoid CORS issues.
# When we move to prod, this will have to be updated to whatever the domain name ends up being.
app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "http://localhost:3000"}}, supports_credentials=True)

basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'foodlogs.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True
db.init_app(app)

# This will now import all blueprints from the Controllers directory as they're added to the __init__ file.
for bp in blueprints:
    app.register_blueprint(bp)

getcontext().prec = 10

with app.app_context():
    print("Creating all tables...")
    try:
        db.create_all()
        print("Tables created.")
    except Exception as e:
        print("Error creating tables:", e)

if __name__ == '__main__':
    app.run(debug=True)