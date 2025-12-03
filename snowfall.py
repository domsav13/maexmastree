# snowfall.py
import time
import json
import os
import random
import signal
from rpi_ws281x import PixelStrip, Color

running = True
strip = None

def GRB(r,g,b):
    return Color(g,r,b)

def handle_exit(signum, frame):
    global running
    running = False

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
with open(os.path.join(BASE_DIR,"tree_coords.json")) as f:
    coords = json.load(f)

LED_COUNT=len(coords)
zs=[p[2] for p in coords]
z_min,z_max=min(zs),max(zs)

LED_PIN=18
LED_FREQ_HZ=800000
LED_DMA=10
LED_BRIGHTNESS=255
LED_INVERT=False
LED_CHANNEL=0

# Snowflake particles
class Flake:
    def __init__(self):
        self.led = random.randrange(LED_COUNT)
        self.z = zs[self.led]
        self.brightness = 255

    def update(self):
        # Slowly fall downward
        self.z -= 0.7

        # fade slightly as it falls
        self.brightness = max(0, self.brightness - 5)

        # reposition to closest LED at this Z
        closest = min(range(LED_COUNT),
                      key=lambda i: abs(zs[i]-self.z))
        self.led = closest

        # if below bottom, respawn at top
        if self.z <= z_min - 2:
            self.z = random.uniform(z_max-1, z_max)
            self.brightness = 255

def main():
    global strip, running

    signal.signal(signal.SIGTERM, handle_exit)
    signal.signal(signal.SIGINT, handle_exit)

    strip = PixelStrip(LED_COUNT,LED_PIN,LED_FREQ_HZ,
                       LED_DMA,LED_INVERT,LED_BRIGHTNESS,LED_CHANNEL)
    strip.begin()

    # Create many snow particles
    flakes = [Flake() for _ in range(45)]

    while running:

        # clear frame
        for i in range(LED_COUNT):
            strip.setPixelColor(i, GRB(0,0,0))

        # update and draw flakes
        for fl in flakes:
            fl.update()
            strip.setPixelColor(fl.led, GRB(fl.brightness, fl.brightness, fl.brightness))

        strip.show()
        time.sleep(0.03)

    # clear on exit
    for i in range(LED_COUNT):
        strip.setPixelColor(i, GRB(0,0,0))
    strip.show()

if __name__ == "__main__":
    main()
