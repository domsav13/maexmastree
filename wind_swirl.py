# wind_swirl.py
import time
import json
import os
import math
import signal
from rpi_ws281x import PixelStrip, Color
import colorsys

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

LED_COUNT = len(coords)

# Precompute angles + Z
thetas = []
zs = []
for x,y,z in coords:
    thetas.append(math.atan2(y,x))
    zs.append(z)

z_min, z_max = min(zs), max(zs)
height = z_max - z_min

# strip config
LED_PIN=18
LED_FREQ_HZ=800000
LED_DMA=10
LED_BRIGHTNESS=255
LED_INVERT=False
LED_CHANNEL=0

def vibrant(h):
    r,g,b = colorsys.hsv_to_rgb(h,1,1)
    return GRB(int(r*255),int(g*255),int(b*255))

def main():
    global strip, running
    signal.signal(signal.SIGTERM, handle_exit)
    signal.signal(signal.SIGINT, handle_exit)

    strip = PixelStrip(LED_COUNT,LED_PIN,LED_FREQ_HZ,
                       LED_DMA,LED_INVERT,LED_BRIGHTNESS,LED_CHANNEL)
    strip.begin()

    t=0
    swirl_speed = 0.03
    vertical_wave_speed = 0.012
    swirl_strength = 7.0

    while running:
        t+=0.03
        for i in range(LED_COUNT):
            theta = thetas[i]
            z_norm = (zs[i] - z_min) / height

            # swirl pattern: wind spiraling up
            wind_phase = theta * swirl_strength + z_norm * 10 - t * 3

            intensity = (math.sin(wind_phase) + 1)/2

            hue = (z_norm*0.5 + t*vertical_wave_speed) % 1.0
            color = vibrant(hue)

            g = int(((color>>16)&0xFF)*intensity)
            r = int(((color>>8)&0xFF)*intensity)
            b = int((color&0xFF)*intensity)

            strip.setPixelColor(i, GRB(r,g,b))

        strip.show()
        time.sleep(0.02)

    # Off on exit
    for i in range(LED_COUNT):
        strip.setPixelColor(i, GRB(0,0,0))
    strip.show()

if __name__ == "__main__":
    main()
