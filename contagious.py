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
LED_BRIGHTNESS = 150     # power-safe brightness
LED_INVERT     = False
LED_CHANNEL    = 0

# ----------------------------
# LOAD 3D COORDINATES
# ----------------------------
with open("tree_coords.json", "r") as f:
    coords = json.load(f)

# Precompute coords for speed
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
# COLOR HELPERS (GRB ORDER!)
# ----------------------------
def GRB(r, g, b):
    """WS2811 uses GRB, so order the bytes as (g, r, b)."""
    return Color(g, r, b)

XMAS_COLORS = [
    GRB(255, 255, 255),   # white
    GRB(255,   0,   0),   # red
    GRB(  0, 255,   0),   # green
]

# ----------------------------
# UTILITY FUNCTIONS
# ----------------------------
def clear_strip():
    for i in range(LED_COUNT):
        strip.setPixelColor(i, GRB(0, 0, 0))
    strip.show()

def dist(i, j):
    """Euclidean distance between LED i and LED j."""
    x1, y1, z1 = coords[i]
    x2, y2, z2 = coords[j]
    return math.sqrt((x1-x2)**2 + (y1-y2)**2 + (z1-z2)**2)

# ----------------------------
# CONTAGION EFFECT
# ----------------------------
def contagion_spread(
    max_radius=50,        # how far the contagion can spread
    radius_step=2,        # increment of distance per wave
    frame_delay=0.03      # delay between waves
):
    """
    Picks a random LED as the origin of a spread.
    Spreads outward in 3D based on distance.
    Each radius band gets a random color.
    """

    origin = random.randrange(LED_COUNT)
    print(f"Contagion origin LED: {origin}")

    # Precompute distances from origin to all LEDs
    distances = [dist(origin, i) for i in range(LED_COUNT)]

    radius = 0

    while radius < max_radius:
        # Pick a random color for this radius wave
        color = random.choice(XMAS_COLORS)

        # Light LEDs whose distance falls within this "ring"
        for i, d in enumerate(distances):
            if radius <= d < radius + radius_step:
                strip.setPixelColor(i, color)

        strip.show()
        time.sleep(frame_delay)

        radius += radius_step

    # At the end, fade out
    time.sleep(0.4)
    clear_strip()


# ----------------------------
# MAIN LOOP
# ----------------------------
if __name__ == "__main__":
    try:
        clear_strip()
        print("Running contagious spread animation...")

        while True:
            contagion_spread(
                max_radius=55,     # adjust based on your tree size
                radius_step=1.8,   # thinner rings look smoother
                frame_delay=0.03
            )

    except KeyboardInterrupt:
        print("\nStopping, clearing LEDs...")
        clear_strip()
