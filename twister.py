"""
Snowstorm Vortex Effect for a 3D LED Tree
- Uses icy, vibrant snow-like colors (not white or full rainbow)
- Sparkles and fluctuates as LEDs swirl in a helix pattern
- Works with 500 LEDs from tree_coords.json
"""

import os
import time
import math
import argparse
import json
from rpi_ws281x import PixelStrip, Color
import colorsys
import random

# -------------------------------------------------------
# ARGUMENTS
# -------------------------------------------------------
parser = argparse.ArgumentParser(description="Snowstorm Vortex for 3D LED Tree")
parser.add_argument("-i", "--interval", type=float, default=0.035,
                    help="Seconds between frames")
parser.add_argument("-r", "--rotations-per-sec", type=float, default=0.25,
                    help="Full helix rotations per second")
parser.add_argument("-t", "--turns", type=float, default=3.5,
                    help="Helix turns bottom→top")
parser.add_argument("--reverse", action="store_true",
                    help="Rotate backwards")
parser.add_argument("--range", type=float, default=1.0,
                    help="Z range to animate (0–1)")
args = parser.parse_args()

INTERVAL         = args.interval
RPS              = args.rotations_per_sec
HELIX_TURNS      = args.turns
REVERSE          = -1.0 if args.reverse else 1.0
Z_RANGE_FRACTION = max(0.0, min(1.0, args.range))

# -------------------------------------------------------
# LOAD COORDINATES
# -------------------------------------------------------
BASE_DIR     = os.path.dirname(os.path.abspath(__file__))
COORDS_JSON  = os.path.join(BASE_DIR, "tree_coords.json")

with open(COORDS_JSON, "r") as f:
    positions = json.load(f)

LED_COUNT = len(positions)
print(f"Loaded {LED_COUNT} 3D positions.")

# -------------------------------------------------------
# HELPERS (GRB + snow colors)
# -------------------------------------------------------
def GRB(r, g, b):
    return Color(g, r, b)

def icy_color(hue):
    """
    Generate icy snow colors:
    - hues around blue/cyan/violet
    - high brightness
    - soft saturation for pastel snow look
    """
    h = hue % 1.0
    s = 0.20 + random.random() * 0.25    # low sat = frosty
    v = 0.60 + random.random() * 0.40    # bright + shimmering
    r, g, b = colorsys.hsv_to_rgb(h, s, v)
    return GRB(int(r*255), int(g*255), int(b*255))

# -------------------------------------------------------
# PRECOMPUTE THETA + NORMALIZED HEIGHT
# -------------------------------------------------------
zs = [p[2] for p in positions]
z_min, z_max = min(zs), max(zs)
z_height = z_max - z_min

led_theta = []
led_znorm = []

for (x, y, z) in positions:
    theta = math.atan2(y, x)
    z_norm = (z - z_min) / z_height if z_height > 0 else 0.0
    z_norm *= Z_RANGE_FRACTION

    led_theta.append(theta)
    led_znorm.append(z_norm)

# -------------------------------------------------------
# STRIP SETUP
# -------------------------------------------------------
LED_PIN        = 18
LED_FREQ_HZ    = 800000
LED_DMA        = 10
LED_BRIGHTNESS = 255
LED_INVERT     = False
LED_CHANNEL    = 0

strip = PixelStrip(
    LED_COUNT, LED_PIN, LED_FREQ_HZ,
    LED_DMA, LED_INVERT, LED_BRIGHTNESS, LED_CHANNEL
)
strip.begin()

def clear_strip():
    for i in range(LED_COUNT):
        strip.setPixelColor(i, GRB(0,0,0))
    strip.show()

# -------------------------------------------------------
# MAIN LOOP
# -------------------------------------------------------
start_time = time.perf_counter()

try:
    print("Running SNOWSTORM vortex...")

    while True:
        now = time.perf_counter() - start_time
        spin_phase = REVERSE * 2 * math.pi * RPS * now

        for i in range(LED_COUNT):
            theta = led_theta[i]
            zf    = led_znorm[i]

            # helical phase
            phase = theta + spin_phase + 2 * math.pi * HELIX_TURNS * (1 - zf)

            # base helix intensity (wind strength)
            intensity = 0.5 * (1 + math.sin(phase))

            # snowflake flicker
            sparkle = 0.3 + 0.7 * random.random()

            # combined brightness
            bval = max(0, min(1, intensity * sparkle))

            # icy hue rotates with time + LED angle
            hue = (theta / (2*math.pi) + now * 0.1) % 1.0
            base_color = icy_color(hue)

            # unpack GRB
            g = (base_color >> 16) & 0xFF
            r = (base_color >> 8)  & 0xFF
            b = base_color & 0xFF

            # scale brightness
            R = int(r * bval)
            G = int(g * bval)
            B = int(b * bval)

            strip.setPixelColor(i, GRB(R, G, B))

        strip.show()
        time.sleep(INTERVAL)

except KeyboardInterrupt:
    print("Clearing LEDs...")
    clear_strip()
    strip.show()
