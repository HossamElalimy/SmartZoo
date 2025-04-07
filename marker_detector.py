import cv2
import cv2.aruco as aruco
import socketio
import time

# SocketIO client
sio = socketio.Client()
sio.connect('http://localhost:5000')

animal_data = {
    0: {"name": "Elephant 🐘", "fact": "Elephants are the largest land animals.", "image": "images/elephant.jpg", "sound": "sounds/elephant.mp3"},
    1: {"name": "Lion 🦁", "fact": "Lions live in groups called prides.", "image": "images/lion.jpg", "sound": "sounds/lion.mp3"},
    2: {"name": "Donkey 🫏", "fact": "Donkeys are strong animals used as working animals.", "image": "images/donkey.jpg", "sound": "sounds/donkey.mp3"},
    3: {"name": "Monkey 🐒", "fact": "Monkeys are intelligent and social animals.", "image": "images/monkey.jpg", "sound": "sounds/monkey.mp3"},
    4: {"name": "Cow 🐄", "fact": "Cows are domesticated animals raised for milk and meat.", "image": "images/cow.jpg", "sound": "sounds/cow.mp3"},
}

cap = cv2.VideoCapture(0)
aruco_dict = aruco.getPredefinedDictionary(aruco.DICT_6X6_250)
parameters = aruco.DetectorParameters()

last_marker_id = None

print("📷 Show a marker to display animal info")

while True:
    ret, frame = cap.read()
    if not ret:
        break

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    corners, ids, _ = aruco.detectMarkers(gray, aruco_dict, parameters=parameters)

    if ids is not None:
        marker_id = int(ids[0][0])
        if marker_id != last_marker_id:
            print(f"🧠 Detected Marker ID: {marker_id}")
            if marker_id in animal_data:
                sio.emit("animal_info", animal_data[marker_id])
                last_marker_id = marker_id

    cv2.imshow("Detector", frame)
    if cv2.waitKey(1) & 0xFF == 27:
        break

cap.release()
cv2.destroyAllWindows()
