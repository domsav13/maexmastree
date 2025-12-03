# top_to_bottom.py
import time
import json
import os
from rpi_ws281x import PixelStrip, Color
import signal

# -------------------------
# GRB helper
# -------------------------
def GRB(r, g, b):
    return Color(g, r, b)

# -------------------------
# Load coordinates (for LED_COUNT)
# -------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
COORDS_JSON = os.path.join(BASE_DIR, "tree_coords.json")

with open(COORDS_JSON, "r") as f:
    coords = json.load(f)

LED_COUNT = len(coords)

# -------------------------
# Strip config
# -------------------------
LED_PIN        = 18
LED_FREQ_HZ    = 800000
LED_DMA        = 10
LED_BRIGHTNESS = 255
LED_INVERT     = False
LED_CHANNEL    = 0

# global strip reference so we can clean up on signal
strip = None
running = True

def handle_exit(signum, frame):
    global running
    running = False

def clear_strip():
    if strip is None:
        return
    for i in range(LED_COUNT):
        strip.setPixelColor(i, GRB(0, 0, 0))
    strip.show()

def main():
    global strip, running

    # set up signal handlers so SIGTERM from Flask stops cleanly
    signal.signal(signal.SIGINT, handle_exit)
    signal.signal(signal.SIGTERM, handle_exit)

    # init strip
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
    # Precompute vertical order (by Y coordinate)
    # -------------------------
    # coords[i] = (x, y, z) → use y (index 1) as vertical axis
    indices_bottom_to_top = sorted(
        range(LED_COUNT),
        key=lambda i: coords[i][1]  # sort by Y
    )
    indices_top_to_bottom = list(reversed(indices_bottom_to_top))

    try:
        while running:
            # ensure strip is clear before each cycle
            clear_strip()

            # bottom -> top: turn on by increasing Y
            for idx in indices_bottom_to_top:
                if not running:
                    break
                strip.setPixelColor(idx, GRB(255, 255, 255))
                strip.show()
                time.sleep(0.01)

            if not running:
                break
            time.sleep(0.2)

            # top -> bottom: turn off by decreasing Y
            for idx in indices_top_to_bottom:
                if not running:
                    break
                strip.setPixelColor(idx, GRB(0, 0, 0))
                strip.show()
                time.sleep(0.005)

            if not running:
                break
            time.sleep(0.2)

    finally:
        clear_strip()

if __name__ == "__main__":
    main()
