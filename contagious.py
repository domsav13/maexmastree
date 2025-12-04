# contagion_effect_fast_singlecolor.py – smooth fast contagion spread (WS2811 GRB)

import time
import random
import math
import os
import json
from rpi_ws281x import PixelStrip, Color

# -----------------------------------------------------
# GRB helper (WS2811 uses GRB order)
# -----------------------------------------------------
def GRB(r, g, b):
    return Color(g, r, b)

# -----------------------------------------------------
# Load coordinates
# -----------------------------------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
with open(os.path.join(BASE_DIR, "tree_coords.json")) as f:
    coords = json.load(f)

LED_COUNT = len(coords)
led_coords = [tuple(p) for p in coords]

print(f"Loaded {LED_COUNT} LED coordinates.")

# -----------------------------------------------------
# LED strip configuration
# -----------------------------------------------------
LED_PIN        = 18
LED_FREQ_HZ    = 800000
LED_DMA        = 10
LED_BRIGHTNESS = 255
LED_INVERT     = False
LED_CHANNEL    = 0

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

# -----------------------------------------------------
# Clear ALL LEDs
# -----------------------------------------------------
def clear_strip():
    for i in range(LED_COUNT):
        strip.setPixelColor(i, GRB(0,0,0))
    strip.show()

# -----------------------------------------------------
# Contagion animation
# -----------------------------------------------------
def animate_contagious_effect(interval=0.008, contagion_speed=14.0, hold_time=0.5):
    """
    Smooth, single-color contagion spread.
    Faster spread speed. No pulsing. No flicker.
    """

    while True:

        # ----------------------------
        # 1. Choose seed + single color
        # ----------------------------
        start_idx = random.randrange(LED_COUNT)
        sx, sy, sz = led_coords[start_idx]

        # ONE color per entire spread (choose new each cycle)
        r = random.randint(170, 255)
        g = random.randint(170, 255)
        b = random.randint(170, 255)
        contagion_color = GRB(r, g, b)

        # ----------------------------
        # 2. Precompute distances
        # ----------------------------
        distances = []
        max_dist = 0.0

        for (x, y, z) in led_coords:
            d = math.dist((sx, sy, sz), (x, y, z))
            distances.append(d)
            if d > max_dist:
                max_dist = d

        # clear once
        clear_strip()

        # ----------------------------
        # 3. Expand contagion
        # ----------------------------
        t0 = time.time()

        while True:
            elapsed = time.time() - t0
            radius = contagion_speed * elapsed

            if radius > max_dist:
                radius = max_dist

            # Light LEDs inside radius
            for idx, d in enumerate(distances):
                if d <= radius:
                    strip.setPixelColor(idx, contagion_color)

            strip.show()

            # Stop spread immediately when full
            if radius >= max_dist:
                break

            time.sleep(interval)

        # ----------------------------
        # 4. Hold full tree
        # ----------------------------
        time.sleep(hold_time)

        # ----------------------------
        # 5. Reset for next color cycle
        # ----------------------------
        clear_strip()
        time.sleep(0.03)


# -----------------------------------------------------
# Main
# -----------------------------------------------------
if __name__ == "__main__":
    animate_contagious_effect(
        interval=0.008,     # faster frame rate
        contagion_speed=14, # faster radius growth
        hold_time=0.5
    )
