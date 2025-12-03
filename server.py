from flask import Flask, render_template, jsonify
import subprocess
import time
import signal

app = Flask(__name__)

current_process = None

def stop_current_animation():
    global current_process
    if current_process is not None:
        current_process.send_signal(signal.SIGTERM)
        current_process = None

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/turn_on", methods=["POST"])
def turn_on():
    global current_process

    stop_current_animation()  # stop old animation
    time.sleep(0.1)

    # start animation as root
    current_process = subprocess.Popen(
        ["sudo", "python3", "top_to_bottom.py"]
    )

    return jsonify({"status": "ON"})

@app.route("/turn_off", methods=["POST"])
def turn_off():
    global current_process

    stop_current_animation()
    time.sleep(0.1)

    subprocess.run(["sudo", "python3", "leds_off.py"])

    return jsonify({"status": "OFF"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
