import time
import math
import random
import json
import os
import signal
from rpi_ws281x import PixelStrip, Color

def RGB(r, g, b):
    return Color(r, g, b)

running = True
strip = None

def handle_exit(signum, frame):
    global running
    running = False

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
COORD_PATH = os.path.join(BASE_DIR, "tree_coords.json")

with open(COORD_PATH, "r") as f:
    positions = json.load(f)

LED_COUNT = len(positions)


LED_PIN        = 18
LED_FREQ_HZ    = 800000
LED_DMA        = 10
LED_INVERT     = False
LED_CHANNEL    = 0
LED_BRIGHTNESS = 255   # Max brightness


def clear_strip():
    """Turn off all LEDs."""
    for i in range(LED_COUNT):
        strip.setPixelColor(i, RGB(0, 0, 0))
    strip.show()

INTERVAL          = 0.01   # Time between frames
PLANE_SPEED       = 35.0   # Higher = faster movement
THICKNESS_FACTOR  = 0.10   # Plane thickness relative to map range
PAUSE_BETWEEN     = 0.6    # Delay before next plane spawn

def animate_random_planes():

    projections = None
    global running

    while running:

        # ---- Generate random plane direction ----
        A, B, C = random.uniform(-1,1), random.uniform(-1,1), random.uniform(-1,1)
        norm = math.sqrt(A*A + B*B + C*C)
        if norm == 0:
            continue
        A, B, C = A/norm, B/norm, C/norm

        # ---- Compute LED projections onto plane vector ----
        projections = [A*x + B*y + C*z for (x,y,z) in positions]
        min_p, max_p = min(projections), max(projections)
        proj_span = max_p - min_p

        thickness = THICKNESS_FACTOR * proj_span

        # Starting sweep position
        D = min_p - thickness
        end_pos = max_p + thickness

        # Single random color per plane
        R = random.randint(120, 255)
        G = random.randint(120, 255)
        Bv = random.randint(120, 255)
        plane_color = RGB(R, G, Bv)

        prev_time = time.time()

        # ---- Sweep motion loop ----
        while running and D < end_pos:

            now = time.time()
            dt = now - prev_time
            prev_time = now

            for idx, p in enumerate(projections):
                if abs(p - D) <= thickness / 2:
                    strip.setPixelColor(idx, plane_color)
                else:
                    strip.setPixelColor(idx, RGB(0,0,0))

            strip.show()
            time.sleep(INTERVAL)

            D += PLANE_SPEED * dt

        clear_strip()
        time.sleep(PAUSE_BETWEEN)

if __name__ == "__main__":
    signal.signal(signal.SIGTERM, handle_exit)
    signal.signal(signal.SIGINT, handle_exit)

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

    try:
        animate_random_planes()
    finally:
        clear_strip()
        print("\n[+] Random plane animation stopped.")
