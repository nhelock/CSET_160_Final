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

@app.route('/test_responses', methods=['GET', 'POST'])
def test_responses():
    if request.method == 'POST':
        usertype = request.form.get('Teacher')
        total_marks = request.form.get('total_marks')
    else:
        teachers = conn.execute(text("SELECT * FROM users")).fetchall()
        return render_template('test_responses.html', teachers=teachers)


@app.route('/test_info')
def test_info():
    test_info = conn.execute(text("SELECT FirstName, LastName, UserType FROM users")).fetchall()
    return render_template('test_info.html', users=test_info)


@app.route('/test_details')
def test_details():
    test_details = conn.execute(text("SELECT FirstName, LastName, UserType FROM users")).fetchall()
    return render_template('test_details.html', users=test_details)


if __name__ == '__main__':
    app.run(debug=True)
