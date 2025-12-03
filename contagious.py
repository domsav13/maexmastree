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

def dist(i, j):
    x1, y1, z1 = coords[i]
    x2, y2, z2 = coords[j]
    return math.sqrt((x1-x2)**2 + (y1-y2)**2 + (z1-z2)**2)

# ----------------------------
# TRUE RADIAL PULSE EFFECT
# ----------------------------
def pulse_wave(
    max_radius=60,
    ring_thickness=2.0,
    radius_step=1.2,
    frame_delay=0.02
):
    """
    A clean outward-propagating pulse wave:
    - LEDs flash only when the wave radius matches their distance from origin.
    - LEDs turn off immediately afterward.
    """

    origin = random.randrange(LED_COUNT)
    print(f"Pulse origin LED: {origin}")

    # Precompute distances to origin
    distances = [dist(origin, i) for i in range(LED_COUNT)]

    # Pick the pulse color
    color = random.choice(XMAS_COLORS)

    radius = 0.0

    clear_strip()

    while radius < max_radius:
        # Light LEDs only IF the wavefront is passing them now
        for i, d in enumerate(distances):
            if radius <= d < radius + ring_thickness:
                strip.setPixelColor(i, color)
            else:
                strip.setPixelColor(i, GRB(0, 0, 0))

        strip.show()
        time.sleep(frame_delay)

        radius += radius_step

    clear_strip()


# ----------------------------
# MAIN LOOP
# ----------------------------
if __name__ == "__main__":
    try:
        clear_strip()
        print("Running radial pulse wave...")

        while True:
            pulse_wave(
                max_radius=65,       # large enough for whole tree
                ring_thickness=2.0,  # thickness of the pulse
                radius_step=1.1,     # how fast the pulse expands
                frame_delay=0.02     # speed of animation
            )

    except KeyboardInterrupt:
        print("\nStopping, clearing LEDs...")
        clear_strip()
