from flask import Flask, request, jsonify
import sqlite3

app = Flask(__name__)

# Подключение к базе
def get_db():
    return sqlite3.connect("expenses.db")

# Создание таблицы
def create_table():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS expenses (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        category TEXT,
        amount REAL,
        note TEXT
    )
    """)
    conn.commit()
    conn.close()

create_table()

# Добавить расход
@app.route('/add', methods=['POST'])
def add_expense():
    data = request.json
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO expenses (category, amount, note) VALUES (?, ?, ?)",
        (data['category'], data['amount'], data['note'])
    )
    conn.commit()
    conn.close()
    return jsonify({"message": "Expense added"})

# Показать все расходы
@app.route('/expenses', methods=['GET'])
def get_expenses():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM expenses")
    rows = cursor.fetchall()
    conn.close()
    
    return jsonify(rows)

# Обновить расход
@app.route('/update/<int:id>', methods=['PUT'])
def update_expense(id):
    data = request.json
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE expenses SET category=?, amount=?, note=? WHERE id=?",
        (data['category'], data['amount'], data['note'], id)
    )
    conn.commit()
    conn.close()
    return jsonify({"message": "Updated"})

# Удалить расход
@app.route('/delete/<int:id>', methods=['DELETE'])
def delete_expense(id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM expenses WHERE id=?", (id,))
    conn.commit()
    conn.close()
    return jsonify({"message": "Deleted"})

if __name__ == '__main__':
    app.run(debug=True)