from flask import Flask, render_template, request, redirect
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

# Initialize DB when app starts
init_db()

# ---------- Home Dashboard ----------
@app.route("/")
def home():
    conn = sqlite3.connect("database/finance.db")
    cursor = conn.cursor()
    
    # Total Income
    cursor.execute("SELECT SUM(amount) FROM transactions WHERE type='Income'")
    total_income = cursor.fetchone()[0] or 0
    
    # Total Expense
    cursor.execute("SELECT SUM(amount) FROM transactions WHERE type='Expense'")
    total_expense = cursor.fetchone()[0] or 0
    
    # Balance
    balance = total_income - total_expense
    
    # Expenses by category (for pie chart)
    cursor.execute("SELECT category, SUM(amount) FROM transactions WHERE type='Expense' GROUP BY category")
    category_data = cursor.fetchall()
    categories = [row[0] for row in category_data]
    category_amounts = [row[1] for row in category_data]
    
    conn.close()
    
    return render_template(
        "index.html",
        total_income=total_income,
        total_expense=total_expense,
        balance=balance,
        categories=categories,
        category_amounts=category_amounts
    )

# ---------- Transactions Page ----------
@app.route("/transactions")
def get_transactions():
    conn = sqlite3.connect("database/finance.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM transactions")
    rows = cursor.fetchall()
    conn.close()

    return render_template("transactions.html", transactions=rows)

# ---------- Add Transaction Form Submission ----------
@app.route("/add_transaction", methods=["POST"])
def add_transaction():
    date = request.form["date"]
    category = request.form["category"]
    type_ = request.form["type"]
    amount = float(request.form["amount"])
    note = request.form["note"]

    conn = sqlite3.connect("database/finance.db")
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO transactions (date, category, type, amount, note)
        VALUES (?, ?, ?, ?, ?)
    """, (date, category, type_, amount, note))
    conn.commit()
    conn.close()

    return redirect("/transactions")

@app.route("/delete_transaction/<int:id>")
def delete_transaction(id):
    conn = sqlite3.connect("database/finance.db")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM transactions WHERE id=?", (id,))
    conn.commit()
    conn.close()
    return redirect("/transactions")

# -------------Show edit form--------------------
@app.route("/edit_transaction/<int:id>")
def edit_transaction(id):
    conn = sqlite3.connect("database/finance.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM transactions WHERE id=?", (id,))
    tx = cursor.fetchone()
    conn.close()
    return render_template("edit_transaction.html", tx=tx)

# Handle edit form submission
@app.route("/update_transaction/<int:id>", methods=["POST"])
def update_transaction(id):
    date = request.form["date"]
    category = request.form["category"]
    type_ = request.form["type"]
    amount = float(request.form["amount"])
    note = request.form["note"]

    conn = sqlite3.connect("database/finance.db")
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE transactions 
        SET date=?, category=?, type=?, amount=?, note=?
        WHERE id=?
    """, (date, category, type_, amount, note, id))
    conn.commit()
    conn.close()
    return redirect("/transactions")



# ---------- Run App ----------
if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
