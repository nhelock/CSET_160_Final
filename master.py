from flask import Flask, render_template, request
from sqlalchemy import Column, Integer, String, Numeric, create_engine, text

app = Flask(__name__)
conn_str = "mysql://root:MarioMovie8!@localhost/cset_160_final"
engine = create_engine(conn_str, echo=True)
conn = engine.connect()


@app.route('/')
def base():
    return render_template('login.html')


@app.route('/login')
def login():
    return render_template('login.html')


@app.route('/login', methods = [ "POST" ])
def login_route():
    return render_template('index.html')


@app.route('/signup')
def signup():
    return render_template('signup.html')


@app.route('/signup', methods = [ "POST" ])
def signup_button_route():
    return render_template('index.html')


@app.route('/signup', methods = [ "POST" ])
def signup_route():
    return render_template('index.html')


@app.route('/test_results')
def test_results():
    result = conn.execute(text("SELECT UserID, TestID, Grade FROM Grade")).fetchall()
    return render_template('test_results.html', grade=result)


@app.route('/test_responses')
def test_responses():
    students = conn.execute(text("SELECT CONCAT(FirstName, ' ', LastName) AS Name FROM users WHERE UserType = 'Student'")).fetchall()
    return render_template('test_responses.html', students=students)


@app.route('/test_responses', methods = [ "POST" ])
def test_responses_submit_route():
    result = conn.execute(text("SELECT UserID, TestID, Grade FROM Grade")).fetchall()
    return render_template('test_results.html', grade=result)


@app.route('/test_info')
def test_info():
    info = conn.execute(text("SELECT FirstName, LastName, UserType FROM users")).fetchall()
    return render_template('test_info.html', users=info)


@app.route('/test_details')
def test_details():
    details = conn.execute(text("SELECT FirstName, LastName, UserID, UserType FROM users where UserType = 'Student'")).fetchall()
    return render_template('test_details.html', users=details)


@app.route('/test_details', methods = [ "POST" ])
def test_details_student_route():
    students = conn.execute(text("SELECT CONCAT(FirstName, ' ', LastName) AS Name FROM users WHERE UserType = 'Student'")).fetchall()
    return render_template('test_responses.html', students=students)


@app.route('/test_list')
def test_list():
    students = conn.execute(text("SELECT CONCAT(FirstName, ' ', LastName) AS Name FROM users WHERE UserType = 'Student'")).fetchall()
    return render_template('test_list.html', students=students)


if __name__ == '__main__':
    app.run(debug=True)
