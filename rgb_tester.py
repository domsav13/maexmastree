import time
import json
import os
from rpi_ws281x import PixelStrip, Color

def RGB(r, g, b):
    return Color(r, g, b)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
COORD_PATH = os.path.join(BASE_DIR, "tree_coords.json")

with open(COORD_PATH, "r") as f:
    coords = json.load(f)

LED_COUNT = len(coords)

LED_PIN        = 18
LED_FREQ_HZ    = 800000
LED_DMA        = 10
LED_BRIGHTNESS = 255     # full brightness
LED_INVERT     = False
LED_CHANNEL    = 0

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

def fill_color(r, g, b):
    print(f"→ Showing RGB ({r}, {g}, {b})")
    for i in range(LED_COUNT):
        strip.setPixelColor(i, RGB(r, g, b))
    strip.show()


def clear():
    for i in range(LED_COUNT):
        strip.setPixelColor(i, RGB(0, 0, 0))
    strip.show()

try:
    print("\nRGB Tester Loaded.")
    print("------------------------------------------------")
    print("Enter an RGB value in format: 255 0 128")
    print("Type 'off' to turn lights off.")
    print("Press Ctrl+C to quit.\n")

    while True:
        user_input = input("RGB > ").strip().lower()

        if user_input == "off":
            clear()
            print("✓ LEDs off.")
            continue

        try:
            r, g, b = map(int, user_input.split())
            if all(0 <= v <= 255 for v in (r, g, b)):
                fill_color(r, g, b)
            else:
                print("⚠ Values must be between 0–255.")
        except:
            print("⚠ Invalid format. Use:  R G B   (example: 255 0 0)")

except KeyboardInterrupt:
    print("\nExiting...")
finally:
    clear()
    print("✓ LEDs cleared and tester script exited.")
