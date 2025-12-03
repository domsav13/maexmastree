import time
import json
from rpi_ws281x import PixelStrip, Color

# ----------------------------
# LED STRIP CONFIG
# ----------------------------
LED_COUNT      = 500      # Number of LEDs
LED_PIN        = 18       # PWM pin
LED_FREQ_HZ    = 800000
LED_DMA        = 10
LED_BRIGHTNESS = 200      # Prevents huge current draw
LED_INVERT     = False
LED_CHANNEL    = 0
LED_STRIP_TYPE = None     # Not needed here

# ----------------------------
# LOAD YOUR 3D COORDINATES
# ----------------------------
with open("tree_coords.json", "r") as f:
    coords = json.load(f)    # list of [x, y, z]

# ----------------------------
# SORT LED INDICES TOP → BOTTOM
# (highest z first, lowest z last)
# ----------------------------
# coords[i][2] = z value
sorted_indices = sorted(range(len(coords)), key=lambda i: coords[i][2], reverse=True)

# ----------------------------
# INITIALIZE LED STRIP
# ----------------------------
strip = PixelStrip(
    LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA,
    LED_INVERT, LED_BRIGHTNESS, LED_CHANNEL
)
strip.begin()

# GRB helper because WS2811 uses GRB, not RGB
def GRB(g, r, b):
    return Color(g, r, b)

# ----------------------------
# LIGHT FROM TOP TO BOTTOM
# ----------------------------
def light_top_to_bottom(delay=0.02):
    """Lights up LEDs in physically sorted order (top → bottom)."""
    # turn all off first
    for i in range(strip.numPixels()):
        strip.setPixelColor(i, GRB(0, 0, 0))
    strip.show()

    # light in sorted order
    for idx in sorted_indices:
        strip.setPixelColor(idx, GRB(255, 20, 20))  # red-ish in GRB
        strip.show()
        time.sleep(delay)

    # optional: fade out afterwards
    time.sleep(1)
    for idx in sorted_indices:
        strip.setPixelColor(idx, GRB(0, 0, 0))
        strip.show()
        time.sleep(delay / 2)


# ----------------------------
# RUN EFFECT
# ----------------------------
try:
    print("Running top-to-bottom effect...")
    light_top_to_bottom(delay=0.02)

except KeyboardInterrupt:
    print("\nClearing LEDs...")
    for i in range(strip.numPixels()):
        strip.setPixelColor(i, GRB(0, 0, 0))
    strip.show()
