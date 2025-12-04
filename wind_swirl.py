# wind_swirl.py – fast spiral, all white, blinking brightness
import time
import json
import os
import math
import signal
from rpi_ws281x import PixelStrip, Color

running = True
strip = None

def GRB(r, g, b):
    return Color(g, r, b)

def handle_exit(signum, frame):
    global running
    running = False


# -----------------------------
# Load coordinates
# -----------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
with open(os.path.join(BASE_DIR, "tree_coords.json")) as f:
    coords = json.load(f)

LED_COUNT = len(coords)

# Precompute angle + Z
thetas = []
zs = []
for x, y, z in coords:
    thetas.append(math.atan2(y, x))
    zs.append(z)

z_min, z_max = min(zs), max(zs)
height = z_max - z_min


# -----------------------------
# LED Strip
# -----------------------------
LED_PIN = 18
LED_FREQ_HZ = 800000
LED_DMA = 10
LED_BRIGHTNESS = 255
LED_INVERT = False
LED_CHANNEL = 0


# -----------------------------
# Main animation
# -----------------------------
def main():
    global strip, running

    signal.signal(signal.SIGTERM, handle_exit)
    signal.signal(signal.SIGINT, handle_exit)

    strip = PixelStrip(
        LED_COUNT, LED_PIN, LED_FREQ_HZ,
        LED_DMA, LED_INVERT, LED_BRIGHTNESS, LED_CHANNEL
    )
    strip.begin()

    # Animation parameters
    t = 0.0
    spiral_speed = 0.06           # MUCH faster spiral
    swirl_strength = 11.0         # tighter wind spiral
    blink_speed = 0.10            # pulsing brightness

    try:
        while running:
            t += 0.05

            # blinking factor: 0 → 1 → 0 smoothly
            blink = (math.sin(t * blink_speed * 2 * math.pi) + 1) / 2

            for i in range(LED_COUNT):
                theta = thetas[i]
                z_norm = (zs[i] - z_min) / height

                # fast, clean spiral motion
                phase = theta * swirl_strength + z_norm * 8 - t * spiral_speed * 50

                swirl_intensity = (math.sin(phase) + 1) / 2

                # combine spiral + blinking
                brightness = swirl_intensity * blink
                brightness = max(0.0, min(1.0, brightness))

                val = int(brightness * 255)
                strip.setPixelColor(i, GRB(val, val, val))  # pure white

            strip.show()
            time.sleep(0.015)

    finally:
        # turn off LEDs on exit
        for i in range(LED_COUNT):
            strip.setPixelColor(i, GRB(0, 0, 0))
        strip.show()


if __name__ == "__main__":
    main()
