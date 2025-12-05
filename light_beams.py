# light_beams.py — sweeping 3D vertical light beams for 500-LED mapped Christmas tree

import time
import json
import os
import math
import signal
import random
from rpi_ws281x import PixelStrip, Color


# ------------------------------
#  WS2811 Color Helper (GRB)
# ------------------------------
def GRB(r, g, b):
    return Color(g, r, b)


# ------------------------------
#  Signal Handling for Exit
# ------------------------------
running = True
strip = None

def handle_exit(signal_received, frame):
    global running
    running = False


# ------------------------------
#  Load Coordinates
# ------------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
with open(os.path.join(BASE_DIR, "tree_coords.json")) as f:
    coords = json.load(f)

LED_COUNT = len(coords)

# Precompute polar angles for each LED
thetas = [math.atan2(y, x) for x, y, z in coords]


# ------------------------------
#  LED Driver Settings
# ------------------------------
LED_PIN        = 18
LED_FREQ_HZ    = 800000
LED_DMA        = 10
LED_BRIGHTNESS = 255
LED_INVERT     = False
LED_CHANNEL    = 0


# ------------------------------
#  Hyperparameters (Tweak These)
# ------------------------------
BEAM_COUNT        = 1        # how many beams sweep around
BEAM_WIDTH        = 0.45     # larger = thicker beams
ROTATION_SPEED    = 0.2     # smaller = slower sweep
SOFTNESS          = 5        # higher = smoother edges
COLOR_MODE        = "random_cycle"  # "white", "red", "green", "blue", "rainbow", "random_cycle"

FRAME_TIME        = 0.02     # delay per frame (smoothness)


# Optional color presets
COLOR_PRESETS = {
    "white":  (255, 255, 255),
    "red":    (255, 0, 0),
    "green":  (0, 255, 0),
    "blue":   (0, 0, 255)
}


def get_beam_color(t):
    """Return color based on selected mode."""
    if COLOR_MODE in COLOR_PRESETS:
        return COLOR_PRESETS[COLOR_MODE]

    # Smooth rainbow mode
    if COLOR_MODE == "rainbow":
        hue = (t * 0.05) % 1
        r = int((math.sin(hue * math.pi * 2) * 0.5 + 0.5) * 255)
        g = int((math.sin((hue + 0.33) * math.pi * 2) * 0.5 + 0.5) * 255)
        b = int((math.sin((hue + 0.66) * math.pi * 2) * 0.5 + 0.5) * 255)
        return (r, g, b)

    # Random cycle mode: occasionally shift color
    if COLOR_MODE == "random_cycle":
        if random.random() < 0.002:  # occasional shift
            return (random.randint(50,255), random.randint(50,255), random.randint(50,255))
        return get_beam_color.last_color

# store last color to avoid flicker on random cycle
get_beam_color.last_color = (255, 255, 255)


# ------------------------------
#  Animation Loop
# ------------------------------
def main():
    global strip, running

    signal.signal(signal.SIGINT, handle_exit)
    signal.signal(signal.SIGTERM, handle_exit)

    strip = PixelStrip(
        LED_COUNT, LED_PIN, LED_FREQ_HZ,
        LED_DMA, LED_INVERT, LED_BRIGHTNESS, LED_CHANNEL
    )
    strip.begin()

    # Clear startup garbage
    for _ in range(3):
        for i in range(LED_COUNT):
            strip.setPixelColor(i, GRB(0,0,0))
        strip.show()
        time.sleep(0.05)

    t = 0

    while running:
        t += FRAME_TIME

        # choose color only occasionally if in random mode
        color = get_beam_color(t)
        get_beam_color.last_color = color

        for i in range(LED_COUNT):

            # rotating beam angular position
            beam_angle = (t * ROTATION_SPEED) % (2 * math.pi)

            # support multiple beams evenly spaced
            beam_value = 0
            for b in range(BEAM_COUNT):
                offset = 2 * math.pi * (b / BEAM_COUNT)
                diff = abs(math.sin((thetas[i] - beam_angle - offset) / BEAM_WIDTH))
                beam_value += 1 - diff

            # soften edges
            beam_value = max(0, min(1, beam_value ** SOFTNESS))

            r = int(color[0] * beam_value)
            g = int(color[1] * beam_value)
            b = int(color[2] * beam_value)

            strip.setPixelColor(i, GRB(r, g, b))

        strip.show()
        time.sleep(FRAME_TIME)

    # turn off on exit
    for i in range(LED_COUNT):
        strip.setPixelColor(i, GRB(0,0,0))
    strip.show()


if __name__ == "__main__":
    main()
