# contagion_effect.py – spherical spreading contagion for 500 LEDs
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
# Load coordinates from JSON (500 LEDs)
# -----------------------------------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
COORDS_JSON = os.path.join(BASE_DIR, "tree_coords.json")

with open(COORDS_JSON, "r") as f:
    coords = json.load(f)   # list of [x,y,z]

LED_COUNT = len(coords)
led_coords = coords[:]      # nice alias

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
# Clear all LEDs
# -----------------------------------------------------
def clear_strip():
    for i in range(LED_COUNT):
        strip.setPixelColor(i, GRB(0,0,0))
    strip.show()

# -----------------------------------------------------
# Main contagion animation
# -----------------------------------------------------
def animate_contagious_effect(interval=0.01, contagion_speed=10.0, hold_time=0.5):
    """
    Picks a random LED, random color, spreads outward until full tree is lit.
    """
    while True:

        # ----------------------------
        # Choose starting LED + color
        # ----------------------------
        start_idx = random.randrange(LED_COUNT)
        sx, sy, sz = led_coords[start_idx]

        # strong, bright, vibrant color set
        r = random.randint(150, 255)
        g = random.randint(150, 255)
        b = random.randint(150, 255)

        contagion_color = GRB(r, g, b)

        # ----------------------------
        # Compute distances from seed
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
        # Spread outward
        # ----------------------------
        t0 = time.time()
        while True:
            elapsed = time.time() - t0
            radius  = contagion_speed * elapsed

            clear_strip()

            # light LEDs that fall within the growing radius
            for idx, d in enumerate(distances):
                if d <= radius:
                    strip.setPixelColor(idx, contagion_color)

            strip.show()

            if elapsed >= spread_duration:
                break

            time.sleep(interval)

        # ----------------------------
        # Hold full-color tree
        # ----------------------------
        for i in range(LED_COUNT):
            strip.setPixelColor(i, contagion_color)
        strip.show()
        time.sleep(hold_time)

        # ----------------------------
        # Clear before repeating
        # ----------------------------
        clear_strip()
        time.sleep(0.02)


# -----------------------------------------------------
# Run if called directly
# -----------------------------------------------------
if __name__ == "__main__":
    animate_contagious_effect(
        interval=0.01,
        contagion_speed=9.5,
        hold_time=0.5
    )
