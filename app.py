from flask import Flask, render_template, request, Response
import subprocess
import os
from myAI import resume_flag

app = Flask(__name__)
process = None  # Global variable to manage the subprocess


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/start", methods=["POST"])
def start_jarvis():
    global process
    if not process:
        process = subprocess.Popen(
            [".venv/Scripts/python.exe", "-u", "myAI.py"],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True
            )
    return {"status": "Jarvis started"}


@app.route("/stop", methods=["POST"])
def stop_jarvis():
    global process
    if process:
        process.terminate()
        process = None
    return {"status": "Jarvis stopped"}

@app.route("/enter", methods=["POST"])
def enter_key():
    with resume_flag.get_lock():  # Ensure thread safety
        resume_flag.value = True  # Set the flag
    return {"status": "Enter pressed"}

@app.route("/logs")
def stream_logs():
    global process
    if not process:
        return "No process running", 400

    def generate():
        while True:
            output = process.stdout.readline()
            if output:  # Stream output immediately
                yield f"data: {output.strip()}\n\n"
            elif process.poll() is not None:  # Exit if the process ends
                break

    return Response(generate(), mimetype="text/event-stream")



if __name__ == '__main__':
    app.run(debug=True, port=7000)


