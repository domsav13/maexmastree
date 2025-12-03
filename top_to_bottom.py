# top_to_bottom.py
import time
import json
import os
from rpi_ws281x import PixelStrip, Color

running = True  # Flask will set this to False to stop the animation

def GRB(r, g, b):
    return Color(g, r, b)

def run_top_to_bottom():
    global running
    running = True

    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    with open(os.path.join(BASE_DIR, "tree_coords.json")) as f:
        coords = json.load(f)

    LED_COUNT = len(coords)
    
    strip = PixelStrip(LED_COUNT, 18, 800000, 10, False, 255, 0)
    strip.begin()

    while running:
        for i in range(LED_COUNT):
            if not running:
                break
            strip.setPixelColor(i, GRB(255,255,255))
            strip.show()
            time.sleep(0.01)
        
        # clear
        for i in range(LED_COUNT):
            strip.setPixelColor(i, GRB(0,0,0))
        strip.show()

if __name__ == "__main__":
    run_top_to_bottom()
