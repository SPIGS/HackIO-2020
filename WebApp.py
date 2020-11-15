from flask import Flask, render_template, request, make_response, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import text
import os, hashlib, uuid

app = Flask(__name__)
#domain = '127.0.0.1'
domain = None
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ["DATABASE_URL"]
#app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:postgres@localhost:5432/postgres'
db = SQLAlchemy(app)
db.create_all()

class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(50))
    organizer = db.Column(db.Boolean)
    admin = db.Column(db.Boolean)
    address = db.Column(db.String(100))
    state = db.Column(db.String(50))
    zip_code = db.Column(db.Integer)

class User_Auth(db.Model):
    __tablename__ = 'user_auth'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(50))
    hashed_password = db.Column(db.String(200)) #NOTE: THIS IS NOT SECURE!!!! THIS IS ONLY INTENDED FOR PROTOTYPING SINCE THIS IS A HACKATHON!!!!

class Order (db.Model):
    __tablename__ = 'order'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer)
    zip_code = db.Column(db.Integer)
    items = db.relationship('Item', backref='order')
    paid = db.Column(db.Boolean)

class Item (db.Model):
    __tablename__ = 'item'
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('order.id'))
    name = db.Column(db.String(50))
    price = db.Column(db.Numeric(10, 2))
    qty = db.Column(db.Integer)

class ListItem:
    def __init__(self, name, stock, price):
        self.name = name
        self.stock =  stock
        self.price = str(format(price,'.2f'))

class OrderItem:
    def __init__(self, name, price, qty):
        self.name = name
        self.price = price
        self.qty = qty

items = [ListItem('Apples', 1000, 1.00),
        ListItem('Beef', 500, 3.00),
        ListItem('Cat Food',130, 5.00),
        ListItem('Deep Dish', 0, 10.00)]


@app.route('/')
def front():
    db.create_all()
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

    return render_template(r"order.html", items=items)

@app.route('/tracker/')
def get_tracker_page():
    return render_template(r"tracker.html")

@app.route('/payment/')
def get_payment_page():
    login_cookie = request.cookies.get('UserLogin')
    if login_cookie is not None:

        id_from_cookie, email_from_cookie = login_cookie.split(':')
        user_data = User.query.filter_by(email=email_from_cookie).first()
        id_from_db = user_data.id
        
        user_order_list = Order.query.filter_by(user_id=id_from_db).first()
        if user_order_list is not None:
            #display order info
            order_items = user_order_list.items
            items = []
            total = 0.00
            for item in order_items:
                items.append(OrderItem(item.name, item.price, item.qty))
                total += float(item.price) * int(item.qty)
            
            return render_template(r"payment.html", items=items, total="{:10.2f}".format(total))
        else:
            return redirect("/order/")

    else:
        return redirect("/customer-login/")

@app.route('/profile/')
def get_profile_page():
    return render_template(r"profile.html")

@app.route('/place-order/', methods=['POST'])
def place_order():
    login_cookie = request.cookies.get('UserLogin')

    if login_cookie is not None:

        id_from_cookie, email_from_cookie = login_cookie.split(':')
        user_data = User.query.filter_by(email=email_from_cookie).first()
        id_from_db = user_data.id
        zip_from_db = user_data.zip_code

        user_order_list = Order.query.filter_by(user_id=id_from_db).first()
        if user_order_list is not None:
            #append order
            try:
                qty_apples = request.form['Apples-quantity']
                user_order_list.items[0].qty += int(qty_apples)
            except:
                    print(" apples out of stock; cant append")

            try:
                qty_beef = request.form['Beef-quantity']
                user_order_list.items[1].qty += int(qty_beef)
            except:
                print(" beef out of stock; cant append")

            try:
                qty_catfd = request.form['Cat Food-quantity']
                user_order_list.items[2].qty += int(qty_catfd)
            except:
                print(" cat food out of stock; cant append")

            try:
                qty_deepdish = request.form['Deep Dish-quantity']
                user_order_list.items[3].qty += int(qty_deepdish)
            except:
                print(" deepdish out of stock; cant append")

            db.session.commit()
        else:
            #make new order
            item_list = []
            apples = None
            beef = None
            catfood = None
            deepdish = None

            try:
                qty_apples = request.form['Apples-quantity']
                apples = Item(name="Apples", qty=qty_apples, price=1.00)
                item_list.append(apples)
                db.session.add(apples)
            except:
                print(" apples out of stock")
            
            try:
                qty_beef = request.form['Beef-quantity']
                beef = Item(name="Beef", qty=qty_beef,price=3.00)
                item_list.append(beef)
                db.session.add(beef)
            except:
                print(" beef out of stock")

            try:
                qty_catfd = request.form['Cat Food-quantity']
                cat_food = Item(name="Cat Food", qty=qty_catfd, price=5.00)
                item_list.append(cat_food)
                db.session.add(cat_food)
            except:
                print(" cat food out of stock")

            try:
                qty_deepdish = request.form['Deep Dish-quantity']
                deepdish = Item(name="Deep Dish", qty=qty_deepdish, price=10.00)
                item_list.append(deepdish)
                db.session.add(deepdish)
            except:
                print(" deepdish out of stock")

            order = Order(user_id=id_from_db,
                          zip_code=zip_from_db, items=item_list, paid=False)
            db.session.add(order)
            db.session.commit()
    else:
        return redirect("/customer-login/")

    # treat list relationship as python list
    # a = Address(email='foo@bar.com')
    # p = Person(name='foo', addresses=[a])
    return redirect("/payment/")

@app.route('/login/', methods=['POST'])
def handle_login():
    user_email = request.form['email']
    password_form = request.form['password']
    user_auth = User_Auth.query.filter_by(email=user_email).first() 
    
    if user_auth != None and check_password(user_auth.hashed_password, password_form):
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
        return render_template(r"new-user.html", mismatch=True)

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
    db.delete_all()
    db.create_all()
    app.run(port=5000)
