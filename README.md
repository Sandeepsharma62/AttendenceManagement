# Face Recognition Attendance System (No Flask)

Tech used:
- Python
- OpenCV + LBPH face recognition
- MySQL
- HTML
- CSS
- JavaScript
- Python built-in HTTP server (`http.server`) — Flask is NOT used.

## 1. MySQL setup

Open MySQL Workbench and run:

CREATE DATABASE face_attendance;
USE face_attendance;

CREATE TABLE students (
    id INT AUTO_INCREMENT PRIMARY KEY,
    roll_no VARCHAR(50) UNIQUE NOT NULL,
    name VARCHAR(100) NOT NULL
);

CREATE TABLE attendance (
    id INT AUTO_INCREMENT PRIMARY KEY,
    roll_no VARCHAR(50) NOT NULL,
    name VARCHAR(100) NOT NULL,
    attendance_date DATE NOT NULL,
    attendance_time TIME NOT NULL,
    UNIQUE KEY one_attendance_per_day (roll_no, attendance_date)
);

Then open `database.py` and change:
DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "YOUR_MYSQL_PASSWORD",
    "database": "face_attendance"
}

## 2. Install

Open the project in VS Code Terminal:

python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt

## 3. Run

python server.py

Then open:
http://localhost:8000

## 4. Workflow

1. Enter name and roll number on the website.
2. Click Register & Capture Face.
3. A camera window opens and captures face samples.
4. Click Train Model.
5. Click Start Attendance.
6. The camera recognizes registered faces and saves attendance in MySQL.
7. Dashboard displays attendance records.
8. Export CSV downloads the attendance table.

## Important
This is an educational prototype. Face recognition can make mistakes, so it should not be treated as a high-security biometric system.
