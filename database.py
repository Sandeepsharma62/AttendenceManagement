import mysql.connector
from mysql.connector import Error

DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "BabuL0har@2026",
    "database": "face_attendance"
}

def get_connection():
    return mysql.connector.connect(**DB_CONFIG)

def add_student(roll_no, name):
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO students (roll_no, name) VALUES (%s, %s)",
            (roll_no, name)
        )
        conn.commit()
        return cur.lastrowid
    finally:
        conn.close()

def get_student(student_id):
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute(
            "SELECT roll_no, name FROM students WHERE id=%s",
            (student_id,)
        )
        return cur.fetchone()
    finally:
        conn.close()

def get_all_attendance():
    conn = get_connection()
    try:
        cur = conn.cursor(dictionary=True)
        cur.execute("""
            SELECT roll_no, name, attendance_date, attendance_time
            FROM attendance
            ORDER BY attendance_date DESC, attendance_time DESC
        """)
        return cur.fetchall()
    finally:
        conn.close()

def mark_attendance(roll_no, name):
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute("""
            INSERT IGNORE INTO attendance
            (roll_no, name, attendance_date, attendance_time)
            VALUES (%s, %s, CURDATE(), CURTIME())
        """, (roll_no, name))
        conn.commit()
        return cur.rowcount == 1
    finally:
        conn.close()
