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
        
        CREATE TABLE IF NOT EXISTS sevimli_fanlar (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            fan TEXT,
            FOREIGN KEY (user_id) REFERENCES users(tg_id)
        );
        
        CREATE TABLE IF NOT EXISTS yutuqlar (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            nomi TEXT,
            tavsif TEXT,
            sana TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(tg_id)
        );
        
        CREATE TABLE IF NOT EXISTS bellashuv (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            boshlagan INTEGER,
            raqib INTEGER,
            fan TEXT,
            savol_soni INTEGER,
            boshlagan_ball INTEGER DEFAULT 0,
            raqib_ball INTEGER DEFAULT 0,
            boshlagan_savol INTEGER DEFAULT 1,
            raqib_savol INTEGER DEFAULT 1,
            boshlagan_joriy_savol TEXT,
            raqib_joriy_savol TEXT,
            holat TEXT DEFAULT 'kutish',
            sana TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)
    
    conn.commit()
    conn.close()
