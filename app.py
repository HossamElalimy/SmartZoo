from flask import Flask, render_template
from flask_socketio import SocketIO, emit
from animal_data import animal_data

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, cors_allowed_origins="*")

@app.route("/")
def index():
    return render_template("index.html")

@socketio.on("marker_detected")
def handle_marker(data):
    marker_id = data.get("marker_id")
    print(f"Received marker: {marker_id}")
    if marker_id in animal_data:
        emit("animal_info", animal_data[marker_id], broadcast=True)
    else:
        print("Unknown marker")

if __name__ == '__main__':
    socketio.run(app, host="0.0.0.0", port=5050)

