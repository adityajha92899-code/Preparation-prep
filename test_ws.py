import asyncio
import json
import websockets

async def main():
    uri = "ws://127.0.0.1:8000/ws/test_user"
    async with websockets.connect(uri) as ws:
        await ws.send(json.dumps({"message":"Explain sliding window","user_id":"test_user"}))
        resp = await ws.recv()
        print(resp)

if __name__ == '__main__':
    asyncio.run(main())
