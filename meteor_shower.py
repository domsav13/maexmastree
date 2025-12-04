# meteor_shower.py — 3D meteor shower for 500-LED Christmas tree (WS2811 GRB)

import time
import os
import json
import math
import random
import signal
from rpi_ws281x import PixelStrip, Color

running = True
strip = None

# ----------------------------------------------------------
# WS2811 GRB helper
# ----------------------------------------------------------
def GRB(r, g, b):
    return Color(g, r, b)

def handle_exit(signum, frame):
    global running
    running = False

# ----------------------------------------------------------
# Load 500 LED coordinates
# ----------------------------------------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
with open(os.path.join(BASE_DIR, "tree_coords.json")) as f:
    coords = json.load(f)   # list of [x,y,z]

LED_COUNT = len(coords)
xs = [p[0] for p in coords]
ys = [p[1] for p in coords]
zs = [p[2] for p in coords]

x_min, x_max = min(xs), max(xs)
y_min, y_max = min(ys), max(ys)
z_min, z_max = min(zs), max(zs)

# ----------------------------------------------------------
# LED Strip Init
# ----------------------------------------------------------
LED_PIN = 18
LED_FREQ_HZ = 800000
LED_DMA = 10
LED_BRIGHTNESS = 255
LED_INVERT = False
LED_CHANNEL = 0

# ----------------------------------------------------------
# Utility: distance
# ----------------------------------------------------------
def dist3(p, q):
    return math.sqrt(
        (p[0]-q[0])**2 +
        (p[1]-q[1])**2 +
        (p[2]-q[2])**2
    )

# ----------------------------------------------------------
# Meteor Object
# ----------------------------------------------------------
class Meteor:
    def __init__(self):
        self.reset()

    def reset(self):
        # Spawn somewhere above or to the side
        start_side = random.choice(["top","side"])
        
        if start_side == "top":
            self.pos = [
                random.uniform(x_min, x_max),
                random.uniform(y_min, y_max),
                z_max + random.uniform(5, 20)
            ]
        else:
            # Side-spawn guarantees cool diagonal meteors
            theta = random.uniform(0, 2*math.pi)
            radius = max(x_max, y_max) + 10
            self.pos = [
                radius * math.cos(theta),
                radius * math.sin(theta),
                random.uniform(z_min, z_max)
            ]

        # Random 3D direction downward toward the center
        target = [
            random.uniform(x_min, x_max),
            random.uniform(y_min, y_max),
            random.uniform(z_min - 10, z_max/2)
        ]
        dx = target[0] - self.pos[0]
        dy = target[1] - self.pos[1]
        dz = target[2] - self.pos[2]
        mag = math.sqrt(dx*dx + dy*dy + dz*dz)

        self.dir = [dx/mag, dy/mag, dz/mag]

        # Meteor speed & tail
        self.speed = random.uniform(25, 55)       # movement units/sec
        self.tail = random.uniform(15, 30)        # tail length

        # Color (white, blue-white, ice, gold, cyan)
        palette = [
            (255,255,255),
            (180,220,255),
            (100,180,255),
            (255,240,180),
            (160,255,200)
        ]
        self.color = random.choice(palette)

        self.active = True


    def update(self, dt):
        if not self.active:
            return

        # Move meteor
        self.pos[0] += self.dir[0] * self.speed * dt
        self.pos[1] += self.dir[1] * self.speed * dt
        self.pos[2] += self.dir[2] * self.speed * dt

        # Despawn if below tree or too far
        if (
            self.pos[2] < z_min - 10 or
            math.hypot(self.pos[0], self.pos[1]) > max(x_max,y_max) + 50
        ):
            self.reset()


# ----------------------------------------------------------
# Main meteor shower animation
# ----------------------------------------------------------
def meteor_shower_loop(
    interval=0.015,
    num_meteors=12,
    fade_factor=0.78
):
    # brightness buffer
    buffer = [(0,0,0)] * LED_COUNT

    meteors = [Meteor() for _ in range(num_meteors)]

    prev = time.time()

    while running:
        now = time.time()
        dt = now - prev
        prev = now

        # Fade buffer
        newbuf = []
        for (r,g,b) in buffer:
            nr = int(r * fade_factor)
            ng = int(g * fade_factor)
            nb = int(b * fade_factor)
            newbuf.append((nr, ng, nb))
        buffer = newbuf[:]

        # Update meteors
        for m in meteors:
            m.update(dt)

            # Light trail based on distance to meteor
            for i, (x,y,z) in enumerate(coords):
                d = dist3((x,y,z), m.pos)
                if d < m.tail:
                    t = 1 - d/m.tail
                    R = int(m.color[0] * t)
                    G = int(m.color[1] * t)
                    B = int(m.color[2] * t)

                    old_r, old_g, old_b = buffer[i]
                    buffer[i] = (
                        max(old_r, R),
                        max(old_g, G),
                        max(old_b, B)
                    )

        # Push buffer to LEDs
        for i, (r,g,b) in enumerate(buffer):
            strip.setPixelColor(i, GRB(r,g,b))

        strip.show()
        time.sleep(interval)


# ----------------------------------------------------------
# Entry point
# ----------------------------------------------------------
def main():
    global strip

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

    # Start animation
    try:
        meteor_shower_loop(
            interval=0.015,
            num_meteors=14,
            fade_factor=0.76
        )
    finally:
        # Clear on exit
        for i in range(LED_COUNT):
            strip.setPixelColor(i, GRB(0,0,0))
        strip.show()


if __name__ == "__main__":
    main()
