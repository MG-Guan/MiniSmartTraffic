from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse
from picamera2 import Picamera2
import cv2
import threading
import asyncio
import numpy as np
import base64
import io
import logging
import httpx
from fastapi import HTTPException

# Set up logger
logger = logging.getLogger("video_stream")
logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)
UTILITY_API_URL = "http://104.168.34.100:5555/v1/image/alpr"

async def get_plate(image_bytes: bytes) -> str:
    """
    accept JPEG bytes directly
    Returns recognized plate or empty string on failure
    """
    try:
        # Encode to base64
        image_b64 = base64.b64encode(image_bytes).decode('utf-8')
        
        # Send to license plate recognition API
        async with httpx.AsyncClient(timeout=2.0) as client:
            response = await client.post(
                UTILITY_API_URL,
                files={"upload": ("plate.jpg", image_bytes, "image/jpeg")}
            )
        
        # Handle response
        if response.status_code != 200:
            logger.error(f"Utility API error: {response.status_code} - {response.text}")
            return ""
            
        predictions = response.json().get("predictions", [])
        if not predictions:
            logger.info("No license plates detected")
            return ""
            
        return predictions[0].get("plate", "")
        
    except Exception as e:
        logger.error(f"Plate recognition error: {str(e)}")
        return ""


app = FastAPI()

# Initialize camera
picam2 = Picamera2()
config = picam2.create_video_configuration(
    main={"size": (640, 480)},
    controls={"FrameRate": 30}
)
picam2.configure(config)
picam2.start()

# Thread-safe frame buffer
class FrameBuffer:
    def __init__(self):
        self.frame = None
        self.lock = threading.Lock()
    
    def update(self, frame):
        with self.lock:
            self.frame = frame
    
    def get_frame(self):
        with self.lock:
            return self.frame

frame_buffer = FrameBuffer()

# Camera capture thread
def capture_frames():
    while True:
        frame = picam2.capture_array()
        frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
        frame_buffer.update(frame)

capture_thread = threading.Thread(target=capture_frames, daemon=True)
capture_thread.start()

# MJPEG streaming endpoint
async def generate_mjpeg():
    """Generate MJPEG stream with integrated plate recognition"""
    frame_count = 0
    recognition_interval = 30  # Process every 30 frames (~1/sec at 30fps)
    
    while True:
        frame = frame_buffer.get_frame()
        if frame is None:
            await asyncio.sleep(0.01)
            continue
            
        # Encode frame to JPEG
        _, jpeg = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 85])
        jpeg_bytes = jpeg.tobytes()
        
        # Run plate recognition periodically
        if frame_count % recognition_interval == 0:
            logger.info("detection")
            plate = await get_plate(jpeg_bytes)
            if plate:
                logger.info(f"Detected license plate: {plate}")
            # Else: Errors already logged in get_plate()
        
        # Yield MJPEG frame
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + 
               jpeg_bytes + b'\r\n')
        
        frame_count += 1
        await asyncio.sleep(0.033)  # Maintain ~30 FPS

@app.get("/video_feed")
async def video_feed():
    return StreamingResponse(
        generate_mjpeg(),
        media_type="multipart/x-mixed-replace; boundary=frame"
    )

@app.get("/")
async def root():
    return {"message": "Connect to /video_feed for streaming"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)