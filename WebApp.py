from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import text
import os, psycopg2

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ["DATABASE_URL"]
db = SQLAlchemy(app)

@app.route('/')
def front():
    return render_template(r"src\webapp\WEB-INF\front.html")

@app.route('/SignUp')
def sign_up ():
    return 'signup'

@app.route('/Login')
def login ():
    return 'login'

@app.errorhandler(505)
def internal_error(error):
    return "500 error"

@app.errorhandler(404)
def not_found(error):
    return "404 error", 404

if __name__ == '__main__':
    app.run(port=5000, debug=True)
