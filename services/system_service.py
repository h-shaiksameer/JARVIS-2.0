from __future__ import annotations

import os
import subprocess
import webbrowser
from datetime import datetime

from core.config import get_absolute_path


def open_powerpoint() -> None:
    try:
        subprocess.Popen([r"C:\ProgramData\Microsoft\Windows\Start Menu\Programs\PowerPoint.lnk"], shell=True)
    except Exception:
        print("PowerPoint could not be opened.")


def open_chrome() -> None:
    try:
        subprocess.Popen([r"C:\ProgramData\Microsoft\Windows\Start Menu\Programs\Google Chrome.lnk"], shell=True)
    except Exception:
        print("Google Chrome could not be opened.")


def open_cmd() -> None:
    try:
        subprocess.Popen([r"C:\Windows\System32\cmd.exe"])
    except Exception:
        print("Command Prompt could not be opened.")


def open_github() -> None:
    try:
        subprocess.Popen([r"C:\Users\hp\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Chrome Apps\GitHub.lnk"], shell=True)
    except Exception:
        print("GitHub could not be opened.")


def open_instagram() -> None:
    webbrowser.open("https://www.instagram.com/")


def open_linkedin() -> None:
    webbrowser.open("https://www.linkedin.com")


def tell_time() -> str:
    now = datetime.now()
    message = now.strftime("The current time is %I:%M %p")
    print(message)
    return message


def get_weather() -> str:
    # placeholder; delegate to the existing logic in myAI.py later
    print("Weather service is ready for integration.")
    return "Weather service is ready for integration."


def check_battery_status() -> str:
    try:
        import psutil

        battery = psutil.sensors_battery()
        if battery:
            percent = battery.percent
            charging = battery.power_plugged
            return (
                f"Laptop is charging. Battery is at {percent}%"
                if charging
                else f"Laptop is not charging. Battery is at {percent}%"
            )
        return "Battery information is not available."
    except Exception:
        return "Battery information is not available."
