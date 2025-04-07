import asyncio
import websockets
import json

connected = set()

async def handler(websocket):
    connected.add(websocket)
    try:
        async for _ in websocket:
            pass  # ignore client messages
    finally:
        connected.remove(websocket)

async def send_data_to_all(data):
    message = json.dumps(data)
    await asyncio.gather(*(ws.send(message) for ws in connected if ws.open))

async def main():
    print("🌐 WebSocket server running on ws://localhost:8765")
    async with websockets.serve(handler, "localhost", 8765):
        await asyncio.Future()

if __name__ == "__main__":
    asyncio.run(main())
