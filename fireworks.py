import time
import random
import math
import os
import json
from rpi_ws281x import PixelStrip, Color

# ----------------------------------------------------
# WS2811 GRB color helper
# ----------------------------------------------------
def GRB(r, g, b):
    return Color(g, r, b)

# ----------------------------------------------------
# Load 500 LED coordinates from JSON
# ----------------------------------------------------
BASE_DIR    = os.path.dirname(os.path.abspath(__file__))
COORDS_JSON = os.path.join(BASE_DIR, "tree_coords.json")

with open(COORDS_JSON, "r") as f:
    positions = json.load(f)

LED_COUNT = len(positions)
print(f"Loaded {LED_COUNT} LED positions.")

# ----------------------------------------------------
# LED strip setup (WS2811, GRB)
# ----------------------------------------------------
LED_PIN        = 18
LED_FREQ_HZ    = 800000
LED_DMA        = 10
LED_BRIGHTNESS = 150    # gentle peak, fireworks fade blending
LED_INVERT     = False
LED_CHANNEL    = 0

strip = PixelStrip(
    LED_COUNT, LED_PIN, LED_FREQ_HZ,
    LED_DMA, LED_INVERT, LED_BRIGHTNESS, LED_CHANNEL
)
strip.begin()

# ----------------------------------------------------
# Clear strip
# ----------------------------------------------------
def clear_strip():
    for i in range(LED_COUNT):
        strip.setPixelColor(i, GRB(0,0,0))
    strip.show()

# ----------------------------------------------------
# 3D distance helper
# ----------------------------------------------------
def dist3(p, q):
    return math.sqrt(
        (p[0]-q[0])**2 +
        (p[1]-q[1])**2 +
        (p[2]-q[2])**2
    )

# ----------------------------------------------------
# Fireworks animation
# ----------------------------------------------------
def animate_fireworks(
    interval=0.05,
    firework_duration=0.5,
    spawn_chance=0.3,
    blast_radius_factor=0.5
):

    # tree bounds
    xs = [p[0] for p in positions]
    ys = [p[1] for p in positions]
    zs = [p[2] for p in positions]

    max_dim = max(max(xs) - min(xs),
                  max(ys) - min(ys),
                  max(zs) - min(zs))

    local_radius = blast_radius_factor * max_dim

    # color groups (RGB → GRB)
    group1 = [(0,255,0), (69,255,0), (255,255,0)]
    group2 = [(105,255,180), (0,128,128), (0,0,255)]
    group3 = [(0,0,255), (255,255,0), (255,255,255)]
    raw_groups = [group1, group2, group3]

    # convert all to GRB tuples
    color_groups = [
        [(r,g,b) for (r,g,b) in grp]
        for grp in raw_groups
    ]

    # active fireworks list
    active_fireworks = []

    prev_time = time.time()

    try:
        while True:
            now = time.time()
            dt  = now - prev_time
            prev_time = now

            # --------------------------
            # Possibly spawn a new firework
            # --------------------------
            if random.random() < spawn_chance:
                center_idx = random.randrange(LED_COUNT)
                cx, cy, cz = positions[center_idx]

                # find all LEDs within radius
                local_leds = []
                for idx, p in enumerate(positions):
                    if dist3(p, (cx,cy,cz)) <= local_radius:
                        local_leds.append(idx)
                if not local_leds:
                    local_leds = [center_idx]

                chosen_group = random.choice(color_groups)

                # assign random colors to each affected LED
                colors = {
                    idx: random.choice(chosen_group)
                    for idx in local_leds
                }

                active_fireworks.append({
                    "local_leds": local_leds,
                    "colors":      colors,
                    "start_time":  now,
                    "duration":    firework_duration
                })

            # --------------------------
            # Prepare contribution buffer
            # --------------------------
            contributions = [(0,0,0)] * LED_COUNT

            # --------------------------
            # Process active fireworks
            # --------------------------
            new_active = []

            for fw in active_fireworks:
                age = now - fw["start_time"]

                if age < fw["duration"]:
                    fade = 1.0 - (age / fw["duration"])

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

            # --------------------------
            # Render frame (GRB!)
            # --------------------------
            for i, (r, g, b) in enumerate(contributions):
                strip.setPixelColor(i, GRB(r, g, b))

            strip.show()
            time.sleep(interval)

    except KeyboardInterrupt:
        print("\nStopping fireworks...")
        clear_strip()


# ----------------------------------------------------
# Run animation
# ----------------------------------------------------
if __name__ == "__main__":
    animate_fireworks(
        interval=0.05,
        firework_duration=0.6,
        spawn_chance=0.4,
        blast_radius_factor=0.45
    )
