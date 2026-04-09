from flask import Flask, render_template, request, redirect
import sqlite3

app = Flask(__name__)

# Создаем таблицу, если нет
conn = sqlite3.connect('database.db')
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

# Главная страница
@app.route('/')
def index():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM expenses")
    expenses = cursor.fetchall()
    conn.close()
    return render_template('index.html', expenses=expenses)

# Добавить расход
@app.route('/add', methods=['POST'])
def add():
    category = request.form['category']
    amount = request.form['amount']
    note = request.form['note']
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute("INSERT INTO expenses (category, amount, note) VALUES (?, ?, ?)",
                   (category, amount, note))
    conn.commit()
    conn.close()
    return redirect('/')

# Удалить расход
@app.route('/delete/<int:id>')
def delete(id):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute("DELETE FROM expenses WHERE id = ?", (id,))
    conn.commit()
    conn.close()
    return redirect('/')

# Редактировать расход
@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit(id):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    if request.method == 'POST':
        category = request.form['category']
        amount = request.form['amount']
        note = request.form['note']
        cursor.execute("UPDATE expenses SET category=?, amount=?, note=? WHERE id=?",
                       (category, amount, note, id))
        conn.commit()
        conn.close()
        return redirect('/')
    else:
        cursor.execute("SELECT * FROM expenses WHERE id=?", (id,))
        expense = cursor.fetchone()
        conn.close()
        return render_template('index.html', expenses=[expense], edit=True)

if __name__ == '__main__':
    app.run(debug=True)