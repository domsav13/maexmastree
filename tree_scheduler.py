#!/usr/bin/env python3
import os
import time
import random
import subprocess
from datetime import datetime
import pytz

# -----------------------------
# CONFIGURATION
# -----------------------------
ANIMATION_DIR = "/home/dsavarino/maexmastree"
ANIMATION_DURATION = 30 * 60     # 30 minutes

# *** FIXED FOR 9 AM → 12 AM EST ***
EST = pytz.timezone("America/New_York")
ACTIVE_START = 9                 # 9 AM EST
ACTIVE_END = 24                 # Midnight EST

PYTHON = "/usr/bin/python3"

# Animations to select from (filenames inside ANIMATION_DIR)
ANIMATIONS = [
    "wind_swirl.py",
    "double_helix.py",
    "snake.py",
    "matrix_rain.py",
    "fireworks.py",
    "contagious.py",
    "candy_cane.py",
    "light_beams.py",
    "top_to_bottom.py",
    "random_plane.py"
]

OFF_SCRIPT = "leds_off.py"

# -----------------------------
# HELPER FUNCTIONS
# -----------------------------
def tree_should_be_on():
    """Check if current time in EST falls between ACTIVE_START and ACTIVE_END."""
    now_est = datetime.now(EST)
    hour = now_est.hour
    return ACTIVE_START <= hour < ACTIVE_END


def start_animation(anim_path):
    print(f"[Scheduler] Starting animation: {anim_path}")
    return subprocess.Popen([PYTHON, anim_path])


def stop_animation(proc):
    if proc and proc.poll() is None:
        print("[Scheduler] Stopping current animation...")
        proc.terminate()
        try:
            proc.wait(timeout=3)
        except subprocess.TimeoutExpired:
            proc.kill()


def turn_off_leds():
    print("[Scheduler] Turning LEDs OFF")
    subprocess.call([PYTHON, os.path.join(ANIMATION_DIR, OFF_SCRIPT)])


# -----------------------------
# MAIN LOOP
# -----------------------------
def main():

    current_proc = None
    last_switch_time = 0

    while True:
        try:
            now = time.time()

            # TIME CHECK FIXED (EST)
            if not tree_should_be_on():

                if current_proc:
                    stop_animation(current_proc)
                    current_proc = None

                turn_off_leds()
                time.sleep(60)
                continue

            if current_proc is None:
                anim = random.choice(ANIMATIONS)
                anim_path = os.path.join(ANIMATION_DIR, anim)
                current_proc = start_animation(anim_path)
                last_switch_time = now

            if now - last_switch_time >= ANIMATION_DURATION:
                stop_animation(current_proc)
                anim = random.choice(ANIMATIONS)
                anim_path = os.path.join(ANIMATION_DIR, anim)
                current_proc = start_animation(anim_path)
                last_switch_time = now

            time.sleep(5)

        except Exception as e:
            print(f"[Scheduler] ERROR: {e}")
            time.sleep(5)


if __name__ == "__main__":
    main()
