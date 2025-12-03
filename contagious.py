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
# COLOR HELPERS (WS2811 = GRB)
# ----------------------------
def GRB(r, g, b):
    return Color(g, r, b)

WHITE = GRB(255, 255, 255)
RED   = GRB(255, 0,   0)
GREEN = GRB(0,   255, 0)

XMAS_COLORS = [WHITE, RED, GREEN]

# ----------------------------
# UTILITY: CLEAR
# ----------------------------
def clear_strip():
    for i in range(LED_COUNT):
        strip.setPixelColor(i, GRB(0, 0, 0))
    strip.show()

# ----------------------------
# PRECOMPUTED DISTANCES
# ----------------------------
def distance(i, j):
    x1, y1, z1 = coords[i]
    x2, y2, z2 = coords[j]
    return math.sqrt((x1-x2)**2 + (y1-y2)**2 + (z1-z2)**2)

# Precompute distance map for speed:
print("Precomputing distances (first run only)...")
DIST = [
    [distance(i, j) for j in range(LED_COUNT)]
    for i in range(LED_COUNT)
]
print("Distance matrix ready.")

# ----------------------------
# TRUE SPHERICAL FILL ANIMATION
# ----------------------------
def spherical_fill(
    radius_step=1.2,
    frame_delay=0.02
):
    """
    - Pick a random LED
    - Expand spherical radius until entire tree is lit
    - LEDs STAY LIT once activated
    - Reset and repeat
    """

    origin = random.randrange(LED_COUNT)
    print(f"New origin: {origin}")

    # Precomputed distances from origin
    dist_list = DIST[origin]

    # Pick random color
    color = random.choice(XMAS_COLORS)

    # Determine maximum needed radius (farthest LED)
    max_radius = max(dist_list)

    lit = [False] * LED_COUNT

    radius = 0.0
    while radius <= max_radius:
        for i, d in enumerate(dist_list):
            if not lit[i] and d <= radius:
                lit[i] = True
                strip.setPixelColor(i, color)

        strip.show()
        time.sleep(frame_delay)
        radius += radius_step

    time.sleep(0.5)
    clear_strip()


# ----------------------------
# MAIN LOOP
# ----------------------------
if __name__ == "__main__":
    try:
        clear_strip()
        print("Running spherical fill contagion effect...")

        while True:
            spherical_fill(
                radius_step=1.2,
                frame_delay=0.02
            )

    except KeyboardInterrupt:
        print("\nClearing LEDs...")
        clear_strip()
