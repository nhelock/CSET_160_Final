from flask import Flask, render_template, request
from sqlalchemy import Column, Integer, String, Numeric, create_engine, text
import uuid
from flask import redirect, url_for


app = Flask(__name__)
conn_str = "mysql://root:NateNate3.00@localhost/cset_160_final1"
engine = create_engine(conn_str, echo=True)
conn = engine.connect()


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/user/<name>')
def user(name):
    return render_template('user.html', name=name)


@app.route('/tests')
def show_tests():
    query = text("SELECT * FROM tests")
    result = conn.execute(query)
    tests = [dict(row) for row in result]
    return render_template('tests.html', tests=tests)

@app.route('/create_test', methods=['GET'])
def create_get_request():
    return render_template('create_test.html')

@app.route('/create_test', methods=['POST'])
def create_test():
    try:
        test_id = request.form.get('test_id')

        question1 = request.form.get('question1')
        question2 = request.form.get('question2')
        question3 = request.form.get('question3')

        question1_id = str(uuid.uuid4())
        question2_id = str(uuid.uuid4())
        question3_id = str(uuid.uuid4())
        conn.execute(
            text(
                "INSERT INTO questions (TestID, QuestionID, Question) VALUES (:test_id, :question1_id, :question1), (:test_id, :question2_id, :question2), (:test_id, :question3_id, :question3)"),
            {"test_id": test_id, "question1_id": question1_id, "question2_id": question2_id,
             "question3_id": question3_id, "question1": question1, "question2": question2, "question3": question3}
        )

        return render_template('create_test.html', error=None, success="Test created successfully!")
    except Exception as e:
        error = e.orig.args[1]
        print(error)
        return render_template('create_test.html', error=error, success=None)


@app.route('/edit_test/<int:test_id>', methods=['GET', 'POST'])
def edit_test(test_id):
    if request.method == 'POST':
        question1 = request.form['question1']
        question2 = request.form['question2']
        question3 = request.form['question3']

        query = text(
            "UPDATE tests SET question1 = :question1, question2 = :question2, question3 = :question3 WHERE id = :test_id")
        conn.execute(query, question1=question1, question2=question2, question3=question3, test_id=test_id)

        return redirect(url_for('show_tests'))

    test_info = ...
    return render_template('edit_test.html', test_info=test_info)


@app.route('/delete', methods=['GET'])
def delete_get_request():
    return render_template('tests_delete.html')

@app.route('/delete', methods=['POST'])
def delete_test():
    try:
        conn.execute(
            text("DELETE FROM boats WHERE id = :id"),
            request.form
        )
        return render_template('tests_delete.html', error=None, success="Data deleted successfully!")
    except Exception as e:
        error = e.orig.args[1]
        print(error)
        return render_template('tests_delete.html', error=error, success=None)


if __name__ == '__main__':
    app.run(debug=True)
