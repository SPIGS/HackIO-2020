from flask import Flask, render_template, request, make_response, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import text
import os, hashlib, uuid

app = Flask(__name__)
domain = '127.0.0.1'
#domain = None
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# app.config['SQLALCHEMY_DATABASE_URI'] = os.environ["DATABASE_URL"]
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:postgres@localhost:5432/postgres'
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
    return render_template(r"new-user.html",mismatch=False)

@app.route('/customer-login/')
def get_login_page():
    return render_template(r"customer-login.html")

@app.route('/home/')
def get_home_page():
    login_cookie = request.cookies.get('UserLogin')

    if login_cookie is not None:
        id_from_cookie, email_from_cookie = login_cookie.split(':')
        user_data = User.query.filter_by(email=email_from_cookie).first()
        id_from_db = user_data.id

        if str(id_from_db) == str(id_from_cookie):
            res = make_response(render_template(r'home.html'))
            return res
        else:
            res = make_response(redirect('/customer-login/'))
            return res
    else:
        # there is no userlogin cookie so they can't access this page
        res = make_response(redirect('/customer-login/'))
        return res

@app.route('/order/')
def get_order_page():
    return render_template(r"order.html")

@app.route('/login/', methods=['POST'])
def handle_login():
    user_email = request.form['email']
    password_form = request.form['password']
    user_auth = User_Auth.query.filter_by(email=user_email).first()
    is_correct_password = check_password(user_auth.hashed_password, password_form)
    
    if is_correct_password:
        user_data = User.query.filter_by(email=user_email).first()
        user_id = user_data.id

        res = make_response(redirect('/home/'))
        res.set_cookie('UserLogin', str(user_id) + ':' +
                       str(user_email), domain=domain, secure=True)
        return res
    else:
        return render_template(r"customer-login.html",invalid=True)

@app.route('/sign-up/', methods=['POST'])
def handle_sign_up():
    if request.form['password'] == request.form['confirmation']:
        user_email = request.form['email']
        
        users_in_db = User.query.filter_by(email=user_email).first()

        # dont allow duplicate user emails
        if users_in_db is not None:
            return render_template(r"new-user.html", mismatch=True)

        user = User(email=user_email, organizer=False, admin=False, address=request.form['address'], state=request.form['state'], zip_code=request.form['ZIP'])
        user_auth = User_Auth(email=request.form['email'], hashed_password=get_hashed_password(request.form['password']))
        db.session.add(user)
        db.session.add(user_auth)
        db.session.commit()
        
        user_id = User.query.filter_by(email=user_email).first()

        res = make_response(redirect('/home/'))
        res.set_cookie('UserLogin', str(user_id.id) + ':' + str(user_email), domain=domain, secure=True)
        return res
    else:
        return render_template(r"new-user.html",mismatch=True)

@app.route('/user/<email>/')
def get_user(email):
    user = User.query.filter_by(email=email).first()
    login = request.cookies.get('UserLogin')
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
