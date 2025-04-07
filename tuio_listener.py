import pytuio
import socketio
import time

# Connect to the Flask WebSocket server
sio = socketio.Client()
sio.connect("http://localhost:5000")

class MarkerHandler(pytuio.TrackingListener):
    def add_object(self, obj):
        marker_id = obj.symbol_id
        print(f"TUIO Marker detected: {marker_id}")
        sio.emit("marker_detected", {"marker_id": marker_id})

if __name__ == '__main__':
    listener = pytuio.Tracking()
    listener.add_listener(MarkerHandler())
    listener.start()
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        listener.stop()
