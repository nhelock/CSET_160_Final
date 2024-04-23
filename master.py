from flask import Flask, render_template, request, redirect, url_for, session
from flask_mysqldb import MySQL
import MySQLdb.cursors
import MySQLdb.cursors, re, hashlib
from sqlalchemy import Column, Integer, String, Numeric, create_engine, text

app = Flask(__name__)
conn_str = "mysql://root:FunnyPassword321@localhost/160_final"
engine = create_engine(conn_str, echo=True)
conn = engine.connect()


@app.route('/')
def login():
    return render_template('login.html')

@app.route('/signup')
def signup():
    return render_template('signup.html')

@app.route('/accounts')
def accounts():
    users = conn.execute(text(f"SELECT * FROM users")).all()
    return render_template('accounts.html', users=users)

@app.route('/tests')
def testslist():
    tests = conn.execute(text(f"SELECT * FROM tests")).all()
    return render_template('testslist.html', tests=tests)


if __name__ == '__main__':
    app.run(debug=True)
