from flask import Flask, render_template, request, make_response
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import text
import os, hashlib, uuid

app = Flask(__name__)
domain = '127.0.0.1'
#domain = None
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ["DATABASE_URL"]
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

@app.route('/home/')
def get_home_page():
    return render_template(r"home.html")

@app.route('/login/', methods=['POST'])
def handle_login():
    user_email = request.form['email']
    password_form = request.form['password']
    user_auth = User_Auth.query.filter_by(email=user_email).first()
    is_correct_password = check_password(user_auth.hashed_password, password_form)
    if is_correct_password:
        res = make_response('Correct password login should happen')
        return res
    else:
        res = make_response('Incorrect password')
        return res

@app.route('/sign-up/', methods=['POST'])
def handle_sign_up():
    #write user info to database
    user_email = request.form['email']
    user = User(email=user_email, organizer=False, admin=False, address=request.form['address'], state=request.form['state'], zip_code=request.form['ZIP'])
    user_auth = User_Auth(email=request.form['email'], hashed_password=get_hashed_password(request.form['password']));
    db.session.add(user)
    db.session.add(user_auth)
    db.session.commit()

    #set login cookie
    user_query = User.query.filter_by(email=user_email).first()
    response = make_response(f'You login in!')
    response.set_cookie('Login', str(user_query.id) + ':' +
                        str(user_email), domain=domain, secure=True,)

    return response

@app.route('/user/<email>/')
def get_user(email):
    user = User.query.filter_by(email=email).first()
    login = request.cookies.get('Login')
    return f'<ul><li>Email: { login }</li></ul>'

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
    return password + ':' + salt == hashlib.sha256(salt.encode() + user_password.encode()).hexdigest() + ':' + salt

if __name__ == '__main__':
    app.run(port=5000, debug=True)
