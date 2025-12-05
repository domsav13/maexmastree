# snowfall.py (calm, slow, soft snowfall)
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

# -----------------------------
# Load LED coordinates
# -----------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
with open(os.path.join(BASE_DIR, "tree_coords.json")) as f:
    coords = json.load(f)

LED_COUNT = len(coords)
zs = [p[2] for p in coords]
z_min, z_max = min(zs), max(zs)

# -----------------------------
# LED hardware settings
# -----------------------------
LED_PIN = 18
LED_FREQ_HZ = 800000
LED_DMA = 10
LED_BRIGHTNESS = 255
LED_INVERT = False
LED_CHANNEL = 0

# -----------------------------
# Snowflake particle
# -----------------------------
class Flake:
    def __init__(self):
        self.reset()

    def reset(self):
        # start near top
        self.z = random.uniform(z_max - 2, z_max)
        self.brightness = random.randint(210, 255)
        self.led = min(range(LED_COUNT), key=lambda i: abs(zs[i] - self.z))

    def update(self):
        # fall gently
        self.z -= 0.15

        # soft natural fading
        self.brightness = max(50, self.brightness - 1)

        # subtle random twinkle variation
        if random.random() < 0.02:
            self.brightness = min(255, self.brightness + random.randint(1, 8))

        # move flake LED to closest z
        self.led = min(range(LED_COUNT), key=lambda i: abs(zs[i] - self.z))

        # respawn if it reaches bottom
        if self.z <= z_min - 2:
            self.reset()

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

    # More flakes, softer vibe
    flakes = [Flake() for _ in range(65)]

    while running:
        # Clear frame
        for i in range(LED_COUNT):
            strip.setPixelColor(i, GRB(0, 0, 0))

        # Draw flakes
        for fl in flakes:
            fl.update()
            strip.setPixelColor(fl.led, GRB(fl.brightness, fl.brightness, fl.brightness))

        strip.show()
        time.sleep(0.055)  # slower pacing

    # Clear on exit
    for i in range(LED_COUNT):
        strip.setPixelColor(i, GRB(0, 0, 0))
    strip.show()

if __name__ == "__main__":
    main()
