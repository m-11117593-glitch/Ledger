import sqlite3
from datetime import datetime, timedelta
import pandas as pd
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "expenses.db")

def get_connection():
    """Returns a SQLite connection with row factory configured."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initializes the SQLite database with the expenses table and user_email column."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL,
            description TEXT NOT NULL,
            amount REAL NOT NULL,
            category TEXT NOT NULL,
            user_email TEXT NOT NULL DEFAULT 'demo@ledger.app',
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Check if user_email column exists in existing table (migration check)
    cursor.execute("PRAGMA table_info(expenses)")
    columns = [row["name"] for row in cursor.fetchall()]
    if "user_email" not in columns:
        cursor.execute("ALTER TABLE expenses ADD COLUMN user_email TEXT NOT NULL DEFAULT 'demo@ledger.app'")
        
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_date ON expenses (date)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_category ON expenses (category)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_user ON expenses (user_email)")
    conn.commit()
    conn.close()

def add_expense(date_str: str, description: str, amount: float, category: str, user_email: str = "demo@ledger.app") -> int:
    """Inserts a new expense or income record attached to a user email."""
    conn = get_connection()
    cursor = conn.cursor()
    clean_email = user_email.strip().lower() if user_email else "demo@ledger.app"
    cursor.execute("""
        INSERT INTO expenses (date, description, amount, category, user_email)
        VALUES (?, ?, ?, ?, ?)
    """, (date_str, description.strip(), float(amount), category.strip(), clean_email))
    conn.commit()
    new_id = cursor.lastrowid
    conn.close()
    return new_id

def delete_expense(expense_id: int, user_email: str = None):
    """Deletes an expense or income entry by ID, scoped to user if provided."""
    conn = get_connection()
    cursor = conn.cursor()
    if user_email:
        clean_email = user_email.strip().lower()
        cursor.execute("DELETE FROM expenses WHERE id = ? AND user_email = ?", (expense_id, clean_email))
    else:
        cursor.execute("DELETE FROM expenses WHERE id = ?", (expense_id,))
    conn.commit()
    conn.close()

def get_expenses(period: str = "All Time", user_email: str = None) -> pd.DataFrame:
    """
    Fetches transactions filtered by the specified period and user_email:
    - 'This Week': from Monday of the current week to today
    - 'This Month': from the 1st of the current month to today
    - 'All Time': all records
    """
    conn = get_connection()
    today = datetime.now().date()
    clean_email = user_email.strip().lower() if user_email else None
    
    where_clauses = []
    params = []
    
    if clean_email:
        where_clauses.append("user_email = ?")
        params.append(clean_email)
        
    if period == "This Week":
        start_date = (today - timedelta(days=today.weekday())).strftime("%Y-%m-%d")
        where_clauses.append("date >= ?")
        params.append(start_date)
    elif period == "This Month":
        start_date = today.replace(day=1).strftime("%Y-%m-%d")
        where_clauses.append("date >= ?")
        params.append(start_date)
        
    where_sql = ("WHERE " + " AND ".join(where_clauses)) if where_clauses else ""
    query = f"SELECT * FROM expenses {where_sql} ORDER BY date DESC, id DESC"

    df = pd.read_sql_query(query, conn, params=params)
    conn.close()
    return df

def get_summary_stats(df: pd.DataFrame) -> dict:
    """
    Computes cash flow metrics, separating Income (money gained)
    from Outflow/Expenses (money spent).
    """
    if df.empty:
        return {
            "total_income": 0.0,
            "total_spent": 0.0,
            "net_savings": 0.0,
            "transaction_count": 0,
            "expense_count": 0,
            "average_spent": 0.0,
            "top_category": "None",
            "top_category_amount": 0.0,
            "top_category_pct": 0.0,
            "category_summary": pd.DataFrame(columns=["category", "amount", "percentage"]),
            "timeline_summary": pd.DataFrame(columns=["date", "expenses", "income"])
        }
    
    # Split into Income (inflow) vs Expenses (outflow)
    df_income = df[df["category"].str.strip().str.lower() == "income"]
    df_expenses = df[df["category"].str.strip().str.lower() != "income"]
    
    total_income = float(df_income["amount"].sum())
    total_spent = float(df_expenses["amount"].sum())
    net_savings = total_income - total_spent
    
    transaction_count = int(len(df))
    expense_count = int(len(df_expenses))
    average_spent = float(total_spent / expense_count) if expense_count > 0 else 0.0
    
    # Top spending category (computed strictly across actual expenses, NOT income)
    if not df_expenses.empty:
        cat_grp = df_expenses.groupby("category")["amount"].sum().reset_index()
        cat_grp = cat_grp.sort_values(by="amount", ascending=False)
        cat_grp["percentage"] = (cat_grp["amount"] / total_spent * 100).round(1) if total_spent > 0 else 0.0
        
        top_cat_row = cat_grp.iloc[0]
        top_category = str(top_cat_row["category"])
        top_category_amount = float(top_cat_row["amount"])
        top_category_pct = float(top_cat_row["percentage"])
    else:
        cat_grp = pd.DataFrame(columns=["category", "amount", "percentage"])
        top_category = "None"
        top_category_amount = 0.0
        top_category_pct = 0.0
        
    # Timeline breakdown with both expenses and income per date
    all_dates = sorted(list(df["date"].unique()))
    timeline_rows = []
    for d in all_dates:
        day_exp = float(df_expenses[df_expenses["date"] == d]["amount"].sum()) if not df_expenses.empty else 0.0
        day_inc = float(df_income[df_income["date"] == d]["amount"].sum()) if not df_income.empty else 0.0
        timeline_rows.append({"date": d, "expenses": day_exp, "income": day_inc})
    
    timeline_df = pd.DataFrame(timeline_rows) if timeline_rows else pd.DataFrame(columns=["date", "expenses", "income"])
    
    return {
        "total_income": total_income,
        "total_spent": total_spent,
        "net_savings": net_savings,
        "transaction_count": transaction_count,
        "expense_count": expense_count,
        "average_spent": average_spent,
        "top_category": top_category,
        "top_category_amount": top_category_amount,
        "top_category_pct": top_category_pct,
        "category_summary": cat_grp,
        "timeline_summary": timeline_df
    }
