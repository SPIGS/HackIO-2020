import os
import psycopg2

DATABASE_URL = os.environ['DATABASE_URL']

conn = psycopg2.connect(DATABASE_URL, sslmode='require')

cur = conn.cursor()

cur.execute("CREATE TABLE userdata (email text PRIMARY KEY NOT NULL, password text NOT NULL, firstName text NOT NULL, lastName text NOT NULL, userID int NOT NULL)")

cur.execute("")
