# matrix_rain.py — 3D Matrix Code Rain for 500-LED Tree (WS2811 GRB)

import time
import json
import os
import math
import random
import signal
from rpi_ws281x import PixelStrip, Color

running = True
strip = None

def GRB(r, g, b):
    return Color(g, r, b)  # WS2811 uses GRB format

def handle_exit(signum, frame):
    global running
    running = False

# ----------------------------------------------------
# Load LED coordinates
# ----------------------------------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
with open(os.path.join(BASE_DIR, "tree_coords.json")) as f:
    coords = json.load(f)   # list of [x, y, z]

LED_COUNT = len(coords)

# Extract Z (used for falling rain)
zs = [p[2] for p in coords]
z_min, z_max = min(zs), max(zs)
height = z_max - z_min

# Get LED index sorted by descending Z (top to bottom)
sorted_by_z = sorted(range(LED_COUNT), key=lambda i: zs[i], reverse=True)

# ----------------------------------------------------
# Strip configuration
# ----------------------------------------------------
LED_PIN        = 18
LED_FREQ_HZ    = 800000
LED_DMA        = 10
LED_BRIGHTNESS = 255
LED_INVERT     = False
LED_CHANNEL    = 0

# ----------------------------------------------------
# Clear strip
# ----------------------------------------------------
def clear_strip():
    for i in range(LED_COUNT):
        strip.setPixelColor(i, GRB(0,0,0))
    strip.show()

# ----------------------------------------------------
# Matrix Rain Animation
# ----------------------------------------------------
class RainDrop:
    def __init__(self):
        self.reset()

    def reset(self):
        # start above top of tree
        self.pos = z_max + random.uniform(5, 20)
        self.speed = random.uniform(15, 28)     # falling speed
        self.brightness = random.randint(180, 255)
        self.length = random.randint(18, 33)    # green tail length

# ----------------------------------------------------
def matrix_rain_loop(interval=0.015, num_streams=10, fade_factor=0.80):
    """
    interval: time between frames
    num_streams: number of raindrops falling at once
    fade_factor: brightness decay (0.8 = smooth fade)
    """

    drops = [RainDrop() for _ in range(num_streams)]

    # Holds current brightness for each LED
    buffer = [(0,0,0)] * LED_COUNT

    while running:

        # Fade existing buffer
        new_buffer = []
        for (r, g, b) in buffer:
            new_g = int(g * fade_factor)   # only green channel
            new_buffer.append((0, new_g, 0))

        buffer = new_buffer[:]

        # Update each rain stream
        for drop in drops:
            drop.pos -= drop.speed * interval

            # If below bottom → restart
            if drop.pos < z_min - 10:
                drop.reset()

            # Light LEDs in this vertical segment
            for idx in sorted_by_z:
                z = zs[idx]

                if drop.pos - drop.length <= z <= drop.pos:
                    # brighter at drop head, dimmer in tail
                    dist = drop.pos - z
                    t = 1 - (dist / drop.length)
                    g = int(drop.brightness * t)

                    old_r, old_g, old_b = buffer[idx]
                    buffer[idx] = (0, max(old_g, g), 0)

        # Render frame
        for i, (r,g,b) in enumerate(buffer):
            strip.setPixelColor(i, GRB(r,g,b))

        strip.show()
        time.sleep(interval)

# ----------------------------------------------------
# Main
# ----------------------------------------------------
def main():
    global strip

    signal.signal(signal.SIGTERM, handle_exit)
    signal.signal(signal.SIGINT, handle_exit)

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

    clear_strip()

    try:
        matrix_rain_loop(
            interval=0.015,
            num_streams=12,     # more streams = denser matrix rain
            fade_factor=0.78    # lower = longer tails
        )
    finally:
        clear_strip()

if __name__ == "__main__":
    main()
