from flask import Flask, render_template, jsonify
import threading
import subprocess
import time

import top_to_bottom
import leds_off

app = Flask(__name__)

animation_thread = None

def run_animation():
    top_to_bottom.run_top_to_bottom()

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/turn_on", methods=["POST"])
def turn_on():
    global animation_thread

    # stop previous animation if running
    top_to_bottom.running = False
    time.sleep(0.1)

    # turn off LEDs before starting new animation
    leds_off.turn_all_off()

    # start new animation thread
    animation_thread = threading.Thread(target=run_animation)
    animation_thread.daemon = True
    animation_thread.start()

    return jsonify({"status": "ON"})

@app.route("/turn_off", methods=["POST"])
def turn_off():
    global animation_thread

    # stop animation
    top_to_bottom.running = False
    time.sleep(0.1)

    # turn all LEDs off
    leds_off.turn_all_off()

    return jsonify({"status": "OFF"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
