# contagion_effect_rgb.py – spherical spreading contagion for 500 LEDs (RGB ORDER)
import time
import random
import math
import os
import json
from rpi_ws281x import PixelStrip, Color

# -----------------------------------------------------
# RGB helper (your strip uses RGB order)
# -----------------------------------------------------
def RGB(r, g, b):
    return Color(r, g, b)

# -----------------------------------------------------
# Load coordinates from JSON
# -----------------------------------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
COORDS_JSON = os.path.join(BASE_DIR, "tree_coords.json")

with open(COORDS_JSON, "r") as f:
    coords = json.load(f)

LED_COUNT = len(coords)
led_coords = coords[:]

print(f"Loaded {LED_COUNT} LED coordinates (RGB strip).")

# -----------------------------------------------------
# LED strip configuration
# -----------------------------------------------------
LED_PIN        = 12
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
# Clear all LEDs
# -----------------------------------------------------
def clear_strip():
    for i in range(LED_COUNT):
        strip.setPixelColor(i, RGB(0, 0, 0))
    strip.show()

# -----------------------------------------------------
# Contagion animation (ONE COLOR ONLY)
# -----------------------------------------------------
def animate_contagious_effect(interval=0.01, contagion_speed=15.0, hold_time=0.4):

    while True:

        # ----------------------------
        # Pick ONE LED and ONE color
        # ----------------------------
        start_idx = random.randrange(LED_COUNT)
        sx, sy, sz = led_coords[start_idx]

        # Bright single color chosen ONCE
        r = random.randint(120, 255)
        g = random.randint(120, 255)
        b = random.randint(120, 255)
        contagion_color = RGB(r, g, b)

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

        spread_duration = max_dist / contagion_speed

        # ----------------------------
        # Expand radius outward
        # ----------------------------
        t0 = time.time()

        while True:
            elapsed = time.time() - t0
            radius = contagion_speed * elapsed

            # no pulsing, no brightness, no flicker
            for idx, d in enumerate(distances):
                if d <= radius:
                    strip.setPixelColor(idx, contagion_color)
                else:
                    strip.setPixelColor(idx, RGB(0, 0, 0))

            strip.show()

            if elapsed >= spread_duration:
                break

            time.sleep(interval)

        # ----------------------------
        # FULL tree on briefly
        # ----------------------------
        for i in range(LED_COUNT):
            strip.setPixelColor(i, contagion_color)
        strip.show()
        time.sleep(hold_time)

        # ----------------------------
        # Reset
        # ----------------------------
        clear_strip()
        time.sleep(0.05)

# -----------------------------------------------------
# Run
# -----------------------------------------------------
if __name__ == "__main__":
    animate_contagious_effect(
        interval=0.01,
        contagion_speed=20.0,   # faster spread
        hold_time=0.4
    )
