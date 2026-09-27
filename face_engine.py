from pathlib import Path
import cv2
import numpy as np
import database

BASE = Path(__file__).parent
FACE_DIR = BASE / "data" / "faces"
MODEL = BASE / "data" / "trainer.yml"
FACE_DIR.mkdir(parents=True, exist_ok=True)

CASCADE = cv2.data.haarcascades + "haarcascade_frontalface_default.xml"

def capture_faces(student_id, sample_count=30):
    camera = cv2.VideoCapture(0)
    if not camera.isOpened():
        raise RuntimeError("Camera could not be opened.")

    detector = cv2.CascadeClassifier(CASCADE)
    count = 0

    while True:
        ok, frame = camera.read()
        if not ok:
            break

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = detector.detectMultiScale(gray, 1.2, 5)

        for x, y, w, h in faces:
            count += 1
            image_path = FACE_DIR / f"User.{student_id}.{count}.jpg"
            cv2.imwrite(str(image_path), gray[y:y+h, x:x+w])

            cv2.rectangle(frame, (x,y), (x+w,y+h), (255,0,0), 2)
            cv2.putText(
                frame, f"Samples: {count}/{sample_count}",
                (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.7,
                (255,255,255), 2
            )

        cv2.imshow("Capture Face - Press Q", frame)

        if cv2.waitKey(50) & 0xFF == ord("q") or count >= sample_count:
            break

    camera.release()
    cv2.destroyAllWindows()

    if count == 0:
        raise RuntimeError("No face detected. Try better lighting.")

    return count

def train_model():
    recognizer = cv2.face.LBPHFaceRecognizer_create()
    images = []
    ids = []

    for path in FACE_DIR.glob("User.*.*.jpg"):
        image = cv2.imread(str(path), cv2.IMREAD_GRAYSCALE)
        if image is None:
            continue

        parts = path.stem.split(".")
        if len(parts) != 3:
            continue

        try:
            student_id = int(parts[1])
        except ValueError:
            continue

        images.append(image)
        ids.append(student_id)

    if not images:
        raise RuntimeError("No face samples found. Register a student first.")

    recognizer.train(images, np.array(ids))
    recognizer.write(str(MODEL))

    return len(images)

def start_attendance():
    if not MODEL.exists():
        raise RuntimeError("Train the model first.")

    recognizer = cv2.face.LBPHFaceRecognizer_create()
    recognizer.read(str(MODEL))

    detector = cv2.CascadeClassifier(CASCADE)
    camera = cv2.VideoCapture(0)

    if not camera.isOpened():
        raise RuntimeError("Camera could not be opened.")

    last_message = "Looking for a registered face..."

    while True:
        ok, frame = camera.read()
        if not ok:
            break

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = detector.detectMultiScale(gray, 1.2, 5)

        for x, y, w, h in faces:
            student_id, confidence = recognizer.predict(gray[y:y+h, x:x+w])

            # LBPH: lower confidence distance = closer match.
            if confidence < 70:
                student = database.get_student(student_id)

                if student:
                    roll_no, name = student
                    added = database.mark_attendance(roll_no, name)

                    if added:
                        last_message = f"Attendance marked: {name}"
                    else:
                        last_message = f"Already marked today: {name}"

                    label = name
                else:
                    label = "Unknown"
            else:
                label = "Unknown"

            cv2.rectangle(frame, (x,y), (x+w,y+h), (0,255,0), 2)
            cv2.putText(
                frame, label, (x, y-10),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0,255,0), 2
            )

        cv2.putText(
            frame, last_message, (10,30),
            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255,255,255), 2
        )
        cv2.putText(
            frame, "Press Q to close", (10,60),
            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255,255,255), 2
        )

        cv2.imshow("Face Recognition Attendance", frame)

        if cv2.waitKey(30) & 0xFF == ord("q"):
            break

    camera.release()
    cv2.destroyAllWindows()
    return last_message
