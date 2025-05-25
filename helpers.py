from cs50 import SQL
from flask import redirect, session
from functools import wraps

db = SQL("sqlite:///vocabulary.db")

levels = ['a1', 'a2', 'b1', 'b2', 'c1', 'c2']

def login_required(f):
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)

    return decorated_function


def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not is_admin():
            return redirect("/")
        return f(*args, **kwargs)
    return decorated_function


def is_admin():
    user = db.execute("SELECT role FROM users WHERE id = ?", session.get("user_id"))
    return user and user[0]["role"] == "admin"


def get_questions(type, num_questions=20, seed_value="user_123456"):
    rowids = db.execute("SELECT id, level, type FROM questions WHERE type = ?", type)
    if not rowids:
        return []

    question_ids = []
    if type == "Placement":
        n = num_questions / 6 
        for level in levels:
            random_ids = sorted([row['id'] for row in rowids if row['type'] == 'Placement' and row['level'] == level], key=lambda x: hash(f"{seed_value}_{x}") % 1000)
            selected_ids = random_ids[:int(n)]
            print(selected_ids)
            question_ids.extend(selected_ids)
    else:
        question_ids = [row['id'] for row in rowids]

    num_questions = min(num_questions, len(question_ids))

    random_ids = sorted(question_ids, key=lambda x: hash(f"{seed_value}_{x}") % 1000)

    selected_ids = random_ids[:num_questions]

    query = """
        SELECT id, question, option0, option1, option2, option3, answer
        FROM questions
        WHERE id IN ({})
    """.format(','.join('?' * len(selected_ids)))

    questions = db.execute(query, *selected_ids)

    return questions