# candy_cane_motion.py — animated candy cane spiral

import time
import json
import os
import math
import signal
from rpi_ws281x import PixelStrip, Color


# -------------------------
# WS2811 GRB helper
# -------------------------
def GRB(r, g, b):
    return Color(g, r, b)


# -------------------------
# Exit Handling
# -------------------------
running = True
strip = None

def handle_exit(signum, frame):
    global running
    running = False


# -------------------------
# Load LED coordinates
# -------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
with open(os.path.join(BASE_DIR, "tree_coords.json")) as f:
    coords = json.load(f)

LED_COUNT = len(coords)

# Precompute angle & height normalization
thetas = []
z_norms = []

zs = [p[2] for p in coords]
z_min, z_max = min(zs), max(zs)
height = z_max - z_min

for x, y, z in coords:
    thetas.append(math.atan2(y, x))
    z_norms.append((z - z_min) / height)


# -------------------------
# LED Setup
# -------------------------
LED_PIN        = 12
LED_FREQ_HZ    = 800000
LED_DMA        = 10
LED_BRIGHTNESS = 255
LED_INVERT     = False
LED_CHANNEL    = 0


# -------------------------
# Animation Parameters
# -------------------------
STRIPES_PER_HEIGHT = 50       # how many diagonal stripes wrap the tree
ROTATION_SPEED     = 4    # smaller = slower movement
FADE_SHARPNESS     = 10       # higher = cleaner separation between red & white


# -------------------------
# Main Animation Loop
# -------------------------
def main():
    global strip, running

    signal.signal(signal.SIGTERM, handle_exit)
    signal.signal(signal.SIGINT, handle_exit)

    strip = PixelStrip(
        LED_COUNT, LED_PIN, LED_FREQ_HZ,
        LED_DMA, LED_INVERT, LED_BRIGHTNESS, LED_CHANNEL
    )
    strip.begin()

    # Clear garbage startup colors
    for _ in range(2):
        for i in range(LED_COUNT):
            strip.setPixelColor(i, GRB(0,0,0))
        strip.show()
        time.sleep(0.05)

    t = 0

    RED   = (255,0,0)
    WHITE = (255,255,255)

    try:
        while running:
            t += 0.02

            for i in range(LED_COUNT):

                # Spiral: angle + height offset + time shift
                phase = thetas[i] * 3 + z_norms[i] * STRIPES_PER_HEIGHT * math.pi + t * ROTATION_SPEED

                # stripe value oscillates between 0 and 1
                stripe = (math.sin(phase) + 1) / 2

                # make boundaries clean (sharper edges)
                stripe = stripe ** FADE_SHARPNESS

                # blend between red & white
                r = int(RED[0]   * (1-stripe) + WHITE[0] * stripe)
                g = int(RED[1]   * (1-stripe) + WHITE[1] * stripe)
                b = int(RED[2]   * (1-stripe) + WHITE[2] * stripe)

                strip.setPixelColor(i, GRB(r,g,b))

            strip.show()
            time.sleep(0.02)

    finally:
        # turn off gracefully
        for i in range(LED_COUNT):
            strip.setPixelColor(i, GRB(0,0,0))
        strip.show()


if __name__ == "__main__":
    main()
