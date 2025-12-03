"""
Helical vortex / spiral twister effect for a 3D LED Christmas tree.
Uses tree_coords.json (500 LEDs) and WS2811 GRB pixels.
"""

import os
import time
import math
import argparse
import json
from rpi_ws281x import PixelStrip, Color
import colorsys

# -------------------------------------------------------
# ARGUMENTS
# -------------------------------------------------------
parser = argparse.ArgumentParser(description="Vortex/Spiral Twister effect on 3D LED tree")
parser.add_argument("-i", "--interval", type=float, default=0.05,
                    help="Seconds between frames (frame rate)")
parser.add_argument("-r", "--rotations-per-sec", type=float, default=0.2,
                    help="Full rotations per second")
parser.add_argument("-t", "--turns", type=float, default=3.0,
                    help="Helix turns from bottom to top")
parser.add_argument("--reverse", action="store_true",
                    help="Reverse rotation direction")
parser.add_argument("--range", type=float, default=1.0,
                    help="Fractional Z range to animate (0–1)")
parser.add_argument("--rainbow", action="store_true",
                    help="Use rainbow colors instead of white")
args = parser.parse_args()

INTERVAL         = args.interval
RPS              = args.rotations_per_sec
HELIX_TURNS      = args.turns
REVERSE          = -1.0 if args.reverse else 1.0
Z_RANGE_FRACTION = max(0.0, min(1.0, args.range))

# -------------------------------------------------------
# LOAD 500 LED COORDINATES
# -------------------------------------------------------
BASE_DIR     = os.path.dirname(os.path.abspath(__file__))
COORDS_JSON  = os.path.join(BASE_DIR, "tree_coords.json")

with open(COORDS_JSON, "r") as f:
    positions = json.load(f)

LED_COUNT = len(positions)
print(f"Loaded {LED_COUNT} LED coordinates.")

# -------------------------------------------------------
# HELPER: GRB (WS2811)
# -------------------------------------------------------
def GRB(r, g, b):
    return Color(g, r, b)

def hsv_to_grb(h):
    """Convert hue to bright GRB color (rainbow mode)."""
    r, g, b = colorsys.hsv_to_rgb(h, 1.0, 1.0)
    return GRB(int(r*255), int(g*255), int(b*255))

# -------------------------------------------------------
# PRECOMPUTE THETA + NORMALIZED HEIGHT
# -------------------------------------------------------
tree_zs    = [p[2] for p in positions]
z_min      = min(tree_zs)
z_max      = max(tree_zs)
z_height   = z_max - z_min

led_theta = []
led_znorm = []

for (x, y, z) in positions:
    theta = math.atan2(y, x)
    z_n = (z - z_min) / z_height if z_height > 0 else 0.0
    z_n = z_n * Z_RANGE_FRACTION
    led_theta.append(theta)
    led_znorm.append(z_n)

# -------------------------------------------------------
# WS2811 LED STRIP SETUP
# -------------------------------------------------------
LED_PIN        = 18
LED_FREQ_HZ    = 800000
LED_DMA        = 10
LED_BRIGHTNESS = 255     # full, we control manually
LED_INVERT     = False
LED_CHANNEL    = 0

strip = PixelStrip(
    LED_COUNT, LED_PIN, LED_FREQ_HZ,
    LED_DMA, LED_INVERT, LED_BRIGHTNESS, LED_CHANNEL
)
strip.begin()

# -------------------------------------------------------
# CLEAR STRIP
# -------------------------------------------------------
def clear_strip():
    for i in range(LED_COUNT):
        strip.setPixelColor(i, GRB(0,0,0))

# -------------------------------------------------------
# MAIN LOOP
# -------------------------------------------------------
start_time = time.perf_counter()

try:
    print("Running vortex / spiral twister...")

    while True:
        now = time.perf_counter() - start_time
        spin_phase = REVERSE * 2 * math.pi * RPS * now

        for i in range(LED_COUNT):
            theta = led_theta[i]
            zfrac = led_znorm[i]

            # Helix phase contribution from Z
            phase = theta + spin_phase + 2 * math.pi * HELIX_TURNS * (1 - zfrac)

            # Wave brightness
            intensity = 0.5 * (1 + math.sin(phase))
            bval = max(0, min(1, intensity))

            if args.rainbow:
                # shift hue with spin
                hue = (theta / (2*math.pi) + now * RPS) % 1.0
                base_color = hsv_to_grb(hue)
            else:
                base_color = GRB(255, 255, 255)  # bright white

            # extract GRB components
            g = (base_color >> 16) & 0xFF
            r = (base_color >> 8)  & 0xFF
            b = base_color & 0xFF

            # scale intensity
            R = int(r * bval)
            G = int(g * bval)
            B = int(b * bval)

            strip.setPixelColor(i, GRB(R, G, B))

        strip.show()
        time.sleep(INTERVAL)

except KeyboardInterrupt:
    print("Stopping, clearing LEDs...")
    clear_strip()
    strip.show()
