import socket
import json

animal_data = {
    0: ("Elephant 🐘", "Elephants are the largest land animals."),
    1: ("Lion 🦁", "Lions live in groups called prides."),
    2: ("Donkey 🫏", "Donkeys are strong animals used as working animals."),
    3: ("Monkey 🐒", "Monkeys are intelligent and social animals."),
    4: ("Cow 🐄", "Cows are domesticated animals raised for milk and meat.")
}

HOST = 'localhost'
PORT = 9999

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.bind((HOST, PORT))
    s.listen()
    print("📡 Socket server running on port 9999...")

    conn, addr = s.accept()
    with conn:
        print(f"🟢 Connected by {addr}")
        while True:
            marker_id = input("Enter marker ID (0-4): ")
            if marker_id.isdigit():
                marker_id = int(marker_id)
                name, fact = animal_data.get(marker_id, ("Unknown ❓", "No info available."))
                msg = json.dumps({"name": name, "fact": fact})
                conn.sendall(msg.encode('utf-8'))
