import sqlite3
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder, CommandHandler, CallbackQueryHandler,
    MessageHandler, ContextTypes, filters
)

# --- Database setup ---
conn = sqlite3.connect('bank.db', check_same_thread=False)
c = conn.cursor()
c.execute('''
CREATE TABLE IF NOT EXISTS transactions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    type TEXT NOT NULL,
    category TEXT,
    amount REAL NOT NULL,
    note TEXT,
    date TEXT NOT NULL
)
''')
conn.commit()

# --- Get balance ---
def get_balance():
    c.execute("SELECT SUM(amount) FROM transactions WHERE type='deposit'")
    deposits = c.fetchone()[0] or 0
    c.execute("SELECT SUM(amount) FROM transactions WHERE type='expense'")
    expenses = c.fetchone()[0] or 0
    return deposits - expenses

# --- Main menu ---
def main_menu():
    keyboard = [
        [InlineKeyboardButton("💰 Balance", callback_data='balance'),
         InlineKeyboardButton("📜 Show Transactions", callback_data='show')],
        [InlineKeyboardButton("➕ Add Deposit", callback_data='deposit'),
         InlineKeyboardButton("➖ Add Expense", callback_data='expense')]
    ]
    return InlineKeyboardMarkup(keyboard)

# --- Expense categories menu ---
def expense_categories_menu():
    keyboard = [
        [InlineKeyboardButton("🍔 Food", callback_data='cat_food'),
         InlineKeyboardButton("🚌 Transport", callback_data='cat_transport')],
        [InlineKeyboardButton("🎮 Entertainment", callback_data='cat_fun'),
         InlineKeyboardButton("📦 Other", callback_data='cat_other')],
        [InlineKeyboardButton("⬅️ Back", callback_data='back')]
    ]
    return InlineKeyboardMarkup(keyboard)

# --- /start handler ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Hello! I am your Interactive Bank Bot 💳\nChoose an action:",
        reply_markup=main_menu()
    )

# --- Callback for buttons ---
async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "balance":
        await query.edit_message_text(
            f"💰 Current balance: {get_balance()}₸",
            reply_markup=main_menu()
        )

    elif query.data == "show":
        c.execute('SELECT * FROM transactions')
        rows = c.fetchall()
        if not rows:
            await query.edit_message_text("No transactions yet.", reply_markup=main_menu())
            return
        message = "📜 All transactions:\n"
        for row in rows:
            category_text = f"{row[2]} " if row[2] else ""
            note_text = f"{row[4]}" if row[4] else ""
            message += f"{row[0]}. {row[1]} {category_text}{row[3]}₸ {note_text} ({row[5]})\n"
        await query.edit_message_text(message, reply_markup=main_menu())

    elif query.data == "deposit":
        await query.edit_message_text(
            "Enter deposit in the format:\nAmount [Note]",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Back", callback_data='back')]])
        )

    elif query.data == "expense":
        await query.edit_message_text(
            "Choose an expense category:",
            reply_markup=expense_categories_menu()
        )

    elif query.data == "back":
        await query.edit_message_text(
            "You returned to the main menu. Choose an action:",
            reply_markup=main_menu()
        )

# --- Handling category selection ---
async def category_choice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    categories = {
        'cat_food': 'Food',
        'cat_transport': 'Transport',
        'cat_fun': 'Entertainment',
        'cat_other': 'Other'
    }
    context.user_data['category'] = categories[query.data]
    await query.edit_message_text(
        f"You selected category: {categories[query.data]}\n"
        "Enter expense in the format:\nAmount [Note]\n\n"
        "To return to main menu, press the button below.",
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Back", callback_data='back')]])
    )

# --- Handling messages for deposits/expenses ---
async def add_transaction(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.split()
    try:
        amount = float(text[0])
        note = ' '.join(text[1:]) if len(text) > 1 else ''
        date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        if 'category' in context.user_data:  # Expense
            category = context.user_data['category']
            if amount > get_balance():
                await update.message.reply_text("❌ Insufficient funds!", reply_markup=main_menu())
                return
            c.execute(
                "INSERT INTO transactions (type, category, amount, note, date) VALUES (?, ?, ?, ?, ?)",
                ('expense', category, amount, note, date)
            )
            await update.message.reply_text(
                f"✅ Spent: {amount}₸ on {category} {note}\nRemaining balance: {get_balance()}₸",
                reply_markup=main_menu()
            )
            del context.user_data['category']
        else:  # Deposit
            c.execute(
                "INSERT INTO transactions (type, category, amount, note, date) VALUES (?, ?, ?, ?, ?)",
                ('deposit', None, amount, note, date)
            )
            await update.message.reply_text(
                f"✅ Deposit: {amount}₸ {note}\nBalance: {get_balance()}₸",
                reply_markup=main_menu()
            )

        conn.commit()
    except:
        await update.message.reply_text(
            "❌ Error! Use format: Amount [Note]",
            reply_markup=main_menu()
        )

# --- Run bot ---
app = ApplicationBuilder().token("123456789:ABCdefGHIjklMNO_pQrSTUVwxyZ").build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CallbackQueryHandler(button, pattern='^(balance|deposit|expense|show|back)$'))
app.add_handler(CallbackQueryHandler(category_choice, pattern='^cat_'))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, add_transaction))

print("Bot is running with improved buttons...")
app.run_polling()