from fastapi import FastAPI
from fastapi.responses import FileResponse
import uvicorn
import threading
import time

app = FastAPI()

# Shared state
tree_on = False

def led_off():
    print("Turning LEDs OFF")
    # insert your clear_strip() call here

def run_led_loop():
    """Animation loop that runs while tree_on is True."""
    global tree_on
    print("LED loop thread started")

    while tree_on:
        # Example: simple heartbeat
        print("LEDs ON (heartbeat)")
        time.sleep(1)

    led_off()
    print("LED loop thread stopped")

@app.get("/")
def landing_page():
    return FileResponse("index.html")

@app.post("/turn_on")
def turn_on():
    global tree_on
    if not tree_on:
        tree_on = True
        threading.Thread(target=run_led_loop, daemon=True).start()
    return {"status": "ON"}

@app.post("/turn_off")
def turn_off():
    global tree_on
    tree_on = False
    return {"status": "OFF"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
