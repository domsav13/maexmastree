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
LED_BRIGHTNESS = 255    # we will control brightness manually
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
# COLOR HELPERS (GRB FORMAT)
# ----------------------------
def GRB(r, g, b):
    """WS2811 uses GRB byte order."""
    return Color(g, r, b)

WHITE = GRB(255, 255, 255)
RED   = GRB(255,   0,   0)
GREEN = GRB(0,   255,   0)

XMAS_COLORS = [WHITE, RED, GREEN]

# ----------------------------
# UTILITY FUNCTIONS
# ----------------------------
def clear_strip():
    for i in range(LED_COUNT):
        strip.setPixelColor(i, GRB(0, 0, 0))
    strip.show()

def distance(i, j):
    x1, y1, z1 = coords[i]
    x2, y2, z2 = coords[j]
    return math.sqrt((x1-x2)**2 + (y1-y2)**2 + (z1-z2)**2)

# ----------------------------
# PRECOMPUTE DISTANCES
# ----------------------------
print("Computing distance matrix (one-time init)...")
DIST = [
    [distance(i, j) for j in range(LED_COUNT)]
    for i in range(LED_COUNT)
]
print("Distance matrix ready.")

# ----------------------------
# CONSTANT BRIGHTNESS SCALING
# ----------------------------
def scale_brightness(color, lit_count, max_total_brightness=160):
    """
    Keeps visual brightness constant regardless of how many LEDs are lit.
    color = GRB ordered Color()
    """
    if lit_count <= 0:
        return GRB(0, 0, 0)

    # Extract GRB components from packed Color
    g = (color >> 16) & 0xFF
    r = (color >> 8)  & 0xFF
    b =  color        & 0xFF

    # Normalize scale
    scale = max_total_brightness / (lit_count)
    if scale > 1:
        scale = 1  # avoid going brighter than original

    r = int(r * scale)
    g = int(g * scale)
    b = int(b * scale)

    return GRB(r, g, b)

# ----------------------------
# SPHERICAL CONTAGION FILL
# ----------------------------
def spherical_fill(
    radius_step=1.2,
    frame_delay=0.02
):
    """
    - Pick a random origin LED
    - Expand outward until all LEDs are lit
    - LEDs stay ON during that spread
    - After full illumination: reset & repeat
    - Colors are GRB and random per spread
    """

    origin = random.randrange(LED_COUNT)
    print(f"New origin: {origin}")

    dist_list = DIST[origin]
    color = random.choice(XMAS_COLORS)

    max_radius = max(dist_list)

    lit = [False] * LED_COUNT

    radius = 0.0

    while radius <= max_radius:
        lit_count = 0

        # Determine who should turn ON this frame
        for i, d in enumerate(dist_list):
            if not lit[i] and d <= radius:
                lit[i] = True

            if lit[i]:
                lit_count += 1

        # Render frame with constant brightness
        for i, is_lit in enumerate(lit):
            if is_lit:
                strip.setPixelColor(i, scale_brightness(color, lit_count))
            else:
                strip.setPixelColor(i, GRB(0,0,0))

        strip.show()
        time.sleep(frame_delay)

        radius += radius_step

    # Pause briefly, then reset
    time.sleep(0.4)
    clear_strip()


# ----------------------------
# MAIN LOOP
# ----------------------------
if __name__ == "__main__":
    try:
        clear_strip()
        print("Running spherical fill with constant brightness...")

        while True:
            spherical_fill(
                radius_step=1.2,    # expansion speed
                frame_delay=0.02    # smoothness
            )

    except KeyboardInterrupt:
        print("\nClearing LEDs...")
        clear_strip()
