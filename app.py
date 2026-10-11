import os
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent
VENV_PYTHON = PROJECT_ROOT / ".venv" / "Scripts" / "python.exe"

if VENV_PYTHON.exists() and os.path.normcase(os.path.normpath(sys.executable)) != os.path.normcase(os.path.normpath(str(VENV_PYTHON))):
    os.execv(str(VENV_PYTHON), [str(VENV_PYTHON), str(Path(__file__).resolve()), *sys.argv[1:]])

from flask import Flask, jsonify, render_template, request, Response
import subprocess
import json
from datetime import datetime
from multiprocessing import Value
import requests

from core.application import AssistantApplication
from core.command_router import CommandRouter
from core.config import AppConfig
from services.gemini import GeminiService

app_config = AppConfig.from_environment()
dashboard_application = AssistantApplication(CommandRouter(), GeminiService(app_config))
resume_flag = Value('b', False)

app = Flask(__name__)
process = None  # Global variable to manage the subprocess
runtime_state = {"state": "stopped", "detail": "Assistant is offline."}
HOLOGRAPHIC_LOCK = PROJECT_ROOT / "temp" / "holographic.active"
HOLOGRAPHIC_LOCK.unlink(missing_ok=True)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/holographic")
def holographic():
    return render_template("holographic.html")


@app.route("/holographic/activate", methods=["POST"])
def activate_holographic():
    HOLOGRAPHIC_LOCK.parent.mkdir(parents=True, exist_ok=True)
    HOLOGRAPHIC_LOCK.write_text("active", encoding="utf-8")
    return jsonify({"active": True})


@app.route("/holographic/deactivate", methods=["POST"])
def deactivate_holographic():
    HOLOGRAPHIC_LOCK.unlink(missing_ok=True)
    return jsonify({"active": False})


@app.route("/holographic/status")
def holographic_status():
    return jsonify({"active": HOLOGRAPHIC_LOCK.exists()})


def get_project_python():
    if VENV_PYTHON.exists():
        return str(VENV_PYTHON)
    return sys.executable


@app.route("/start", methods=["POST"])
def start_jarvis():
    global process, runtime_state
    if process is None or process.poll() is not None:
        preferred_targets = ["myAI.py", "jarvis_app.py"]
        launch_target = next((name for name in preferred_targets if os.path.exists(name)), "myAI.py")
        process = subprocess.Popen(
            [get_project_python(), "-u", launch_target],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            cwd=str(PROJECT_ROOT),
        )
        runtime_state = {"state": "starting", "detail": "Starting assistant services..."}
    return {"status": "Jarvis started"}


@app.route("/stop", methods=["POST"])
def stop_jarvis():
    global process, runtime_state
    if process:
        process.terminate()
        process = None
    runtime_state = {"state": "stopped", "detail": "Assistant is offline."}
    HOLOGRAPHIC_LOCK.unlink(missing_ok=True)
    return {"status": "Jarvis stopped"}


@app.route("/restart", methods=["POST"])
def restart_jarvis():
    stop_jarvis()
    return start_jarvis()


@app.route("/status")
def assistant_status():
    running = process is not None and process.poll() is None
    state = dashboard_application.health()
    state.update({
        "running": running,
        "pid": process.pid if running else None,
        "runtime_state": runtime_state,
    })
    return jsonify(state)


@app.route("/environment")
def environment_snapshot():
    latitude = request.args.get("lat", type=float)
    longitude = request.args.get("lon", type=float)
    result = {
        "time": datetime.now().astimezone().strftime("%I:%M:%S %p"),
        "date": datetime.now().astimezone().strftime("%A, %d %B %Y"),
        "location": "Location unavailable",
        "weather": "Weather unavailable",
    }
    if latitude is None or longitude is None:
        return jsonify(result)

    result["location"] = f"{latitude:.3f}, {longitude:.3f}"
    if not app_config.openweather_api_key:
        return jsonify(result)
    try:
        response = requests.get(
            "https://api.openweathermap.org/data/2.5/weather",
            params={
                "lat": latitude,
                "lon": longitude,
                "appid": app_config.openweather_api_key,
                "units": "metric",
            },
            timeout=5,
        )
        response.raise_for_status()
        data = response.json()
        city = data.get("name") or result["location"]
        description = data.get("weather", [{}])[0].get("description", "Unknown")
        temperature = data.get("main", {}).get("temp")
        result["location"] = city
        result["weather"] = f"{temperature:.1f} C, {description}" if isinstance(temperature, (int, float)) else description
    except (requests.RequestException, ValueError, TypeError, KeyError):
        pass
    return jsonify(result)


@app.route("/command", methods=["POST"])
def text_command():
    body = request.get_json(silent=True) or {}
    command = str(body.get("command", "")).strip()
    if not command:
        return jsonify({"error": "command is required"}), 400
    response = dashboard_application.handle_text(command)
    return jsonify({"input": command, "response": response.text, "source": response.source})

@app.route("/enter", methods=["POST"])
def enter_key():
    with resume_flag.get_lock():
        resume_flag.value = True
    return {"status": "Enter pressed"}

@app.route("/logs")
def stream_logs():
    global process, runtime_state
    if not process:
        return "No process running", 400

    visible_prefixes = ("Sameer Boss:", "Jarvis:")

    def generate():
        while True:
            output = process.stdout.readline()
            if output:
                line = output.strip()
                if line.startswith("JARVIS_STATE:"):
                    try:
                        runtime_state = json.loads(line.split(":", 1)[1].strip())
                        yield f"event: state\ndata: {json.dumps(runtime_state)}\n\n"
                    except json.JSONDecodeError:
                        pass
                elif line.startswith(visible_prefixes):
                    yield f"data: {line}\n\n"
            elif process.poll() is not None:  # Exit if the process ends
                break

    return Response(generate(), mimetype="text/event-stream")



if __name__ == '__main__':
    app.run(host='127.0.0.1', port=7000, debug=False, use_reloader=False)


