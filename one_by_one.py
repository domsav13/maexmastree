import time
from rpi_ws281x import PixelStrip, Color

# ----------------------------
# LED STRIP CONFIGURATION
# ----------------------------
LED_COUNT      = 500      # Number of LEDs in your strip
LED_PIN        = 18       # GPIO pin (18 uses PWM!)
LED_FREQ_HZ    = 800000   # LED signal frequency
LED_DMA        = 10       # DMA channel to use
LED_BRIGHTNESS = 255      # Max brightness
LED_INVERT     = False    # True if using a transistor/inverting circuit
LED_CHANNEL    = 0        # Use channel 0 for GPIO 18

# ----------------------------
# INITIALIZE STRIP
# ----------------------------
strip = PixelStrip(
    LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA,
    LED_INVERT, LED_BRIGHTNESS, LED_CHANNEL
)
strip.begin()

# ----------------------------
# LIGHT LEDs ONE BY ONE
# ----------------------------
def light_up_one_by_one(wait_ms=50):
    """Turn on each LED one by one (walking pixel)."""
    while True:
        for i in range(strip.numPixels()):
            # Turn off all LEDs
            for j in range(strip.numPixels()):
                strip.setPixelColor(j, Color(0, 0, 0))

            # Light the current LED (red example)
            strip.setPixelColor(i, Color(255, 0, 0))
            strip.show()

            time.sleep(wait_ms/1000.0)

try:
    light_up_one_by_one(wait_ms=30)

except KeyboardInterrupt:
    # Clean shutdown — turn everything off
    for i in range(strip.numPixels()):
        strip.setPixelColor(i, Color(0, 0, 0))
    strip.show()
    print("\nStopped. LEDs cleared.")
