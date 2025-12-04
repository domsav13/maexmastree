# northern_lights.py — 3D Aurora Borealis for 500-LED Christmas Tree (WS2811 GRB)
#
# Smooth Perlin-like noise + flowing color gradients based on LED XYZ locations.

import time
import os
import json
import math
import signal
import random
from rpi_ws281x import PixelStrip, Color

running = True
strip   = None

# ------------------------------------------------------
# WS2811 GRB helper
# ------------------------------------------------------
def GRB(r, g, b):
    return Color(g, r, b)

def handle_exit(signum, frame):
    global running
    running = False


# ------------------------------------------------------
# Load LED coordinates
# ------------------------------------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
with open(os.path.join(BASE_DIR, "tree_coords.json")) as f:
    coords = json.load(f)

LED_COUNT = len(coords)

xs = [p[0] for p in coords]
ys = [p[1] for p in coords]
zs = [p[2] for p in coords]

# Normalize coordinates
x_min, x_max = min(xs), max(xs)
y_min, y_max = min(ys), max(ys)
z_min, z_max = min(zs), max(zs)

def norm(v, mn, mx):
    return (v - mn) / (mx - mn + 1e-9)

# Pre-normalized coordinate list for speed
norm_coords = [
    (norm(x, x_min, x_max), norm(y, y_min, y_max), norm(z, z_min, z_max))
    for (x,y,z) in coords
]


# ------------------------------------------------------
# LED Strip Setup
# ------------------------------------------------------
LED_PIN        = 18
LED_FREQ_HZ    = 800000
LED_DMA        = 10
LED_BRIGHTNESS = 255
LED_INVERT     = False
LED_CHANNEL    = 0


# ------------------------------------------------------
# Smooth noise function — cheap fake 3D Perlin
# ------------------------------------------------------
def smooth_noise3(x, y, z, t):
    """ A smoothed multi-octave pseudo-noise field for aurora motion """
    # Primary wave — slow curtain movement
    n1 = math.sin(2*math.pi*(x*0.5 + t*0.03))
    n2 = math.sin(2*math.pi*(y*0.7 - t*0.025))
    n3 = math.sin(2*math.pi*(z*0.8 + t*0.02))

    # Higher octave turbulence
    n4 = math.sin(2*math.pi*(x*2 + y*2 - t*0.065))
    n5 = math.sin(2*math.pi*(y*3 + z*3 + t*0.045))

    # Weighted combination
    return 0.6*n1 + 0.5*n2 + 0.4*n3 + 0.2*n4 + 0.2*n5


# ------------------------------------------------------
# Aurora color palette blend
# ------------------------------------------------------
AURORA_COLORS = [
    (0,   200, 50),   # green
    (0,   255, 200),  # teal
    (50,  150, 255),  # blue
    (180, 80,  255),  # violet
]

def blend_colors(c1, c2, t):
    return (
        int(c1[0] + (c2[0] - c1[0]) * t),
        int(c1[1] + (c2[1] - c1[1]) * t),
        int(c1[2] + (c2[2] - c1[2]) * t),
    )


def aurora_color(f):
    """ Given a 0–1 noise value, pick 2 palette colors and blend """
    f = max(0, min(1, f))
    idx = int(f * (len(AURORA_COLORS)-1))
    idx2 = min(idx+1, len(AURORA_COLORS)-1)

    local_t = (f * (len(AURORA_COLORS)-1)) % 1.0

    return blend_colors(AURORA_COLORS[idx], AURORA_COLORS[idx2], local_t)


# ------------------------------------------------------
# MAIN ANIMATION LOOP
# ------------------------------------------------------
def aurora_loop(interval=0.02, brightness=1.0):
    global strip, running

    t = 0

    while running:
        t += interval

        for i, (nx, ny, nz) in enumerate(norm_coords):

            # Compute layered noise
            f = smooth_noise3(nx, ny, nz, t)
            f = (f + 1) / 2   # normalize to 0–1

            # Additional height weighting to mimic waves in sky
            height_boost = nz**1.5
            f = (f * 0.6) + (height_boost * 0.4)

            # Clamp value
            f = max(0, min(1, f))

            # Convert to aurora color
            r, g, b = aurora_color(f)

            # Global brightness control
            r = int(r * brightness)
            g = int(g * brightness)
            b = int(b * brightness)

            strip.setPixelColor(i, GRB(r, g, b))

        strip.show()
        time.sleep(interval)


# ------------------------------------------------------
# ENTRY POINT
# ------------------------------------------------------
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

    try:
        aurora_loop(interval=0.02, brightness=1.0)
    finally:
        # Turn off on exit
        for i in range(LED_COUNT):
            strip.setPixelColor(i, GRB(0,0,0))
        strip.show()


if __name__ == "__main__":
    main()
