import time
import random
import math
import os
import json
import argparse
from rpi_ws281x import PixelStrip, Color

# ----------------------------------------------------
# WS2811 GRB helper
# ----------------------------------------------------
def GRB(r, g, b):
    return Color(g, r, b)

# ----------------------------------------------------
# Parse arguments
# ----------------------------------------------------
parser = argparse.ArgumentParser(description="3D Fireworks Effect for LED Tree")

parser.add_argument("-i", "--interval", type=float, default=0.05,
                    help="Seconds between frames")

parser.add_argument("-d", "--duration", type=float, default=0.6,
                    help="How long each firework lasts before fading out")

parser.add_argument("-s", "--spawn", type=float, default=0.4,
                    help="Probability (0–1) of spawning a new firework each frame")

parser.add_argument("-b", "--blast", type=float, default=0.45,
                    help="Blast radius factor (0–1) scaled by tree size")

args = parser.parse_args()

INTERVAL            = args.interval
FIREWORK_DURATION   = args.duration
SPAWN_CHANCE        = args.spawn
BLAST_RADIUS_FACTOR = args.blast

print(f"\nFireworks parameters:")
print(f"  interval = {INTERVAL}")
print(f"  duration = {FIREWORK_DURATION}")
print(f"  spawn    = {SPAWN_CHANCE}")
print(f"  blast    = {BLAST_RADIUS_FACTOR}\n")

# ----------------------------------------------------
# Load LED coordinates
# ----------------------------------------------------
BASE_DIR    = os.path.dirname(os.path.abspath(__file__))
COORDS_JSON = os.path.join(BASE_DIR, "tree_coords.json")

with open(COORDS_JSON, "r") as f:
    positions = json.load(f)

LED_COUNT = len(positions)
print(f"Loaded {LED_COUNT} LED positions.")

# ----------------------------------------------------
# LED strip setup (WS2811 GRB)
# ----------------------------------------------------
LED_PIN        = 12
LED_FREQ_HZ    = 800000
LED_DMA        = 10
LED_BRIGHTNESS = 150
LED_INVERT     = False
LED_CHANNEL    = 0

strip = PixelStrip(
    LED_COUNT, LED_PIN, LED_FREQ_HZ,
    LED_DMA, LED_INVERT, LED_BRIGHTNESS, LED_CHANNEL
)
strip.begin()

# ----------------------------------------------------
# Helpers
# ----------------------------------------------------
def clear_strip():
    for i in range(LED_COUNT):
        strip.setPixelColor(i, GRB(0,0,0))
    strip.show()

def dist3(p, q):
    return math.dist(p, q)

# ----------------------------------------------------
# Fireworks Animation
# ----------------------------------------------------
def animate_fireworks():

    xs = [p[0] for p in positions]
    ys = [p[1] for p in positions]
    zs = [p[2] for p in positions]

    max_dim = max(max(xs)-min(xs), max(ys)-min(ys), max(zs)-min(zs))
    local_radius = BLAST_RADIUS_FACTOR * max_dim

    # Color groups
    group1 = [(0,255,0),     (69,255,0),  (255,255,0)]
    group2 = [(105,255,180), (0,128,128), (0,0,255)]
    group3 = [(0,0,255),     (255,255,0), (255,255,255)]
    raw_groups = [group1, group2, group3]

    color_groups = [[(r,g,b) for (r,g,b) in grp] for grp in raw_groups]

    active_fireworks = []
    prev_time = time.time()

    try:
        while True:
            now = time.time()
            dt = now - prev_time
            prev_time = now

            # -----------------------------------
            # Possibly spawn a new firework
            # -----------------------------------
            if random.random() < SPAWN_CHANCE:

                center_idx = random.randrange(LED_COUNT)
                cx, cy, cz = positions[center_idx]

                local_leds = [
                    idx for idx, p in enumerate(positions)
                    if dist3(p, (cx,cy,cz)) <= local_radius
                ]

                if not local_leds:
                    local_leds = [center_idx]

                chosen_group = random.choice(color_groups)

                colors = {
                    idx: random.choice(chosen_group)
                    for idx in local_leds
                }

                active_fireworks.append({
                    "local_leds": local_leds,
                    "colors":     colors,
                    "start_time": now,
                    "duration":   FIREWORK_DURATION
                })

            # -----------------------------------
            # Build contribution buffer
            # -----------------------------------
            contributions = [(0,0,0)] * LED_COUNT
            new_active = []

            for fw in active_fireworks:
                age = now - fw["start_time"]

                if age < fw["duration"]:
                    fade = 1 - (age / fw["duration"])

                    for idx in fw["local_leds"]:
                        br, bg, bb = fw["colors"][idx]
                        cr = int(br * fade)
                        cg = int(bg * fade)
                        cb = int(bb * fade)

                        or_, og, ob = contributions[idx]
                        contributions[idx] = (
                            min(or_ + cr, 255),
                            min(og + cg, 255),
                            min(ob + cb, 255)
                        )

                    new_active.append(fw)

            active_fireworks = new_active

            # -----------------------------------
            # Draw frame
            # -----------------------------------
            for i, (r, g, b) in enumerate(contributions):
                strip.setPixelColor(i, GRB(r, g, b))

            strip.show()
            time.sleep(INTERVAL)

    except KeyboardInterrupt:
        print("\nStopping fireworks...")
        clear_strip()

# ----------------------------------------------------
# MAIN
# ----------------------------------------------------
if __name__ == "__main__":
    animate_fireworks()
