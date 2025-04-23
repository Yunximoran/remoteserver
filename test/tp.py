import asyncio
import websockets

async def client():
    uri = "ws://localhost:8000/server/data/realtime"
    async with websockets.connect(
        uri
    ) as websocket:
        # await websocket.send("Hello Server!")
        while True:
            response = await websocket.recv() 
            print(f"Received: {response}")

asyncio.run(client())