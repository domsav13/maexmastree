import time
import json
import random
import math
from rpi_ws281x import PixelStrip, Color
import colorsys

# --------------------------------------------------------
# LED STRIP CONFIG (GRB WS2811)
# --------------------------------------------------------
LED_COUNT      = 500
LED_PIN        = 18
LED_FREQ_HZ    = 800000
LED_DMA        = 10
LED_BRIGHTNESS = 255     # use full brightness; we will scale manually
LED_INVERT     = False
LED_CHANNEL    = 0

# --------------------------------------------------------
# LOAD 3D COORDINATES
# --------------------------------------------------------
with open("tree_coords.json", "r") as f:
    coords = json.load(f)

coords = [(float(x), float(y), float(z)) for (x, y, z) in coords]

# --------------------------------------------------------
# INITIALIZE PIXEL STRIP
# --------------------------------------------------------
strip = PixelStrip(
    LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA,
    LED_INVERT, LED_BRIGHTNESS, LED_CHANNEL
)
strip.begin()

# --------------------------------------------------------
# COLOR HELPERS (WS2811 USES GRB!)
# --------------------------------------------------------
def GRB(r, g, b):
    """Create a Color() value in GRB order."""
    return Color(g, r, b)

def hsv_to_grb(h):
    """Convert a hue (0–1) to bright GRB color via HSV."""
    r, g, b = colorsys.hsv_to_rgb(h, 1.0, 1.0)
    return GRB(int(r*255), int(g*255), int(b*255))

# 20 vibrant rainbow hues
RAINBOW_COLORS = [hsv_to_grb(i/20) for i in range(20)]

# Extra accent colors
EXTRA_COLORS = [
    GRB(255, 0,   0),    # bright red
    GRB(0,   255, 0),    # bright green
    GRB(255, 255, 0),    # gold/yellow
    GRB(255, 0,   255),  # magenta
    GRB(0,   255, 255),  # cyan
    GRB(255, 100, 0),    # orange
    GRB(180, 0,   255),  # violet
    GRB(255, 255, 255),  # white highlight
]

COLOR_POOL = RAINBOW_COLORS + EXTRA_COLORS

# --------------------------------------------------------
# UTILITY
# --------------------------------------------------------
def clear_strip():
    for i in range(LED_COUNT):
        strip.setPixelColor(i, GRB(0,0,0))
    strip.show()

def distance(i, j):
    x1, y1, z1 = coords[i]
    x2, y2, z2 = coords[j]
    return math.sqrt((x1-x2)**2 + (y1-y2)**2 + (z1-z2)**2)

# --------------------------------------------------------
# PRECOMPUTE DISTANCE MATRIX (fast animation)
# --------------------------------------------------------
print("Computing distance matrix (one-time)…")
DIST = [
    [distance(i, j) for j in range(LED_COUNT)]
    for i in range(LED_COUNT)
]
print("Distance matrix ready.\n")

# --------------------------------------------------------
# CONSTANT BRIGHTNESS NORMALIZATION
# --------------------------------------------------------
def scale_brightness(color, lit_count, max_total_brightness=160):
    """
    Ensures visual brightness stays constant no matter how 
    many LEDs are lit. lit_count is number of lit LEDs.
    """
    if lit_count <= 0:
        return GRB(0,0,0)

    # extract GRB
    g = (color >> 16) & 0xFF
    r = (color >> 8)  & 0xFF
    b =  color        & 0xFF

    scale = max_total_brightness / lit_count
    if scale > 1:
        scale = 1

    r = int(r * scale)
    g = int(g * scale)
    b = int(b * scale)

    return GRB(r, g, b)

# --------------------------------------------------------
# SPHERICAL CONTAGION FILL (GROW UNTIL FULL)
# --------------------------------------------------------
def spherical_fill(
    radius_step=1.2,
    frame_delay=0.02
):
    """
    One LED is chosen.
    Radius expands outward until all LEDs are lit.
    LEDs stay ON once they are lit.
    After the full fill, everything clears and repeats.
    """

    origin = random.randrange(LED_COUNT)
    print(f"Origin = {origin}")

    dist_list = DIST[origin]
    color = random.choice(COLOR_POOL)

    # largest radius needed to cover the entire tree
    max_radius = max(dist_list)

    lit = [False] * LED_COUNT
    radius = 0.0

    while radius <= max_radius:
        # count LEDs that have turned on
        lit_count = 0
        for i, d in enumerate(dist_list):
            if not lit[i] and d <= radius:
                lit[i] = True
            if lit[i]:
                lit_count += 1

        # render with constant brightness
        for i, on in enumerate(lit):
            if on:
                strip.setPixelColor(i, scale_brightness(color, lit_count))
            else:
                strip.setPixelColor(i, GRB(0,0,0))

        strip.show()
        time.sleep(frame_delay)
        radius += radius_step

    # small pause before clear + restart
    time.sleep(0.4)
    clear_strip()

# --------------------------------------------------------
# MAIN LOOP
# --------------------------------------------------------
if __name__ == "__main__":
    try:
        clear_strip()
        print("Running spherical contagion fill (vibrant colors)…\n")

        while True:
            spherical_fill(
                radius_step=1.2,
                frame_delay=0.02
            )

    except KeyboardInterrupt:
        print("\nStopping, clearing LEDs…")
        clear_strip()
