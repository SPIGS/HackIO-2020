from flask import Flask
import os, psycopg2
app = Flask(__name__)
DATABASE_URL = os.environ['DATABASE_URL']
conn = psycopg2.connect(DATABASE_URL, sslmode='require')
cur = conn.cursor()
cur.execute("CREATE TABLE IF NOT EXISTS userdata (email text PRIMARY KEY not null, password text not null, firstName text not null, lastName text not null, userId int not null)")
cur.execute("INSERT INTO userdata * VALUES ('test@email.com', '12345', 'Dio', 'Brando', 1)")
cur.execute("SELECT * FROM userdata")
message = cur.fetchone()
cur.commit()

@app.route('/')
def hello_world():
    return message

if __name__ == '__main__':
    app.run(port=5000)
