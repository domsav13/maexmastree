import time
import json
import random
import math
from rpi_ws281x import PixelStrip, Color

# ----------------------------
# LED STRIP CONFIG
# ----------------------------
LED_COUNT      = 500
LED_PIN        = 18
LED_FREQ_HZ    = 800000
LED_DMA        = 10
LED_BRIGHTNESS = 150
LED_INVERT     = False
LED_CHANNEL    = 0

# ----------------------------
# LOAD 3D COORDINATES
# ----------------------------
with open("tree_coords.json", "r") as f:
    coords = json.load(f)

coords = [(float(x), float(y), float(z)) for (x, y, z) in coords]

# ----------------------------
# INITIALIZE LED STRIP
# ----------------------------
strip = PixelStrip(
    LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA,
    LED_INVERT, LED_BRIGHTNESS, LED_CHANNEL
)
strip.begin()

# ----------------------------
# COLOR HELPERS (GRB!)
# ----------------------------
def GRB(r, g, b):
    return Color(g, r, b)

WHITE = GRB(255, 255, 255)
RED   = GRB(255, 0,   0)
GREEN = GRB(0,   255, 0)

XMAS_COLORS = [WHITE, RED, GREEN]

# ----------------------------
# UTILITY
# ----------------------------
def clear_strip():
    for i in range(LED_COUNT):
        strip.setPixelColor(i, GRB(0, 0, 0))
    strip.show()

def distance(i, j):
    x1, y1, z1 = coords[i]
    x2, y2, z2 = coords[j]
    return math.sqrt((x1-x2)**2 + (y1-y2)**2 + (z1-z2)**2)

# Precompute pairwise distances FROM ANY LED to ALL LEDs
# This makes the effect MUCH faster
dist_matrix = [
    [distance(i, j) for j in range(LED_COUNT)]
    for i in range(LED_COUNT)
]

# ----------------------------
# TRUE SPHERICAL CONTAGION SPREAD
# ----------------------------
def contagious_sphere(
    max_radius=35,
    radius_step=1.8,
    decay=4.0,
    frame_delay=0.02
):
    """
    True spherical contagion:
    - One LED starts the infection
    - Nearby LEDs light up as radius grows
    - LEDs turn OFF after the radius passes (creating decay)
    """

    origin = random.randrange(LED_COUNT)
    print(f"Origin: {origin}")

    distances = dist_matrix[origin]
    color = random.choice(XMAS_COLORS)

    radius = 0

    while radius < max_radius:
        inner = radius - decay        # everything behind the front turns OFF
        outer = radius + radius_step  # current spread front

        for i, d in enumerate(distances):
            if inner <= d < outer:
                strip.setPixelColor(i, color)          # turning ON
            else:
                strip.setPixelColor(i, GRB(0,0,0))     # turning OFF behind

        strip.show()
        time.sleep(frame_delay)

        radius += radius_step

    clear_strip()
    time.sleep(0.05)

# ----------------------------
# MAIN LOOP
# ----------------------------
if __name__ == "__main__":
    try:
        clear_strip()
        print("Running 3D spherical contagion spread...")

        while True:
            contagious_sphere(
                max_radius=40,       # how large the contagion gets
                radius_step=1.7,     # how fast it spreads
                decay=5.0,           # how far behind the wave turns off
                frame_delay=0.02
            )

    except KeyboardInterrupt:
        print("\nStopping...")
        clear_strip()
