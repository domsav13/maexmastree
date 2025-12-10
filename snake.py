import os
import time
import random
import math
import argparse
from rpi_ws281x import PixelStrip, Color
import json

# ---------------------------------------------------
# ARGUMENT PARSING
# ---------------------------------------------------
parser = argparse.ArgumentParser(description="Multi-snake effect on 3D LED tree")
parser.add_argument("-n", "--num-snakes", type=int, default=25,
                    help="Number of independent snakes")
parser.add_argument("-l", "--length", type=int, default=10,
                    help="Length of each snake in LEDs")
parser.add_argument("-d", "--delay", type=float, default=0.1,
                    help="Seconds between frames")
parser.add_argument("-k", "--neighbors", type=int, default=6,
                    help="How many nearest neighbors each LED can move to")
parser.add_argument("--min-bright", type=int, default=50,
                    help="Minimum segment brightness")
parser.add_argument("--max-bright", type=int, default=255,
                    help="Maximum segment brightness")
args = parser.parse_args()

NUM_SNAKES     = args.num_snakes
SNAKE_LENGTH   = args.length
FRAME_DELAY    = args.delay
NEIGHBORS_K    = args.neighbors
MIN_SEG_BRIGHT = args.min_bright
MAX_SEG_BRIGHT = args.max_bright

# ---------------------------------------------------
# LOAD TREE COORDINATES (500 LEDs)
# ---------------------------------------------------
BASE_DIR     = os.path.dirname(os.path.abspath(__file__))
COORDS_JSON  = os.path.join(BASE_DIR, "tree_coords.json")

with open(COORDS_JSON, "r") as f:
    positions = json.load(f)

LED_COUNT = len(positions)
print(f"Loaded {LED_COUNT} coordinates.")

# ---------------------------------------------------
# WS2811 LED STRIP SETUP (GRB FORMAT)
# ---------------------------------------------------
LED_PIN        = 12
LED_FREQ_HZ    = 800000
LED_DMA        = 10
LED_BRIGHTNESS = 255    # we control brightness manually by segments
LED_INVERT     = False
LED_CHANNEL    = 0

strip = PixelStrip(
    LED_COUNT, LED_PIN, LED_FREQ_HZ,
    LED_DMA, LED_INVERT, LED_BRIGHTNESS, LED_CHANNEL
)
strip.begin()

# ---------------------------------------------------
# HELPER: GRB COLOR CREATOR (VERY IMPORTANT!)
# ---------------------------------------------------
def GRB(r, g, b):
    return Color(g, r, b)

# ---------------------------------------------------
# CLEAR STRIP
# ---------------------------------------------------
def clear_strip():
    for i in range(LED_COUNT):
        strip.setPixelColor(i, GRB(0, 0, 0))

# ---------------------------------------------------
# PRECOMPUTE NEAREST NEIGHBORS
# ---------------------------------------------------
print("Precomputing nearest-neighbor graph...")

dist_matrix = []
for i, p in enumerate(positions):
    px, py, pz = p
    dists = []
    for j, q in enumerate(positions):
        if i == j:
            continue
        qx, qy, qz = q
        d = math.sqrt((px-qx)**2 + (py-qy)**2 + (pz-qz)**2)
        dists.append((j, d))
    dists.sort(key=lambda x: x[1])
    dist_matrix.append([idx for idx, _ in dists[:NEIGHBORS_K]])

print("Neighbor graph ready.\n")

# ---------------------------------------------------
# INITIALIZE SNAKES
# ---------------------------------------------------
snakes = []
colors = []

for _ in range(NUM_SNAKES):
    snakes.append([random.randrange(LED_COUNT)])  # random starting LED
    colors.append((
        random.randint(50, 255),   # R
        random.randint(50, 255),   # G
        random.randint(50, 255)    # B
    ))

# ---------------------------------------------------
# CHOOSE NEXT LED FOR THE SNAKE
# ---------------------------------------------------
def choose_next(head, body):
    neighs = dist_matrix[head]
    choices = [n for n in neighs if n not in body]
    return random.choice(choices) if choices else random.choice(neighs)

# ---------------------------------------------------
# MAIN LOOP
# ---------------------------------------------------
try:
    print("Running multi-snake 3D animation...\n")
    while True:

        # UPDATE SNAKES' POSITIONS
        for s in snakes:
            head = s[-1]
            nxt = choose_next(head, s)
            s.append(nxt)

            if len(s) > SNAKE_LENGTH:
                s.pop(0)

        # DRAW FRAME
        clear_strip()

        for idx, s in enumerate(snakes):
            base_r, base_g, base_b = colors[idx]

            for seg_idx, led in enumerate(s):
                frac = seg_idx / (SNAKE_LENGTH - 1)
                bri  = MIN_SEG_BRIGHT + frac * (MAX_SEG_BRIGHT - MIN_SEG_BRIGHT)
                scale = bri / 255.0

                r = int(base_r * scale)
                g = int(base_g * scale)
                b = int(base_b * scale)

                strip.setPixelColor(led, GRB(r, g, b))

        strip.show()
        time.sleep(FRAME_DELAY)

except KeyboardInterrupt:
    print("\nClearing LEDs and exiting...")
    clear_strip()
    strip.show()
