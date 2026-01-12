#!/usr/bin/env python3
import os
import time
import random
import subprocess
from datetime import datetime, timedelta
import pytz

# -----------------------------
# CONFIGURATION
# -----------------------------
ANIMATION_DIR = "/home/dsavarino/maexmastree"
ANIMATION_DURATION = 30 * 60     # 30 minutes

# Run daily from 9:00 AM -> 10:00 PM Eastern
EST = pytz.timezone("America/New_York")
ACTIVE_START_HOUR = 9            # 9 AM
ACTIVE_END_HOUR = 22             # 10 PM (22:00)

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
    """True if current EST time is between 09:00 and 22:00."""
    now_est = datetime.now(EST)
    start = now_est.replace(hour=ACTIVE_START_HOUR, minute=0, second=0, microsecond=0)
    end = now_est.replace(hour=ACTIVE_END_HOUR, minute=0, second=0, microsecond=0)
    return start <= now_est < end


def seconds_until_next_window_check():
    """
    When OFF-hours, sleep until the next meaningful boundary
    (either today's start time or tomorrow's start time).
    """
    now_est = datetime.now(EST)
    today_start = now_est.replace(hour=ACTIVE_START_HOUR, minute=0, second=0, microsecond=0)
    today_end = now_est.replace(hour=ACTIVE_END_HOUR, minute=0, second=0, microsecond=0)

    if now_est < today_start:
        target = today_start
    else:
        # After end time -> next day's start
        target = today_start + timedelta(days=1)

    return max(5, int((target - now_est).total_seconds()))


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
    leds_are_off = False

    while True:
        try:
            now = time.time()

            # OFF HOURS
            if not tree_should_be_on():
                if current_proc:
                    stop_animation(current_proc)
                    current_proc = None

                # Only run leds_off once per off-period (avoids spamming it)
                if not leds_are_off:
                    turn_off_leds()
                    leds_are_off = True

                sleep_s = seconds_until_next_window_check()
                print(f"[Scheduler] Outside active window. Sleeping {sleep_s} seconds...")
                time.sleep(sleep_s)
                continue

            # ON HOURS
            leds_are_off = False

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
