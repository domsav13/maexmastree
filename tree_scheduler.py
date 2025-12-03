#!/usr/bin/env python3
import os
import time
import random
import subprocess
from datetime import datetime

# -----------------------------
# CONFIGURATION
# -----------------------------
ANIMATION_DIR = "/home/dsavarino/maexmastree"
ANIMATION_DURATION = 30 * 60     # 30 minutes
ACTIVE_START = 16                # Start time (4 PM)
ACTIVE_END = 23                  # End time (11 PM)

PYTHON = "/usr/bin/python3"      # Use system python for WS2811

# Animations to select from (filenames inside ANIMATION_DIR)
ANIMATIONS = [
    "double_helix.py",
    "wind_swirl.py",
    "snowfall.py",
    "top_to_bottom.py",
    "snake.py"
]

# Script to turn LEDs off instantly
OFF_SCRIPT = "leds_off.py"


# -----------------------------
# HELPER FUNCTIONS
# -----------------------------
def tree_should_be_on():
    """Check if current time falls between ACTIVE_START and ACTIVE_END."""
    hour = datetime.now().hour
    return ACTIVE_START <= hour < ACTIVE_END


def start_animation(anim_path):
    """Launch animation as subprocess (non-blocking)."""
    print(f"[Scheduler] Starting animation: {anim_path}")
    return subprocess.Popen([PYTHON, anim_path])


def stop_animation(proc):
    """Terminate a running animation."""
    if proc and proc.poll() is None:
        print("[Scheduler] Stopping current animation...")
        proc.terminate()
        try:
            proc.wait(timeout=3)
        except subprocess.TimeoutExpired:
            proc.kill()


def turn_off_leds():
    """Run LED off script."""
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

            if not tree_should_be_on():
                # Outside active hours → turn off LEDs
                if current_proc:
                    stop_animation(current_proc)
                    current_proc = None
                turn_off_leds()
                time.sleep(60)  # check once per minute
                continue

            # If tree should be on but no animation running → start one
            if current_proc is None:
                anim = random.choice(ANIMATIONS)
                anim_path = os.path.join(ANIMATION_DIR, anim)
                current_proc = start_animation(anim_path)
                last_switch_time = now

            # Has the animation been running for 30 min?
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
