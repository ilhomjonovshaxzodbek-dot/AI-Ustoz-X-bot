import sqlite3

def get_db():
    conn = sqlite3.connect("bot.db")
    conn.row_factory = sqlite3.Row
    return conn

def create_tables():
    conn = get_db()
    cur = conn.cursor()
    
    cur.executescript("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            tg_id INTEGER UNIQUE,
            name TEXT,
            lang TEXT DEFAULT 'uz',
            sinf TEXT,
            type TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        
        CREATE TABLE IF NOT EXISTS masalalar (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            masala TEXT,
            javob TEXT,
            togri INTEGER DEFAULT 0,
            sana TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(tg_id)
        );
        
        CREATE TABLE IF NOT EXISTS testlar (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            savol TEXT,
            togri INTEGER DEFAULT 0,
            sana TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(tg_id)
        );
        
        CREATE TABLE IF NOT EXISTS eslatmalar (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER UNIQUE,
            vaqt TEXT,
            active INTEGER DEFAULT 1,
            FOREIGN KEY (user_id) REFERENCES users(tg_id)
        );
        
        CREATE TABLE IF NOT EXISTS kunlik_masalalar (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            masala TEXT,
            sana DATE DEFAULT (date('now')),
            FOREIGN KEY (user_id) REFERENCES users(tg_id)
        );
    """)
    
    conn.commit()
    conn.close()
