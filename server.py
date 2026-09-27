from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
from pathlib import Path
import json
import threading
import csv

import database
import face_engine

ROOT = Path(__file__).parent
WEB = ROOT / "web"

class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(WEB), **kwargs)

    def send_json(self, data, status=200):
        body = json.dumps(data, default=str).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        path = urlparse(self.path).path

        if path == "/api/attendance":
            try:
                self.send_json({"success": True, "data": database.get_all_attendance()})
            except Exception as e:
                self.send_json({"success": False, "message": str(e)}, 500)
            return

        if path == "/api/export":
            try:
                rows = database.get_all_attendance()
                output = ROOT / "attendance_export.csv"
                with output.open("w", newline="", encoding="utf-8") as f:
                    writer = csv.writer(f)
                    writer.writerow(["Roll No", "Name", "Date", "Time"])
                    for row in rows:
                        writer.writerow([
                            row["roll_no"], row["name"],
                            row["attendance_date"], row["attendance_time"]
                        ])
                self.send_response(200)
                self.send_header("Content-Type", "text/csv")
                self.send_header("Content-Disposition", 'attachment; filename="attendance_export.csv"')
                data = output.read_bytes()
                self.send_header("Content-Length", str(len(data)))
                self.end_headers()
                self.wfile.write(data)
            except Exception as e:
                self.send_json({"success": False, "message": str(e)}, 500)
            return

        super().do_GET()

    def do_POST(self):
        path = urlparse(self.path).path

        if path not in ["/api/register", "/api/train", "/api/start"]:
            self.send_json({"success": False, "message": "Not found"}, 404)
            return

        try:
            if path == "/api/register":
                length = int(self.headers.get("Content-Length", 0))
                payload = json.loads(self.rfile.read(length).decode("utf-8"))
                name = payload.get("name", "").strip()
                roll_no = payload.get("roll_no", "").strip()

                if not name or not roll_no:
                    self.send_json({"success": False, "message": "Name and roll number are required."}, 400)
                    return

                student_id = database.add_student(roll_no, name)
                samples = face_engine.capture_faces(student_id)
                self.send_json({
                    "success": True,
                    "message": f"{name} registered and {samples} face samples captured."
                })
                return

            if path == "/api/train":
                samples = face_engine.train_model()
                self.send_json({
                    "success": True,
                    "message": f"Model trained using {samples} face samples."
                })
                return

            if path == "/api/start":
                # Run camera outside the browser request thread so the server remains responsive.
                def worker():
                    try:
                        face_engine.start_attendance()
                    except Exception as e:
                        print("Attendance error:", e)

                threading.Thread(target=worker, daemon=True).start()
                self.send_json({
                    "success": True,
                    "message": "Camera started. Use the camera window and press Q to close it."
                })
                return

        except Exception as e:
            self.send_json({"success": False, "message": str(e)}, 500)

if __name__ == "__main__":
    print("Server running at http://localhost:8000")
    ThreadingHTTPServer(("localhost", 8000), Handler).serve_forever()
