from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import login_required, admin_required, get_questions, is_admin

max_question_number = 30

app = Flask(__name__)

app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

db = SQL("sqlite:///vocabulary.db")
types = {"A1", "A2", "B1", "B2", "C1", "C2", "Placement"}
levels = {"a1", "a2", "b1", "b2", "c1", "c2", "none"}


@app.route('/list_questions')
@admin_required
def list_questions():
    questions = db.execute("SELECT * FROM questions")
    return render_template("listQ.html", questions=questions)


@app.route('/edit_user/<int:id>', methods=['GET', 'POST'])
@admin_required
def edit_user_role(id):
    user = db.execute("SELECT * FROM users WHERE id = ?", id)

    if len(user) != 1:
        flash("User not found", "danger")
        return redirect('/list_users')

    if request.method == 'POST':
        new_role = request.form['role']

        if not new_role:
            flash("Role cannot be empty", "danger")
            return redirect(f'/edit_user/{id}')

        try:
            db.execute("UPDATE users SET role = ? WHERE id = ?", new_role, id)
            flash("User role updated successfully!", "success")
            return redirect('/list_users')
        except Exception as e:
            flash(f"Error: {str(e)}", "danger")
            return redirect(f'/edit_user/{id}')

    return render_template('editU.html', user=user[0])


@app.route('/delete_question/<int:id>', methods=['GET', 'POST'])
@admin_required
def delete_question_by_id(id):
    try:
        db.execute("DELETE FROM questions WHERE id = ?", id)
        flash("Question deleted successfully!", "success")
        return redirect('/list_questions')
    except Exception as e:
        flash(f"Error: {str(e)}", "danger")
        return redirect('/list_questions')


@app.route('/delete_user/<int:id>', methods=['GET', 'POST'])
@admin_required
def delete_user(id):
    try:
        # Delete related records in the results table
        db.execute("DELETE FROM results WHERE user_id = ?", id)
        
        # Delete the user
        db.execute("DELETE FROM users WHERE id = ?", id)
        
        flash("User deleted successfully!", "success")
        return redirect('/list_users')
    except Exception as e:
        flash(f"Error: {str(e)}", "danger")
        return redirect('/list_users')


@app.route('/add_user', methods=['GET', 'POST'])
@admin_required
def add_user():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        role = request.form['role']

        if not username or not password or not role:
            flash("All fields must be filled out", "danger")
            return redirect('/add_user')

        hashed_password = generate_password_hash(password)

        try:
            db.execute("INSERT INTO users (username, hash, role) VALUES (?, ?, ?)",
                       username, hashed_password, role)

            flash(f"User {username} added successfully!", "success")

            return redirect('/list_users')
        except Exception as e:
            flash(f"Error: {str(e)}", "danger")
            return redirect('/add_user')

    return render_template('addU.html')


@app.route('/list_users')
@admin_required
def list_users():
    all_users = db.execute("SELECT * FROM users ORDER BY username")
    return render_template('listU.html', users=all_users)


@app.route('/delete_question', methods=['GET', 'POST'])
@admin_required
def delete_question():
    global types, levels
    if request.method == 'GET':
        questions = db.execute("SELECT * FROM questions")
        num = len(questions)
        return render_template('deleteQ.html', questions=questions, types=types, levels=levels, num=num)

    if request.method == 'POST':
        question_id = request.form['question_id']
        if not question_id:
            flash('Please select a question to delete', 'danger')
            return redirect("/delete_question")
        try:
            db.execute("DELETE FROM questions WHERE id = ?", question_id)
            flash('Question deleted successfully!', 'success')
        except Exception as e:
            flash('An error occurred while deleting the question. Please try again later.', 'danger')

        return redirect("/admin")


@app.route('/change_question', methods=['GET', 'POST'])
@admin_required
def change_question():
    if request.method == 'POST':
        if not request.form['question_id']:
            flash('Please select a question to change', 'danger')
            return redirect("/change_question")
        question_id = int(request.form['question_id'])
        new_question = request.form['new_question'].strip()
        option0 = request.form['option0'].strip()
        option1 = request.form['option1'].strip()
        option2 = request.form['option2'].strip()
        option3 = request.form['option3'].strip()
        answer = int(request.form['answer'])
        level = request.form['level']
        if level:
            level = level.strip().lower()
        type_ = request.form['type']
        type_ = type_.strip().capitalize()

        try:
            db.execute("""
                UPDATE questions
                SET question = ?, option0 = ?, option1 = ?, option2 = ?, option3 = ?, answer = ?, level = ?, type = ?
                WHERE id = ?
            """, new_question, option0, option1, option2, option3, answer, level, type_, question_id)
            flash("Question updated successfully!", "success")
            return redirect("/change_question")
        except Exception as e:
            flash(f"Error: {str(e)}", "danger")
            return redirect("/change_question")

    questions = db.execute("SELECT * FROM questions")
    num = len(questions)
    return render_template('changeQ.html', questions=questions, types=types, levels=levels, num=num)


@app.route("/admin")
@admin_required
def admin():
    return render_template("admin.html")


@app.route('/add_question', methods=['GET', 'POST'])
@admin_required
def add_question():
    if request.method == 'POST':
        question = request.form['question'].strip()
        option0 = request.form['option0'].strip()
        option1 = request.form['option1'].strip()
        option2 = request.form['option2'].strip()
        option3 = request.form['option3'].strip()
        answer = int(request.form['answer'])
        level = request.form['level']
        if level:
            level = level.strip().lower()
            session["Alevel"] = level

        type_ = request.form['type']
        type_ = type_.strip().capitalize()
        session["Atype"] = type_

        try:
            db.execute("""
                INSERT INTO questions (question, option0, option1, option2, option3, answer, level, type)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, question, option0, option1, option2, option3, answer, level, type_)
            flash("Question added successfully!", "success")
            return redirect("/add_question")
        except Exception as e:
            flash(f"Error: {str(e)}", "danger")
            return redirect("/add_question")

    level = session.get("Alevel", "")
    type_ = session.get("Atype", "")
    return render_template('addQ.html', type=type_, level=level)


@app.route("/test/<type>", methods=["GET"])
@login_required
def test(type):
    type = type.capitalize()
    questions = get_questions(type, max_question_number, session["username"])
    if not questions:
        flash("There are no questions in that type yet", "info")
        return redirect("/")

    return render_template("test.html", type=type, questions=questions)


@app.route("/result/<type>", methods=["POST"], endpoint="result_endpoint")
@login_required
def result(type):
    type = type.capitalize()
    questions = get_questions(type, max_question_number, session["username"])
    if not questions:
        flash("Could not find any questions in that type", "danger")
        return redirect("/")

    user_answers = {}
    for question in questions:
        question_id = question["id"]
        user_answers[question_id] = request.form.get(
            f"question{question_id}", "-1")  # Default to -1 if no answer is selected

    score = 0
    for question in questions:
        question["user_answer"] = int(user_answers[question["id"]])
        if question["user_answer"] == int(question["answer"]):
            score += 1

    db.execute("INSERT INTO results (user_id, correct, total, type) VALUES(?, ?, ?, ?)",
               session["user_id"], score, len(questions), type)

    return render_template("result.html", score=score, total=len(questions), questions=questions, user_answers=user_answers, type=type)


@app.route("/")
def index():
    return render_template("index.html", is_admin=is_admin())


@app.route("/results", endpoint="results_endpoint")
@login_required
def results():
    results = db.execute(
        "SELECT * FROM results WHERE user_id = ? ORDER BY date DESC", session["user_id"])
    return render_template("results.html", results=results)


@app.route("/login", methods=["GET", "POST"])
def login():
    session.clear()

    if request.method == "POST":
        if not request.form.get("username"):
            flash("must provide username", "danger")
            return redirect("/login")
        elif not request.form.get("password"):
            flash("must provide password", "danger")
            return redirect("/login")

        user = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))

        if len(user) != 1 or not check_password_hash(user[0]["hash"], request.form.get("password")):
            flash("Invalid username and/or password", "danger")
            return redirect("/login")

        session["user_id"] = user[0]["id"]
        session["username"] = user[0]["username"]

        return redirect("/")
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    if request.method == "POST":
        if not request.form.get("username"):
            flash("must provide username", "danger")
            return redirect("/register")
        elif not request.form.get("password"):
            flash("must provide password", "danger")
            return redirect("/register")
        elif not request.form.get("confirmation"):
            flash("must provide password confirmation", "danger")
            return redirect("/register")

        user = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))

        if request.form.get("password") != request.form.get("confirmation"):
            flash("password and confirmation must be same", "danger")
            return redirect("/register")

        if user:
            flash("username taken", "danger")
            return redirect("/register")

        hash = generate_password_hash(request.form.get("password"))
        user = db.execute('INSERT INTO users (username, hash, role) VALUES(?, ?, "user")',
                          request.form.get("username"), hash)

        user = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))
        session["user_id"] = user[0]["id"]
        session["username"] = user[0]["username"]

        return redirect("/")
    else:
        return render_template("register.html")


if __name__ == "__main__":
    app.run(debug=True)
