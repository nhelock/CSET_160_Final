# from flask import Flask, render_template, request
# from sqlalchemy import Column, Integer, String, Numeric, create_engine, text

# app = Flask(__name__)
# conn_str = "mysql://root:FunnyPassword321@localhost/160_final"
# engine = create_engine(conn_str, echo=True)
# conn = engine.connect()


# @app.route('/')
# def base():
#     return render_template('login.html')


# @app.route('/login')
# def login():
#     return render_template('login.html')


# @app.route('/login', methods = [ "POST" ])
# def login_route():
#     return render_template('index.html')


# @app.route('/signup')
# def signup():
#     return render_template('signup.html')


# @app.route('/signup', methods = [ "POST" ])
# def signup_button_route():
#     return render_template('index.html')


# @app.route('/signup', methods = [ "POST" ])
# def signup_route():
#     return render_template('index.html')


# @app.route('/test_results')
# def test_results():
#     result = conn.execute(text("SELECT UserID, TestID, Grade FROM Grade")).fetchall()
#     return render_template('test_results.html', grade=result)


# @app.route('/test_responses')
# def test_responses():
#     students = conn.execute(text("SELECT CONCAT(FirstName, ' ', LastName) AS Name FROM users WHERE UserType = 'Student'")).fetchall()
#     return render_template('test_responses.html', students=students)


# @app.route('/test_responses', methods = [ "POST" ])
# def test_responses_submit_route():
#     result = conn.execute(text("SELECT UserID, TestID, Grade FROM Grade")).fetchall()
#     return render_template('test_results.html', grade=result)


# @app.route('/test_info')
# def test_info():
#     info = conn.execute(text("SELECT FirstName, LastName, UserType FROM users")).fetchall()
#     return render_template('test_info.html', users=info)


# @app.route('/test_details')
# def test_details():
#     details = conn.execute(text("SELECT FirstName, LastName, UserID, UserType FROM users where UserType = 'Student'")).fetchall()
#     return render_template('test_details.html', users=details)


# @app.route('/test_details', methods = [ "POST" ])
# def test_details_student_route():
#     students = conn.execute(text("SELECT CONCAT(FirstName, ' ', LastName) AS Name FROM users WHERE UserType = 'Student'")).fetchall()
#     return render_template('test_responses.html', students=students)


# @app.route('/test_list')
# def test_list():
#     students = conn.execute(text("SELECT CONCAT(FirstName, ' ', LastName) AS Name FROM users WHERE UserType = 'Student'")).fetchall()
#     return render_template('test_list.html', students=students)


# if __name__ == '__main__':
#     app.run(debug=True)

from flask import Flask, render_template, request, redirect, url_for, session
from flask_mysqldb import MySQL
import MySQLdb.cursors
import MySQLdb.cursors, re, hashlib

app = Flask(__name__)

# Secret Key for Hashing (Keep as-is, it's tuned to the database's current data)
app.secret_key = 'your secret key'

# Enter your database connection details below
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'FunnyPassword321'
app.config['MYSQL_DB'] = '160_final'

# Intialize MySQL
mysql = MySQL(app)


@app.route('/')
def base():
    return render_template('index.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    # Error
    msg = ''
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        # Create variables for access
        username = request.form['username']
        password = request.form['password']
        # Retrieve the hashed password
        hash = password + app.secret_key
        hash = hashlib.sha1(hash.encode())
        password = hash.hexdigest()
                # Check Count Validity
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM users WHERE username = %s AND pass = %s', (username, password,))
        # Fetch one record and return the result
        users = cursor.fetchone()
                # If account exists
        if users:
            # Create session data
            session['loggedin'] = True
            session['id'] = users['UserID']
            session['Username'] = users['Username']
            session['FirstName'] = users['FirstName']
            session['LastName'] = users['LastName']
            session['UserType'] = users['UserType']
            # Redirect to home page
            return redirect('/')
        else:
            # Account doesnt exist or username/password incorrect
            msg = 'Incorrect username/password!'
    return render_template('login.html', msg=msg)


@app.route('/logout')
def logout():
    # Log Out
   session.pop('loggedin', None)
   session.pop('id', None)
   session.pop('username', None)
   # Redirect to login page
   return redirect('/')


@app.route('/signup', methods=['GET', 'POST'])
def register():
    # Error Message
    msg = ''
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        # Create variables for easy access
        username = request.form['username']
        password = request.form['password']
        FirstName = request.form['FirstName']
        LastName = request.form['LastName']
        UserType = request.form['UserType']


                # Check if account exists using MySQL
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM users WHERE username = %s', (username,))
        account = cursor.fetchone()
        # If account exists show error and validation checks
        if account:
            msg = 'Account already exists!'
        elif not re.match(r'[A-Za-z0-9]+', username):
            msg = 'Username must contain only characters and numbers!'
        elif not username or not password:
            msg = 'Please fill out the form!'
        else:
            # Hash the password
            hash = password + app.secret_key
            hash = hashlib.sha1(hash.encode())
            password = hash.hexdigest()
            # Account doesn't exist, and the form data is valid, so insert the new account into the users table
            cursor.execute('INSERT INTO users (username, pass, FirstName, LastName, UserType) VALUES (%s, %s, %s, %s, %s)', (username, password, FirstName, LastName, UserType))

            mysql.connection.commit()
            msg = 'You have successfully registered!'
            return render_template('login.html', msg=msg)
    elif request.method == 'POST':
        # Form is empty... (no POST data)
        msg = 'Please fill out the form!'
    # Show registration form with message (if any)
    return render_template('signup.html', msg=msg)


@app.route('/test_results')
def test_results():
    # Check if user is logged in
    if 'loggedin' in session:
        # User is logged in, fetch test results from database
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('''
            SELECT Tests.TestID, users.FirstName, users.LastName 
            FROM Tests 
            JOIN users ON Tests.UserID = users.UserID
        ''')
        tests = cursor.fetchall()
        return render_template('test_results.html', tests=tests)
    else:
        # User is not logged in, redirect to login page
        return redirect(url_for('login'))
    

@app.route('/take_test/<test_id>')
def take_test(test_id):
    
    if session['UserType'] == 'Student':
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM questions WHERE TestID = %s', (test_id,))
        questions = cursor.fetchall()

        return render_template('take_test.html', test_id=test_id, questions=questions)
    else:
        return redirect('/test_results')


@app.route('/take_test/<test_id>', methods=['POST'])
def submit_answers(test_id):
    if 'loggedin' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        try:
            # Get the UserID from the session
            user_id = session['id']
            # Get the form data containing answers
            answers = {key.split('_')[1]: value for key, value in request.form.items() if key.startswith('answer_')}
            # Insert answers into the responses table
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            for question_id, answer in answers.items():
                cursor.execute("INSERT INTO responses (QuestionID, UserID, Answer) VALUES (%s, %s, %s)", (question_id, user_id, answer))
            mysql.connection.commit()
            return redirect(url_for('test_results'))
        except Exception as e:
            return str(e)
    else:
        return "Method not allowed"



@app.route('/accounts')
def accounts():
    try:
        # Establish database connection
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        
        # Fetch all user accounts from the database
        cursor.execute("SELECT UserID, FirstName, LastName, UserType FROM users ORDER BY UserType")
        users = cursor.fetchall()
        
        # Close database connection
        cursor.close()
        
        # Render the accounts.html template with the user data
        return render_template('accounts.html', users=users)
    except Exception as e:
        return str(e)
    

@app.route('/tests')
def show_tests():
    
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('''
        SELECT Tests.TestID, Tests.UserID, users.FirstName, users.LastName 
        FROM Tests 
        JOIN users ON Tests.UserID = users.UserID
    ''')
    tests = cursor.fetchall()
    return render_template('tests.html', tests=tests)





if __name__ == '__main__':
    app.run(debug=True)
