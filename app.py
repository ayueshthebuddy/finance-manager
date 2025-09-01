from flask import Flask, render_template, request, redirect, url_for
import sqlite3
import os

app = Flask(__name__)

# ---------- Database Setup ----------
def init_db():
    if not os.path.exists("database"):
        os.makedirs("database")

    conn = sqlite3.connect("database/finance.db")
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS transactions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        date TEXT NOT NULL,
        category TEXT NOT NULL,
        type TEXT CHECK(type IN ('Income', 'Expense')) NOT NULL,
        amount REAL NOT NULL,
        note TEXT
    )
    """)
    
    conn.commit()
    conn.close()

init_db()

# ---------- Routes ----------
@app.route("/")
def home():
    conn = sqlite3.connect("database/finance.db")
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM transactions ORDER BY date DESC")
    transactions = cursor.fetchall()
    
    cursor.execute("SELECT SUM(amount) FROM transactions WHERE type='Income'")
    total_income = cursor.fetchone()[0] or 0
    
    cursor.execute("SELECT SUM(amount) FROM transactions WHERE type='Expense'")
    total_expense = cursor.fetchone()[0] or 0
    
    balance = total_income - total_expense
    
    conn.close()
    
    return render_template(
        "index.html",
        transactions=transactions,
        total_income=total_income,
        total_expense=total_expense,
        balance=balance
    )

# Route for handling form submission
@app.route("/add", methods=["POST"])
def add_transaction():
    date = request.form["date"]
    category = request.form["category"]
    type_ = request.form["type"]
    amount = request.form["amount"]
    note = request.form["note"]

    conn = sqlite3.connect("database/finance.db")
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO transactions (date, category, type, amount, note) VALUES (?, ?, ?, ?, ?)",
        (date, category, type_, amount, note),
    )
    conn.commit()
    conn.close()

    return redirect(url_for("home"))

if __name__ == "__main__":
    app.run(debug=True)
