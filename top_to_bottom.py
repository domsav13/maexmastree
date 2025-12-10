import time
import json
import random
from rpi_ws281x import PixelStrip, Color

# ----------------------------
# LED STRIP CONFIG
# ----------------------------
LED_COUNT      = 500      # Number of LEDs
LED_PIN        = 12      # PWM pin
LED_FREQ_HZ    = 800000
LED_DMA        = 10
LED_BRIGHTNESS = 160      # Limit brightness for power safety
LED_INVERT     = False
LED_CHANNEL    = 0

# ----------------------------
# LOAD 3D COORDINATES
# ----------------------------
with open("tree_coords.json", "r") as f:
    coords = json.load(f)    # list of [x, y, z]

if len(coords) != LED_COUNT:
    raise ValueError(f"Expected {LED_COUNT} coords, got {len(coords)}")

# Extract z values
z_values = [c[2] for c in coords]
z_min = min(z_values)
z_max = max(z_values)

# ----------------------------
# INITIALIZE LED STRIP
# ----------------------------
strip = PixelStrip(
    LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA,
    LED_INVERT, LED_BRIGHTNESS, LED_CHANNEL
)
strip.begin()

# ----------------------------
# COLOR HELPERS (GRB ORDER)
# ----------------------------
def color_grb(r, g, b):
    """WS2811 uses GRB order; this lets us pass (r,g,b) normally."""
    return Color(g, r, b)

WHITE = color_grb(255, 255, 255)
RED   = color_grb(255, 0,   0)
GREEN = color_grb(0,   255, 0)

XMAS_COLORS = [WHITE, RED, GREEN]

# ----------------------------
# CORE EFFECT: VERTICAL BAND SWEEP
# ----------------------------
def clear_strip():
    for i in range(strip.numPixels()):
        strip.setPixelColor(i, color_grb(0, 0, 0))
    strip.show()

def vertical_sweep(
    band_height_frac=0.10,
    step_frac=0.02,
    frame_delay=0.03,
    cycles=0
):
    """
    Vertical 'wipe' from top -> bottom using a horizontal band.

    band_height_frac : fraction of total height for band thickness (0–1)
    step_frac        : fraction of total height to move band each step
    frame_delay      : time between frames [s]
    cycles           : number of top->bottom passes; 0 = infinite
    """
    height = z_max - z_min
    band_height = band_height_frac * height
    step = step_frac * height

    # Sanity clamp
    if band_height <= 0:
        band_height = 0.05 * height
    if step <= 0:
        step = 0.01 * height

    pass_count = 0

    while True:
        # Move band from top (z_max) down to bottom (z_min)
        z_top = z_max
        while z_top >= z_min - band_height:
            z_bottom = z_top - band_height

            # Pick a random Christmas color for this frame
            color = random.choice(XMAS_COLORS)

            # Draw frame: LEDs inside band ON, others OFF
            for idx, z in enumerate(z_values):
                if z_bottom <= z <= z_top:
                    strip.setPixelColor(idx, color)
                else:
                    strip.setPixelColor(idx, color_grb(0, 0, 0))

            strip.show()
            time.sleep(frame_delay)

            z_top -= step

        pass_count += 1
        if cycles > 0 and pass_count >= cycles:
            break

# ----------------------------
# MAIN
# ----------------------------
if __name__ == "__main__":
    try:
        print("Starting vertical top-to-bottom Xmas sweep...")
        clear_strip()
        # cycles=0 → loop forever; set e.g. cycles=5 to stop after 5 passes
        vertical_sweep(
            band_height_frac=0.10,  # 10% of tree height
            step_frac=0.02,         # move 2% height per frame
            frame_delay=0.03,       # 30 ms per frame
            cycles=0
        )

    except KeyboardInterrupt:
        print("\nInterrupted, clearing LEDs...")
        clear_strip()
