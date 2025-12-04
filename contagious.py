# contagion_effect_fixed.py – smooth non-blinking contagion spread for 500 LEDs (WS2811 GRB)

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
print(f"Loaded {LED_COUNT} LED coordinates.")

# -----------------------------------------------------
# LED setup
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
# Utilities
# -----------------------------------------------------
def clear_strip():
    for i in range(LED_COUNT):
        strip.setPixelColor(i, GRB(0,0,0))
    strip.show()

# Pre-store LED coordinates as tuples for speed
led_coords = [tuple(p) for p in coords]

# -----------------------------------------------------
# FIXED Contagion Animation
# -----------------------------------------------------
def animate_contagious_effect(interval=0.01, contagion_speed=10.0, hold_time=0.5):
    """
    Perfect smooth contagious expansion:
    - No flicker at boundary
    - No destructive clear every frame
    - Full fill -> hold -> reset
    """

    while True:

        # ----------------------------
        # Choose starting LED + bright random color
        # ----------------------------
        start_idx = random.randrange(LED_COUNT)
        sx, sy, sz = led_coords[start_idx]

        r = random.randint(170, 255)
        g = random.randint(170, 255)
        b = random.randint(170, 255)
        contagion_color = GRB(r, g, b)

        # ----------------------------
        # Compute all distances once
        # ----------------------------
        distances = []
        max_dist = 0.0

        for (x, y, z) in led_coords:
            d = math.dist((sx, sy, sz), (x, y, z))
            distances.append(d)
            if d > max_dist:
                max_dist = d

        # ----------------------------
        # Clear once at start
        # ----------------------------
        clear_strip()

        # ----------------------------
        # Expand contagion
        # ----------------------------
        t0 = time.time()

        while True:
            elapsed = time.time() - t0
            radius  = contagion_speed * elapsed

            # Cap radius to avoid overshooting max_dist
            if radius > max_dist:
                radius = max_dist

            # Set LEDs inside radius ON one time only
            for idx, d in enumerate(distances):
                if d <= radius:
                    strip.setPixelColor(idx, contagion_color)

            strip.show()

            # If radius fully covers the tree → stop immediately
            if radius >= max_dist:
                break

            time.sleep(interval)

        # ----------------------------
        # Hold full tree
        # ----------------------------
        time.sleep(hold_time)

        # ----------------------------
        # Clear for next cycle
        # ----------------------------
        clear_strip()
        time.sleep(0.05)

# -----------------------------------------------------
# Main
# -----------------------------------------------------
if __name__ == "__main__":
    animate_contagious_effect(
        interval=0.01,
        contagion_speed=9.5,
        hold_time=0.6
    )
