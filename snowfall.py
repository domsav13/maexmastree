# snowfall_vertical.py — true falling snow using Z-axis ordering

import time
import json
import os
import random
import signal
from rpi_ws281x import PixelStrip, Color

running = True
strip = None

def GRB(r, g, b):
    return Color(g, r, b)

def handle_exit(signum, frame):
    global running
    running = False


# --------------------------------------------------------------
# Hyperparameters
# --------------------------------------------------------------
FLAKE_COUNT       = 100
FALL_SPEED        = 2      # lower = slower drift (0.05–0.18 recommended)
FADE_RATE         = 1
TWINKLE_CHANCE    = 0.02
TWINKLE_AMOUNT    = 10
FRAME_DELAY       = 0.055
BRIGHTNESS_MIN    = 40
BRIGHTNESS_MAX    = 255


# --------------------------------------------------------------
# Load LED positions
# --------------------------------------------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
with open(os.path.join(BASE_DIR, "tree_coords.json")) as f:
    coords = json.load(f)

LED_COUNT = len(coords)

# Extract Z coordinates and sort LED indices by Z descending (top→bottom)
z_values = [p[2] for p in coords]
sorted_by_height = sorted(range(LED_COUNT), key=lambda i: z_values[i], reverse=True)

# for quick lookup, create rank → LED index mapping
# Example: sorted_z_order[0] = highest LED, sorted_z_order[-1] = lowest
sorted_z_order = sorted_by_height

# Also create reverse lookup: which index in this sorted order is LED i?
z_rank = {led: idx for idx, led in enumerate(sorted_z_order)}

z_min = min(z_values)
z_max = max(z_values)


# --------------------------------------------------------------
# Snowflake class using true vertical ordering
# --------------------------------------------------------------
class Flake:
    def __init__(self):
        self.reset()

    def reset(self):
        # start near top (random X/Y LED but HIGH Z rank)
        start_rank = random.randint(0, max(3, LED_COUNT // 10))
        self.position = start_rank                 # position in sorted_z_order list
        self.brightness = BRIGHTNESS_MAX

    def update(self):
        # Move downward along sorted order (larger index → lower physically)
        self.position = min(self.position + FALL_SPEED, LED_COUNT - 1)

        # Fade as it falls
        self.brightness = max(BRIGHTNESS_MIN, self.brightness - FADE_RATE)

        # Twinkle effect
        if random.random() < TWINKLE_CHANCE:
            self.brightness = min(
                BRIGHTNESS_MAX,
                max(BRIGHTNESS_MIN, self.brightness + random.randint(-TWINKLE_AMOUNT, TWINKLE_AMOUNT))
            )

        # Respawn when reaching the bottom
        if self.position >= LED_COUNT - 1:
            self.reset()

    @property
    def led(self):
        # convert float position to nearest LED index
        return sorted_z_order[int(self.position)]


# --------------------------------------------------------------
# Main animation loop
# --------------------------------------------------------------
def main():
    global strip, running

    signal.signal(signal.SIGTERM, handle_exit)
    signal.signal(signal.SIGINT, handle_exit)

    strip = PixelStrip(
        LED_COUNT, 18, 800000, 10, False, 255, 0
    )
    strip.begin()

    flakes = [Flake() for _ in range(FLAKE_COUNT)]

    while running:

        # clear frame
        for i in range(LED_COUNT):
            strip.setPixelColor(i, GRB(0,0,0))

        # update and draw flakes
        for fl in flakes:
            fl.update()
            strip.setPixelColor(fl.led, GRB(fl.brightness, fl.brightness, fl.brightness))

        strip.show()
        time.sleep(FRAME_DELAY)

    # Clear on exit
    for i in range(LED_COUNT):
        strip.setPixelColor(i, GRB(0,0,0))
    strip.show()


if __name__ == "__main__":
    main()
