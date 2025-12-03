# top_to_bottom.py
import time
import json
import os
import signal
from rpi_ws281x import PixelStrip, Color

# -------------------------
# GRB helper
# -------------------------
def GRB(r, g, b):
    return Color(g, r, b)

# -------------------------
# Load coordinates
# -------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
COORDS_JSON = os.path.join(BASE_DIR, "tree_coords.json")

with open(COORDS_JSON, "r") as f:
    coords = json.load(f)

LED_COUNT = len(coords)
ys = [p[1] for p in coords]          # Y coordinate for each LED
y_min, y_max = min(ys), max(ys)
y_range = y_max - y_min

# -------------------------
# LED Strip config
# -------------------------
LED_PIN        = 18
LED_FREQ_HZ    = 800000
LED_DMA        = 10
LED_BRIGHTNESS = 255
LED_INVERT     = False
LED_CHANNEL    = 0

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
    # Band parameters
    # -------------------------
    band_frac = 0.18                # thickness of band as fraction of total height
    band_half = 0.5 * band_frac * y_range

    # start at bottom edge
    pos = y_min + band_half         # center of band
    direction = 1                   # +1 up, -1 down

    # how much to move per frame (in Y units)
    step = y_range / 200.0          # adjust for speed
    frame_delay = 0.02              # seconds

    try:
        while running:
            # move band center
            pos += direction * step

            # reverse direction when band hits top/bottom
            if pos + band_half >= y_max:
                pos = y_max - band_half
                direction = -1
            elif pos - band_half <= y_min:
                pos = y_min + band_half
                direction = 1

            # draw frame: LEDs inside [pos - band_half, pos + band_half] are ON
            low = pos - band_half
            high = pos + band_half

            for i, y in enumerate(ys):
                if low <= y <= high:
                    strip.setPixelColor(i, GRB(255, 255, 255))  # band ON
                else:
                    strip.setPixelColor(i, GRB(0, 0, 0))        # off

            strip.show()
            time.sleep(frame_delay)

    finally:
        clear_strip()

if __name__ == "__main__":
    main()
