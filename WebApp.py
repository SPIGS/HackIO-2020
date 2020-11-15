from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import text
import os, hashlib, uuid

app = Flask(__name__)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
#app.config['SQLALCHEMY_DATABASE_URI'] = os.environ["DATABASE_URL"]
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:postgres@localhost:5433/postgres'
db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(50))
    organizer = db.Column(db.Boolean)
    admin = db.Column(db.Boolean)
    address = db.Column(db.String(100))
    state = db.Column(db.String(50))
    zip_code = db.Column(db.Integer)

class User_Auth(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(50))
    hashed_password = db.Column(db.String(200)) #NOTE: THIS IS NOT SECURE!!!! THIS IS ONLY INTENDED FOR PROTOTYPING SINCE THIS IS A HACKATHON!!!!

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

@app.route('/sign-up/', methods=['POST'])
def handle_sign_up():
    user = User(email=request.form['email'], organizer=False, admin=False, address=request.form['address'], state=request.form['state'], zip_code=request.form['ZIP'])
    user_auth = User_Auth(email=request.form['email'], hashed_password=get_hashed_password(request.form['password']));
    db.session.add(user)
    db.session.add(user_auth)
    db.session.commit()

    return 'You login in!'

@app.route('/user/<email>/')
def get_user(email):
    user = User.query.filter_by(email=email).first()

    return f'<ul><li>Email: { user.email }</li></ul>'

@app.errorhandler(505)
def internal_error(error):
    return "500 error"

@app.errorhandler(404)
def not_found(error):
    return "404 error", 404

'''Get's hashed password'''
def get_hashed_password(password):
    salt = uuid.uuid4().hex
    return hashlib.sha256(salt.encode() + password.encode()).hexdigest() + ':' + salt

'''Returns true if the provided hashed_password and user_password match'''
def check_password(hashed_password, user_password):
    password, salt = hashed_password.split(':')
    return password == hashlib.sha256(salt.encode() + password.encode()).hexdigest() + ':' + salt

if __name__ == '__main__':
    app.run(port=5000, debug=True)
