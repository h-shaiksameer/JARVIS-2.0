from __future__ import annotations

import os
import runpy
import traceback


def load_legacy_main():
    try:
        import myAI
        if hasattr(myAI, "main") and callable(myAI.main):
            return myAI.main
    except Exception:
        print("Importing myAI failed. Showing traceback:")
        traceback.print_exc()

    script_path = os.path.join(os.path.dirname(__file__), "myAI.py")
    if os.path.exists(script_path):
        print("Falling back to executing myAI.py directly...")
        try:
            runpy.run_path(script_path, run_name="__main__")
            return None
        except Exception:
            print("Direct execution of myAI.py also failed. Showing traceback:")
            traceback.print_exc()
            raise SystemExit(1)

    print("Failed to load the legacy Jarvis runtime.")
    raise SystemExit(1)


def main() -> None:
    legacy_main = load_legacy_main()
    if legacy_main is None:
        return

    print("Starting Jarvis legacy runtime...")
    legacy_main()


if __name__ == "__main__":
    main()
