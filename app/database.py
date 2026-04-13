import sqlite3
import os
from datetime import datetime

DB_PATH = "data/scraping_history.db"

def get_db_connection():
    """Koneksi ke database SQLite"""
    os.makedirs("data", exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Buat tabel jika belum ada"""
    conn = get_db_connection()
    conn.execute('''
        CREATE TABLE IF NOT EXISTS scraping_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            keyword TEXT NOT NULL,
            leads_count INTEGER,
            filename TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

def save_to_history(keyword, leads_count, filename):
    """Simpan history scraping"""
    conn = get_db_connection()
    conn.execute(
        "INSERT INTO scraping_history (keyword, leads_count, filename) VALUES (?, ?, ?)",
        (keyword, leads_count, filename)
    )
    conn.commit()
    conn.close()

def get_history(limit=50):
    """Ambil history terbaru"""
    conn = get_db_connection()
    history = conn.execute(
        "SELECT * FROM scraping_history ORDER BY created_at DESC LIMIT ?",
        (limit,)
    ).fetchall()
    conn.close()
    return history

def delete_history_item(id):
    """Hapus satu history"""
    conn = get_db_connection()
    conn.execute("DELETE FROM scraping_history WHERE id = ?", (id,))
    conn.commit()
    conn.close()

def get_total_stats():
    """Dapatkan statistik total"""
    conn = get_db_connection()
    total_leads = conn.execute("SELECT SUM(leads_count) as total FROM scraping_history").fetchone()
    total_scrapes = conn.execute("SELECT COUNT(*) as count FROM scraping_history").fetchone()
    conn.close()
    return {
        'total_leads': total_leads['total'] or 0,
        'total_scrapes': total_scrapes['count'] or 0
    }