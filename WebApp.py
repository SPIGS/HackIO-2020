from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import text
import os, psycopg2

app = Flask(__name__)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
#app.config['SQLALCHEMY_DATABASE_URI'] = os.environ["DATABASE_URL"]
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:postgres@localhost:5433/postgres'
db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(50))
    organizer_status = db.Column(db.Boolean)
    admin_status = db.Column(db.Boolean)
    address = db.Column(db.String(100))
    city = db.Column(db.String(50))
    zip_code = db.Column(db.Integer)

class User_Auth(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(50))
    hashed_password = db.Column(db.Integer) #NOTE: THIS IS NOT SECURE!!!! THIS IS ONLY INTENDED FOR PROTOTYPING SINCE THIS IS A HACKATHON!!!!

@app.route('/')
def front():
    return render_template(r"front.html")

@app.route('/new-user/')
def sign_up():
    return render_template(r"new-user.html")

@app.route('/customer-login/')
def get_login_page():
    return render_template(r"customer-login.html")

@app.route('/login/', methods=['POST'])
def handle_login():
    return request.form

@app.errorhandler(505)
def internal_error(error):
    return "500 error"

@app.errorhandler(404)
def not_found(error):
    return "404 error", 404

if __name__ == '__main__':
    app.run(port=5000, debug=True)
