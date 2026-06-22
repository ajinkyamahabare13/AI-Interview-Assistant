from flask import Flask, render_template, request, session
import pandas as pd
import csv
import difflib
import sqlite3
import random

app = Flask(__name__)
app.secret_key = "interview_secret_key"


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/start", methods=["POST"])
def start():

    subject = request.form["subject"]
    name = request.form["name"]

    session["name"] = name
    session["subject"] = subject

    if subject == "aiml":
     df = pd.read_csv("aiml_questions.csv")

    elif subject == "dbms":
     df = pd.read_csv("dbms_questions.csv")

    else:
     df = pd.read_csv("python_questions.csv")
    sampled_df = df.sample(min(10, len(df)))

    questions = sampled_df["Question"].tolist()

    answers = sampled_df["Answer"].tolist()

    session["answers"] = answers

    session["questions"] = questions
    session["current"] = 0
    session["total_score"] = 0
    session["user_answers"] = []
    session["question_scores"] = []

    return render_template(
        "interview.html",
        question=questions[0],
        qno=1,
        total=len(questions)
    )


@app.route("/submit", methods=["POST"])
def submit():

    answer = request.form["answer"]
    session["user_answers"].append(answer)
    correct_answer = session["answers"][session["current"]]

    similarity = difflib.SequenceMatcher(
    None,
    answer.lower(),
    correct_answer.lower()
    ).ratio()

    score = round(similarity * 10)
    session["question_scores"].append(score)

    session["total_score"] += score
    session["current"] += 1

    questions = session["questions"]
    current = session["current"]

    if current < len(questions):

        return render_template(
            "interview.html",
            question=questions[current],
            qno=current + 1,
            total=len(questions)
        )

    total_score = session["total_score"]

    percentage = min(
        100,
        round((total_score / (len(questions) * 20)) * 100)
    )

    if percentage >= 80:
        performance = "Excellent"

    elif percentage >= 60:
        performance = "Good"

    else:
        performance = "Needs Improvement"

    # Save results
    conn = sqlite3.connect("interview.db")

    cursor = conn.cursor()

    cursor.execute(
    """
    INSERT INTO results
    (name, subject, score, percentage)
    VALUES (?, ?, ?, ?)
    """,
    (
        session["name"],
        session["subject"],
        total_score,
        f"{percentage}%"
    )
)

    conn.commit()
    conn.close()

    return render_template(
    "result.html",
    subject=session["subject"].upper(),
    total_questions=len(questions),
    score=total_score,
    percentage=percentage,
    performance=performance,
    questions=questions,
    user_answers=session["user_answers"],
    correct_answers=session["answers"],
    question_scores=session["question_scores"]
)


@app.route("/reports")
def reports():

    conn = sqlite3.connect("interview.db")

    conn.row_factory = sqlite3.Row

    cursor = conn.cursor()

    cursor.execute("SELECT * FROM results")

    data = cursor.fetchall()

    conn.close()

    return render_template(
        "reports.html",
        data=data
    )

@app.route("/leaderboard")
def leaderboard():

    conn = sqlite3.connect("interview.db")

    conn.row_factory = sqlite3.Row

    cursor = conn.cursor()

    cursor.execute("""
        SELECT *
        FROM results
        ORDER BY score DESC
        LIMIT 10
    """)

    data = cursor.fetchall()

    conn.close()

    return render_template(
        "leaderboard.html",
        data=data
    )
if __name__ == "__main__":
    app.run(debug=True)