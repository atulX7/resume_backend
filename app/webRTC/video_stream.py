import cv2
import numpy as np
from fastapi import WebSocket


async def video_stream(websocket: WebSocket):
    """Handles WebRTC video streaming."""
    await websocket.accept()

    while True:
        frame_data = await websocket.receive_bytes()
        frame = np.frombuffer(frame_data, dtype=np.uint8)
        frame = cv2.imdecode(frame, cv2.IMREAD_COLOR)

        # Process frame (e.g., analyze facial expressions)
        processed_frame = frame

        _, encoded_frame = cv2.imencode(".jpg", processed_frame)
        await websocket.send_bytes(encoded_frame.tobytes())
