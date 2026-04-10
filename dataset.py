import cv2
import time
import sqlite3

# Connect to database
conn = sqlite3.connect("database.db")
cursor = conn.cursor()

# Start camera
cam = cv2.VideoCapture(0)

if not cam.isOpened():
    print("Camera not accessible")
    exit()

face_detector = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')

# Input
numeric_id = int(input("Enter Numeric ID: "))
student_id = input("Enter Roll No: ")
name = input("Enter Name: ")

# 🔹 Check duplicate (by roll number)
cursor.execute("SELECT * FROM students WHERE roll=?", (student_id,))
if cursor.fetchone():
    print("Student already exists!")
    cam.release()
    cv2.destroyAllWindows()
    conn.close()
    exit()

# Instructions
steps = [
    "LOOK STRAIGHT",
    "TURN LEFT",
    "TURN RIGHT",
    "LOOK UP",
    "LOOK DOWN"
]

frames = []
capture_time = 3

print("Follow instructions on screen")

for step in steps:

    start_time = time.time()

    while time.time() - start_time < capture_time:

        ret, img = cam.read()

        if not ret:
            print("Camera error")
            break

        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        faces = face_detector.detectMultiScale(gray, 1.3, 5)

        for (x, y, w, h) in faces:
            cv2.rectangle(img, (x, y), (x+w, y+h), (255, 0, 0), 2)

        # Show instruction
        cv2.putText(img, step, (50, 50),
                    cv2.FONT_HERSHEY_SIMPLEX, 1,
                    (0, 255, 0), 2)

        cv2.imshow('Face Capture', img)

        frames.append(gray)

        if cv2.waitKey(1) & 0xff == 27:
            cam.release()
            cv2.destroyAllWindows()
            conn.close()
            exit()

cam.release()
cv2.destroyAllWindows()

print("Processing images...")

# Save images
count = 0

for frame in frames:
    faces = face_detector.detectMultiScale(frame, 1.3, 5)

    for (x, y, w, h) in faces:
        count += 1

        cv2.imwrite(f"dataset/User.{numeric_id}.{count}.jpg",
                    frame[y:y+h, x:x+w])

        if count >= 30:
            break
    if count >= 30:
        break

# 🔹 Save student ONLY if enough images
if count >= 20:
    cursor.execute("INSERT INTO students VALUES (?, ?, ?)",
                   (numeric_id, student_id, name))
    conn.commit()
    print("Student added successfully")
else:
    print("Not enough images. Try again.")

conn.close()