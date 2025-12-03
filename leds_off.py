# leds_off.py
from rpi_ws281x import PixelStrip, Color
import json
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
COORDS_JSON = os.path.join(BASE_DIR, "tree_coords.json")

with open(COORDS_JSON, "r") as f:
    positions = json.load(f)

LED_COUNT = len(positions)

LED_PIN        = 18
LED_FREQ_HZ    = 800000
LED_DMA        = 10
LED_BRIGHTNESS = 255
LED_INVERT     = False
LED_CHANNEL    = 0

strip = PixelStrip(
    LED_COUNT, LED_PIN, LED_FREQ_HZ,
    LED_DMA, LED_INVERT, LED_BRIGHTNESS, LED_CHANNEL
)
strip.begin()

def turn_all_off():
    for i in range(LED_COUNT):
        strip.setPixelColor(i, Color(0,0,0))
    strip.show()

if __name__ == "__main__":
    turn_all_off()
