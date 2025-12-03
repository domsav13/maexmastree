# top_to_bottom.py  (vertical band sweep)
import time
import json
import os
import signal
from rpi_ws281x import PixelStrip, Color
import math

running = True
strip = None

def GRB(r, g, b):
    return Color(g, r, b)

def handle_exit(signum, frame):
    global running
    running = False

# -------------------------
# Load coordinates
# -------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
with open(os.path.join(BASE_DIR, "tree_coords.json")) as f:
    coords = json.load(f)

LED_COUNT = len(coords)
ys = [p[1] for p in coords]     # y-coordinates of each LED
y_min, y_max = min(ys), max(ys)

# -------------------------
# LED Strip Config
# -------------------------
LED_PIN        = 18
LED_FREQ_HZ    = 800000
LED_DMA        = 10
LED_BRIGHTNESS = 255
LED_INVERT     = False
LED_CHANNEL    = 0

def clear_strip():
    if strip:
        for i in range(LED_COUNT):
            strip.setPixelColor(i, GRB(0, 0, 0))
        strip.show()

def main():
    global running, strip

    signal.signal(signal.SIGINT, handle_exit)
    signal.signal(signal.SIGTERM, handle_exit)

    strip = PixelStrip(
        LED_COUNT,
        LED_PIN,
        LED_FREQ_HZ,
        LED_DMA,
        LED_INVERT,
        LED_BRIGHTNESS,
        LED_CHANNEL
    )
    strip.begin()

    # -------------------------
    # Animation parameters
    # -------------------------
    band_height = (y_max - y_min) * 0.18   # thickness of the light band
    speed = 0.015                           # delay between frames
    direction = 1                           # +1 = up, -1 = down
    position = y_min                        # current vertical position

    try:
        while running:

            # Move the band
            position += direction * 0.8  # speed of vertical movement

            # Reverse at bounds
            if position + band_height > y_max:
                direction = -1
            elif position < y_min:
                direction = 1

            # Render frame
            for i, y in enumerate(ys):
                inside = (position <= y <= position + band_height)
                if inside:
                    strip.setPixelColor(i, GRB(255, 255, 255))  # bright white band
                else:
                    strip.setPixelColor(i, GRB(0, 0, 0))         # off

            strip.show()
            time.sleep(speed)

    finally:
        clear_strip()


if __name__ == "__main__":
    main()
