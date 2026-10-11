import webbrowser
import os
from features.print_slow_and_speak import print_slow_and_speak


applications = {
    "powerpoint": os.getenv("JARVIS_POWERPOINT_PATH", ""),
    "chrome": os.getenv("JARVIS_CHROME_PATH", ""),
    "github": os.getenv("JARVIS_GITHUB_PATH", ""),
    "whatsapp": os.getenv("JARVIS_WHATSAPP_PATH", ""),
    "cmd": os.getenv("JARVIS_CMD_PATH", "")
}


def open_application(app_name):
    print_slow_and_speak(f"OK Boss....Opening {app_name}")
    try:
        if app_name in applications:
            path = os.path.expandvars(os.path.expanduser(applications[app_name]))
            if not path or not os.path.exists(path):
                print_slow_and_speak(f"{app_name} application is not configured or unavailable.")
                return
            os.startfile(path)
        else:
            print_slow_and_speak(f"{app_name} application could not be opened. Please check the name.")
    except Exception as e:
        print_slow_and_speak(f"{app_name} could not be opened. Error: {e}")

def open_url(url, name):
    print_slow_and_speak(f"OK Boss....Opening Your {name}")
    webbrowser.open(url)

def open_github():
    open_url("https://github.com", "GitHub account")

def open_instagram():
    open_url("https://www.instagram.com/h_shaiksameer", "Instagram account")
