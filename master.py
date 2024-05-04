from flask import Flask, render_template, request, redirect, url_for, session
from flask_mysqldb import MySQL
import MySQLdb.cursors
import MySQLdb.cursors, re, hashlib
import json

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


@app.route('/test_list')
def test_list():
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
        return render_template('test_list.html', tests=tests)
    else:
        # User is not logged in, redirect to login page
        return redirect(url_for('login'))
    

@app.route('/take_test/<test_id>')
def take_test(test_id):
    if 'loggedin' not in session:
        return redirect(url_for('login'))

    # Search for Submissions
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("SELECT * FROM Grade WHERE TestID = %s AND UserID = %s", (test_id, session['id']))
    submission = cursor.fetchone()

    if submission:
        return redirect(url_for('test_list'))

    # Redirect to test:
    if session['UserType'] == 'Student':
        cursor.execute('SELECT * FROM questions WHERE TestID = %s', (test_id,))
        questions = cursor.fetchall()
        return render_template('take_test.html', test_id=test_id, questions=questions)
    else:
        return redirect('/test_list')



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
            cursor.execute("INSERT INTO Grade (TestID, UserID) VALUES (%s, %s)", (test_id, user_id))
            mysql.connection.commit()
            return redirect(url_for('test_list'))
        except Exception as e:
            return str(e)
    else:
        return "Method not allowed"
    


@app.route('/test_grades/<test_id>')
def test_grades(test_id):
    try:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("""
            SELECT r.UserID, q.Question, r.Answer, g.Grade
            FROM responses r
            INNER JOIN questions q ON r.QuestionID = q.QuestionID
            LEFT JOIN Grade g ON r.UserID = g.UserID AND q.TestID = g.TestID
            WHERE q.TestID = %s
        """, (test_id,))
        submissions = cursor.fetchall()

        # Group submissions by user
        grouped_submissions = {}
        for submission in submissions:
            user_id = submission['UserID']
            if user_id not in grouped_submissions:
                grouped_submissions[user_id] = []
            grouped_submissions[user_id].append(submission)

        return render_template('test_grades.html', test_submissions=grouped_submissions, test_id=test_id)
    except Exception as e:
        return str(e)

    

@app.route('/test_grades/<test_id>/', methods=['POST'])
def grade_submission(test_id):
    if 'loggedin' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        try:

            grade = request.form.get('grade')
            
            student_id = request.form.get('student_id')

            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute("UPDATE Grade SET Grade = %s WHERE UserID = %s AND TestID = %s", (grade, student_id, test_id))
            mysql.connection.commit()

            return redirect(url_for('test_grades', test_id=test_id))
        except Exception as e:
            return str(e)
    else:
        return redirect(url_for('test_grades', test_id=test_id))






@app.route('/accounts')
def accounts():
    try:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        
        cursor.execute("SELECT UserID, FirstName, LastName, UserType FROM users ORDER BY UserType")
        users = cursor.fetchall()
        
        cursor.close()
        
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



@app.route('/delete_test/<test_id>', methods=['POST'])
def delete_test(test_id):
    try:
        cursor = mysql.connection.cursor()
        cursor.execute("DELETE FROM Tests WHERE TestID = %s", (test_id,))
        mysql.connection.commit()
        return redirect(url_for('show_tests'))
    except Exception as e:
        return str(e)



@app.route('/edit_test/<test_id>', methods=['GET'])
def show_test(test_id):
    if request.method == 'GET':

        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("SELECT * FROM Tests WHERE TestID = %s", (test_id,))
        test_details = cursor.fetchone()

        cursor.execute("SELECT QuestionID, Question FROM Questions WHERE TestID = %s", (test_id,))
        questions = cursor.fetchall()

        return render_template('edit_test.html', test_id=test_id, test_details=test_details, questions=questions)


from flask import request

@app.route('/edit_test/<test_id>', methods=['POST'])
def edit_test(test_id):
    try:
        
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        
        for question_id, question_text in request.form.items():
            if question_id.startswith('question_'):
                question_id = question_id.split('_')[1]
                delete_checkbox = request.form.get('delete_' + question_id)
                if delete_checkbox:

                    cursor.execute("DELETE FROM Questions WHERE QuestionID = %s", (question_id,))
                else:

                    cursor.execute("UPDATE Questions SET Question = %s WHERE QuestionID = %s", (question_text, question_id))
        
        mysql.connection.commit()
        
        return redirect(('/tests'))
    except Exception as e:
        return str(e)
    





@app.route('/create_test', methods=['GET'])
def create_test():
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    try:

        cursor.execute("INSERT INTO Tests (UserID) VALUES (%s)", (session['id'],))
        mysql.connection.commit()
        
        cursor.execute("SELECT LAST_INSERT_ID() as TestID")
        testid = cursor.fetchone()['TestID']
        
        return redirect(url_for('add_questions', test_id=testid))
    except Exception as e:
        return str(e)



@app.route('/create_test', methods=['POST'])
def create_questions():
    try:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("SELECT LAST_INSERT_ID() as TestID")
        test_id = cursor.fetchone()['TestID']

        return redirect(url_for('add_questions/<test_id>', test_id=test_id))
    except Exception as e:
        return str(e)




@app.route('/add_questions/<test_id>', methods=['GET', 'POST'])
def add_questions(test_id):
    if request.method == 'POST':
        try:
            for key, value in request.form.items():
                if key.startswith('question_'):
                    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
                    cursor.execute("INSERT INTO Questions (TestID, Question) VALUES (%s, %s)", (test_id, value))
                    mysql.connection.commit()

            return redirect('/tests')
        except Exception as e:
            return str(e)
    else:
        return render_template('add_questions.html', test_id=test_id)







@app.route('/my_grade')
def grades():
    if 'loggedin' not in session:
        return redirect(url_for('login'))
    
    try:
        user_id = session['id']

        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("SELECT TestID, Grade FROM Grade WHERE UserID = %s", (user_id,))
        grades = cursor.fetchall()
        

        return render_template('my_grade.html', grades=grades)
    except Exception as e:
        return str(e)






if __name__ == '__main__':
    app.run(debug=True)
