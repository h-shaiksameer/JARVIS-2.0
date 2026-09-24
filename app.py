import os
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent
VENV_PYTHON = PROJECT_ROOT / ".venv" / "Scripts" / "python.exe"

if VENV_PYTHON.exists() and os.path.normcase(os.path.normpath(sys.executable)) != os.path.normcase(os.path.normpath(str(VENV_PYTHON))):
    os.execv(str(VENV_PYTHON), [str(VENV_PYTHON), str(Path(__file__).resolve()), *sys.argv[1:]])

from flask import Flask, render_template, request, Response
import subprocess
from multiprocessing import Value

resume_flag = None
try:
    from myAI import resume_flag as legacy_resume_flag
    resume_flag = legacy_resume_flag
except Exception:
    resume_flag = Value('b', False)

app = Flask(__name__)
process = None  # Global variable to manage the subprocess


@app.route("/")
def index():
    return render_template("index.html")


def get_project_python():
    if VENV_PYTHON.exists():
        return str(VENV_PYTHON)
    return sys.executable


@app.route("/start", methods=["POST"])
def start_jarvis():
    global process
    if not process:
        preferred_targets = ["myAI.py", "jarvis_app.py"]
        launch_target = next((name for name in preferred_targets if os.path.exists(name)), "myAI.py")
        process = subprocess.Popen(
            [get_project_python(), "-u", launch_target],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            cwd=str(PROJECT_ROOT),
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
    if resume_flag is None:
        return {"status": "resume flag unavailable"}
    with resume_flag.get_lock():
        resume_flag.value = True
    return {"status": "Enter pressed"}

@app.route("/logs")
def stream_logs():
    global process
    if not process:
        return "No process running", 400

    visible_prefixes = ("Sameer Boss:", "Jarvis:")

    def generate():
        while True:
            output = process.stdout.readline()
            if output:
                line = output.strip()
                if line.startswith(visible_prefixes):
                    yield f"data: {line}\n\n"
            elif process.poll() is not None:  # Exit if the process ends
                break

    return Response(generate(), mimetype="text/event-stream")



if __name__ == '__main__':
    app.run(host='127.0.0.1', port=7000, debug=False, use_reloader=False)


