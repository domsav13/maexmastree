# double_helix.py
import time
import json
import os
import math
import signal
from rpi_ws281x import PixelStrip, Color
import colorsys

running = True
strip = None

def GRB(r, g, b):
    return Color(g, r, b)

def handle_exit(signum, frame):
    global running
    running = False

# Load 3D coordinates
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
with open(os.path.join(BASE_DIR, "tree_coords.json")) as f:
    coords = json.load(f)

LED_COUNT = len(coords)

# Precompute theta and z
thetas = []
zs = []
for x, y, z in coords:
    thetas.append(math.atan2(y, x))
    zs.append(z)

z_min, z_max = min(zs), max(zs)
height = z_max - z_min

# LED strip config
LED_PIN = 18
LED_FREQ_HZ = 800000
LED_DMA = 10
LED_BRIGHTNESS = 255
LED_INVERT = False
LED_CHANNEL = 0

def vibrant(h):
    r, g, b = colorsys.hsv_to_rgb(h, 1.0, 1.0)
    return GRB(int(r*255), int(g*255), int(b*255))

def main():
    global strip, running

    signal.signal(signal.SIGTERM, handle_exit)
    signal.signal(signal.SIGINT, handle_exit)

    strip = PixelStrip(LED_COUNT, LED_PIN, LED_FREQ_HZ,
                       LED_DMA, LED_INVERT, LED_BRIGHTNESS, LED_CHANNEL)
    strip.begin()

    phase = 0.0
    speed = 0.04
    turns = 5.5

    while running:
        phase += speed
        for i in range(LED_COUNT):
            theta = thetas[i]
            z_norm = (zs[i] - z_min) / height

            # helix phase
            h1 = theta + 2 * math.pi * turns * z_norm + phase
            h2 = theta + 2 * math.pi * turns * z_norm - phase

            # Two helix intensities
            v1 = (math.sin(h1) + 1) / 2
            v2 = (math.sin(h2) + 1) / 2

            v = max(v1, v2)  # combined

            color = vibrant((z_norm + phase * 0.1) % 1.0)
            g = int(((color >> 16) & 0xFF) * v)
            r = int(((color >> 8) & 0xFF) * v)
            b = int((color & 0xFF) * v)

            strip.setPixelColor(i, GRB(r, g, b))

        strip.show()
        time.sleep(0.02)

    # On exit
    for i in range(LED_COUNT):
        strip.setPixelColor(i, GRB(0,0,0))
    strip.show()

if __name__ == "__main__":
    main()
