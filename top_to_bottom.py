# top_to_bottom.py  (Vibrant Vertical Band Sweep)
import time
import json
import os
import signal
from rpi_ws281x import PixelStrip, Color
import colorsys

running = True
strip = None

def GRB(r, g, b):
    return Color(g, r, b)

# -------------------------
# Load coordinates
# -------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
COORDS_JSON = os.path.join(BASE_DIR, "tree_coords.json")

with open(COORDS_JSON, "r") as f:
    coords = json.load(f)

LED_COUNT = len(coords)

# Use Z coordinate for height
zs = [p[2] for p in coords]
z_min, z_max = min(zs), max(zs)
z_range = z_max - z_min

# -------------------------
# LED Strip config
# -------------------------
LED_PIN        = 18
LED_FREQ_HZ    = 800000
LED_DMA        = 10
LED_BRIGHTNESS = 255
LED_INVERT     = False
LED_CHANNEL    = 0

# -------------------------
# Helpers
# -------------------------
def handle_exit(signum, frame):
    global running
    running = False

def clear_strip():
    if strip:
        for i in range(LED_COUNT):
            strip.setPixelColor(i, GRB(0, 0, 0))
        strip.show()

def vibrant_color(hue):
    """Returns a GRB vibrant color using HSV full saturation + brightness."""
    r, g, b = colorsys.hsv_to_rgb(hue, 1.0, 1.0)
    return GRB(int(r * 255), int(g * 255), int(b * 255))


# -------------------------
# Main Animation
# -------------------------
def main():
    global strip, running

    signal.signal(signal.SIGINT, handle_exit)
    signal.signal(signal.SIGTERM, handle_exit)

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

    # Band parameters
    band_frac = 0.15              # thickness as fraction of height
    band_half = (band_frac * z_range) / 2.0

    pos = z_min + band_half       # center of band
    direction = 1                 # 1 = up, -1 = down

    z_step = z_range / 200.0      # vertical movement per frame
    frame_delay = 0.02            # speed of animation

    hue = 0.0                     # starting color hue
    hue_step = 0.004              # how fast colors cycle

    try:
        while running:

            # Move vertical band
            pos += direction * z_step

            # Reverse direction at ends
            if pos + band_half >= z_max:
                pos = z_max - band_half
                direction = -1
            elif pos - band_half <= z_min:
                pos = z_min + band_half
                direction = 1

            low = pos - band_half
            high = pos + band_half

            # Cycle vibrant color
            hue = (hue + hue_step) % 1.0
            color = vibrant_color(hue)

            # Render LEDs
            for i, z in enumerate(zs):
                if low <= z <= high:
                    strip.setPixelColor(i, color)
                else:
                    strip.setPixelColor(i, GRB(0, 0, 0))

            strip.show()
            time.sleep(frame_delay)

    finally:
        clear_strip()


if __name__ == "__main__":
    main()
