# wind_swirl_white_fixed.py – pure white spiral + random dips
import time
import json
import os
import math
import signal
import random
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

thetas = []
zs = []
for x, y, z in coords:
    thetas.append(math.atan2(y, x))
    zs.append(z)

z_min, z_max = min(zs), max(zs)
height = z_max - z_min


# -----------------------------
# LED strip setup
# -----------------------------
LED_PIN = 18
LED_FREQ_HZ = 800000
LED_DMA = 10
LED_BRIGHTNESS = 255
LED_INVERT = False
LED_CHANNEL = 0


# -----------------------------
# Random brightness dips
# -----------------------------
BRIGHT_BASE = 255
MIN_RANDOM_DIP = 170
DIP_PERCENTAGE = 0.15

dip_indices = random.sample(range(LED_COUNT), int(LED_COUNT * DIP_PERCENTAGE))

initial_brightness = [BRIGHT_BASE] * LED_COUNT
for i in dip_indices:
    initial_brightness[i] = random.randint(MIN_RANDOM_DIP, BRIGHT_BASE)


# -----------------------------
# MAIN ANIMATION (PURE WHITE)
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

    t = 0.0
    swirl_speed = 0.14
    swirl_strength = 12.0

    try:
        while running:

            t += 0.05

            for i in range(LED_COUNT):
                theta = thetas[i]
                z_norm = (zs[i] - z_min) / height

                phase = theta * swirl_strength + z_norm * 8 - t * swirl_speed * 50
                swirl = (math.sin(phase) + 1) / 2   # 0 → 1

                # scale swirl by initial brightness dip
                brightness = int(swirl * initial_brightness[i])

                strip.setPixelColor(i, GRB(brightness, brightness, brightness))

            strip.show()
            time.sleep(0.015)

    finally:
        for i in range(LED_COUNT):
            strip.setPixelColor(i, GRB(0, 0, 0))
        strip.show()


if __name__ == "__main__":
    main()
