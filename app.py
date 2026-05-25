from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import json
import os

app = Flask(__name__, static_folder=".")
CORS(app)

DATA_FILE = "classroom.json"


# =========================
# DATABASE
# =========================
def load_db():
    if not os.path.exists(DATA_FILE):
        return {}
    try:
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    except:
        return {}


def save_db(db):
    with open(DATA_FILE, "w") as f:
        json.dump(db, f, indent=2)


# =========================
# FRONTEND ROUTES
# =========================
@app.route("/")
def home():
    return send_from_directory(".", "index.html")


@app.route("/dashboard")
def dashboard():
    return send_from_directory(".", "dashboard.html")


# =========================
# FRACTION ENGINE (KID MODE)
# =========================
def fraction_engine(a, b):

    a = int(a)
    b = int(b)

    integer = a // b
    remainder = a % b

    steps = []
    digits = []

    steps.append({
        "step": 1,
        "text": f"{a} ÷ {b} ≈ {integer} remainder {remainder}",
        "digit": "",
        "color": "blue"
    })

    step = 2
    colors = ["green", "red", "blue", "yellow"]

    while remainder != 0 and step <= 8:

        dividend = remainder * 10
        digit = dividend // b
        remainder = dividend % b

        digits.append(str(digit))

        steps.append({
            "step": step,
            "text": f"{dividend} ÷ {b} ≈ {digit} remainder {remainder}",
            "digit": str(digit),
            "color": colors[(step - 2) % len(colors)]
        })

        step += 1

    decimal = str(integer)

    if digits:
        decimal += "." + "".join(digits)

    if remainder != 0:
        decimal += "..."

    return decimal, steps


# =========================
# SOLVE MODE
# =========================
@app.route("/ask", methods=["POST"])
def ask():

    data = request.get_json()

    topic = data.get("topic", "")
    student = data.get("student", "guest")

    if "/" not in topic:
        return jsonify({"error": "Invalid format. Use a/b"})

    a, b = topic.split("/")

    decimal, steps = fraction_engine(a, b)

    percentage = round((int(a) / int(b)) * 100, 6)

    db = load_db()

    if student not in db:
        db[student] = {
            "score": 50,
            "streak": 0,
            "attempts": []
        }

    db[student]["attempts"].append({
        "topic": topic,
        "decimal": decimal,
        "percentage": percentage
    })

    save_db(db)

    return jsonify({
        "decimal": decimal,
        "steps": steps,
        "percentage": percentage
    })


# =========================
# QUIZ MODE (STRICT CHECK)
# =========================
@app.route("/quiz", methods=["POST"])
def quiz():

    data = request.get_json()

    topic = data.get("topic", "")
    answer = data.get("answer", None)
    student = data.get("student", "guest")

    if "/" not in topic:
        return jsonify({"correct": False, "error": "Invalid fraction"})

    a, b = topic.split("/")

    correct = round((int(a) / int(b)) * 100, 6)

    try:
        user = float(answer)
    except:
        return jsonify({
            "correct": False,
            "error": "Answer must be a number",
            "correct_answer": correct
        })

    is_correct = abs(user - correct) < 0.0001

    db = load_db()

    if student not in db:
        db[student] = {
            "score": 50,
            "streak": 0,
            "attempts": []
        }

    if is_correct:
        db[student]["score"] += 5
        db[student]["streak"] += 1
    else:
        db[student]["score"] -= 2
        db[student]["streak"] = 0

    db[student]["score"] = max(0, min(100, db[student]["score"]))

    db[student]["attempts"].append({
        "topic": topic,
        "user_answer": user,
        "correct_answer": correct,
        "result": is_correct
    })

    save_db(db)

    return jsonify({
        "correct": is_correct,
        "correct_answer": correct,
        "score": db[student]["score"],
        "streak": db[student]["streak"]
    })


# =========================
# STUDENT PROFILE
# =========================
@app.route("/student/<name>")
def student(name):

    db = load_db()

    return jsonify(db.get(name, {
        "score": 0,
        "streak": 0,
        "attempts": []
    }))


# =========================
# LEADERBOARD
# =========================
@app.route("/leaderboard")
def leaderboard():

    db = load_db()

    board = []

    for name, data in db.items():
        board.append({
            "student": name,
            "score": data.get("score", 0),
            "streak": data.get("streak", 0),
            "attempts": len(data.get("attempts", []))
        })

    board.sort(key=lambda x: x["score"], reverse=True)

    return jsonify(board)


# =========================
# RUN SERVER
# =========================
if __name__ == "__main__":
    print("🧠 Hermes Classroom Engine Running")
    print("🌐 Open: http://127.0.0.1:5000")
    app.run(debug=True)