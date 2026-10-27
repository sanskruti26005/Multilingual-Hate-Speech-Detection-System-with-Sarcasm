# db.py
import mysql.connector
from mysql.connector import Error
import json
from datetime import datetime

# Edit these to match your MySQL/XAMPP settings
DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "",   # <-- set your MySQL root password if you have one
    "port": 3306
}
DB_NAME = "hate_system"

# ---------------------------
# Internal helper to connect (optionally without DB)
# ---------------------------
def _connect(use_db=True):
    cfg = DB_CONFIG.copy()
    if use_db:
        cfg["database"] = DB_NAME
    return mysql.connector.connect(**cfg)

# ---------------------------
# Ensure database and tables exist (run at import)
# ---------------------------
def ensure_database_and_tables():
    try:
        cnx = _connect(use_db=False)
        cursor = cnx.cursor()
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS `{DB_NAME}` DEFAULT CHARACTER SET 'utf8mb4' COLLATE 'utf8mb4_general_ci';")
        cnx.close()
    except Exception as e:
        print("⚠️ Could not create database automatically:", e)

    # Now create tables if missing
    try:
        cnx = _connect(use_db=True)
        cursor = cnx.cursor()
        # users table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INT AUTO_INCREMENT PRIMARY KEY,
            username VARCHAR(150) NOT NULL UNIQUE,
            password VARCHAR(255) NOT NULL,
            display_name VARCHAR(255),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
        """)
        # submissions table: unified for text & image
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS submissions (
            id INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT NOT NULL,
            content_text TEXT NULL,
            image_path VARCHAR(512) NULL,
            prediction VARCHAR(255),
            score FLOAT DEFAULT 0,
            sentiment VARCHAR(50) DEFAULT 'Neutral',
            is_sarcastic TINYINT(1) DEFAULT 0,
            type VARCHAR(20) DEFAULT 'text',
            meta JSON NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
        """)
        cnx.commit()
        cursor.close()
        cnx.close()
    except Exception as e:
        print("⚠️ Could not ensure tables:", e)

# run ensure on import
ensure_database_and_tables()

# ---------------------------
# Public DB helpers
# ---------------------------
def get_connection():
    try:
        return _connect(use_db=True)
    except Error as e:
        print("DB connection error:", e)
        return None

# ---------- Users ----------
def create_user(username, password, display_name=None):
    conn = get_connection()
    if not conn:
        raise RuntimeError("DB connection failed")
    cur = conn.cursor()
    try:
        cur.execute("INSERT INTO users (username, password, display_name) VALUES (%s, %s, %s)",
                    (username, password, display_name))
        conn.commit()
        user_id = cur.lastrowid
        return user_id
    except mysql.connector.IntegrityError:
        raise ValueError("User already exists")
    finally:
        cur.close()
        conn.close()

def authenticate_user(username, password):
    conn = get_connection()
    if not conn:
        return None
    cur = conn.cursor()
    try:
        cur.execute("SELECT id FROM users WHERE username=%s AND password=%s", (username, password))
        row = cur.fetchone()
        if row:
            return row[0]
        return None
    finally:
        cur.close()
        conn.close()

# ---------- Submissions ----------
def add_text_submission(user_id, text, score, prediction, sentiment="Neutral", is_sarcastic=0, meta=None):
    conn = get_connection()
    if not conn:
        return False
    cur = conn.cursor()
    try:
        meta_json = json.dumps(meta) if meta is not None else None
        cur.execute("""
            INSERT INTO submissions (user_id, content_text, prediction, score, sentiment, is_sarcastic, type, meta)
            VALUES (%s, %s, %s, %s, %s, %s, 'text', %s)
        """, (user_id, text, prediction, score, sentiment, int(bool(is_sarcastic)), meta_json))
        conn.commit()
        return True
    finally:
        cur.close()
        conn.close()

def add_image_submission(user_id, image_path, extracted_text, score, prediction, sentiment="Neutral", is_sarcastic=0, meta=None):
    conn = get_connection()
    if not conn:
        return False
    cur = conn.cursor()
    try:
        meta_json = json.dumps(meta) if meta is not None else None
        cur.execute("""
            INSERT INTO submissions (user_id, image_path, content_text, prediction, score, sentiment, is_sarcastic, type, meta)
            VALUES (%s, %s, %s, %s, %s, %s, %s, 'image', %s)
        """, (user_id, image_path, extracted_text, prediction, score, sentiment, int(bool(is_sarcastic)), meta_json))
        conn.commit()
        return True
    finally:
        cur.close()
        conn.close()

def get_user_history(user_id, limit=200):
    conn = get_connection()
    if not conn:
        return []
    cur = conn.cursor(dictionary=True)
    try:
        cur.execute("""
            SELECT id, content_text AS content_text, image_path, prediction, score, sentiment, is_sarcastic, type, meta, created_at
            FROM submissions
            WHERE user_id=%s
            ORDER BY created_at DESC
            LIMIT %s
        """, (user_id, limit))
        rows = cur.fetchall()
        # Convert meta JSON string to Python object
        for r in rows:
            try:
                r["meta"] = json.loads(r["meta"]) if r.get("meta") else None
            except Exception:
                r["meta"] = None
        return rows
    finally:
        cur.close()
        conn.close()     