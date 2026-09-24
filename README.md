# JARVIS 2.0
JARVIS 2.0 is a Windows personal assistant written in Python. It combines voice input, speech recognition, text-to-speech, Gemini responses, desktop actions, document utilities, weather/news services, email, calendar, and a small Flask dashboard.

## Current Status
The working runtime is the legacy assistant in `myAI.py`.
- `myAI.py` owns the active startup, microphone loop, command matching, Gemini calls, TTS, and feature dispatch.
- `app.py` provides the Flask dashboard and starts the assistant as a child process.
- `jarvis_app.py` is a compatibility wrapper around `myAI.main()`.
- `core/`, `services/`, and `tools/` contain the beginning of the planned modular architecture. They are not yet the primary runtime.
- Gemini connectivity and credentials must be valid. The tested key has reached its free-tier quota before, which produces HTTP 429 responses even when the local application is healthy.

The project is functional enough for iterative cleanup, but it is not yet a fully modular production application.

## Repository Layout

```text
myAI.py                    Live legacy assistant runtime
app.py                     Flask dashboard and process manager
jarvis_app.py              Legacy runtime compatibility launcher
START_JARVIS.bat           Windows convenience launcher
features/                  Legacy feature implementations
core/                      Planned assistant orchestration and routing
services/                  Planned external service wrappers
tools/                     Planned reusable audio and system tools
agents/                    Experimental agent layer
templates/                 Flask HTML templates
static/                    Flask static assets
media/                     Startup, response, and feature audio/video
temp/                      Temporary generated audio files
JarvisResponse/            Generated assistant response audio
MyVoice/                   Voice-related project output
tests/                     Early smoke/integration tests
requirements.txt           Existing broad dependency inventory
requirements.fixed.txt     Clean install list used during environment repair
```

## Runtime Flow

```text
Flask dashboard
    |
    +-- app.py starts .venv/Scripts/python.exe
            |
            +-- myAI.py
                    |
                    +-- record microphone audio
                    +-- save temporary WAV under temp/
                    +-- ignore silent audio
                    +-- SpeechRecognition transcription
                    +-- custom command matching
                    +-- Gemini HTTP request for unknown commands
                    +-- TTS and audio playback
```

The Flask log stream intentionally exposes only lines beginning with `Sameer Boss:` and `Jarvis:`. Startup diagnostics, dependency warnings, and tracebacks remain in the terminal rather than the dashboard.

## Requirements

- Windows
- Python 3.12.x recommended
- A working microphone and speaker
- FFmpeg available on `PATH` for media features that use it
- A valid Gemini API key for AI responses
- Optional service credentials for email, weather, news, and Google Calendar

The project should use this interpreter:

```text
C:\Users\hp\Desktop\JARVIS2.0\.venv\Scripts\python.exe
```

Always prefer the explicit interpreter path. It avoids accidentally running the system Python or an incomplete environment.

## Setup

Open PowerShell in the repository root.

```powershell
cd C:\Users\hp\Desktop\JARVIS2.0
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install --upgrade pip setuptools wheel
.\.venv\Scripts\python.exe -m pip install -r requirements.fixed.txt
```

If the environment already exists, do not recreate it while Python, Flask, or JARVIS processes are running. Stop those processes first.

The dependency list is broad because the legacy features import many optional libraries. The next architecture phase should split this into a small core install and optional feature groups.

## Environment Variables

Create a `.env` file in the repository root. Never commit this file or real credentials.

```env
API_KEY=your_gemini_api_key
GEMINI_API_KEY=your_gemini_api_key
GOOGLE_API_KEY=your_google_api_key
OPENWEATHER_API_KEY=your_openweather_api_key
NEWS_API_KEY=your_news_api_key
EMAIL=your_email_address
EMAIL_APP_PASSWORD=your_email_app_password
```

`API_KEY` is the primary variable currently read by `myAI.py`. The modular Gemini service also accepts `GOOGLE_API_KEY` and `GEMINI_API_KEY`.

## Running JARVIS

### Direct assistant runtime

Use this when debugging the voice and Gemini pipeline:

```powershell
cd C:\Users\hp\Desktop\JARVIS2.0
.\.venv\Scripts\python.exe myAI.py
```

### Compatibility launcher

```powershell
.\.venv\Scripts\python.exe jarvis_app.py
```

### Flask dashboard

```powershell
.\.venv\Scripts\python.exe app.py
```

Then open http://127.0.0.1:7000.

The dashboard starts and stops the assistant process and streams the filtered user/JARVIS conversation. Stop the Flask server with `Ctrl+C` before recreating the virtual environment or changing runtime files.

### Batch launcher

`START_JARVIS.bat` is available for convenience, but the explicit venv commands above are the reliable debugging path.

## Supported Interaction Examples

### Conversation

- `who are you`
- `what is my name`
- General questions are sent to Gemini.

### Applications and desktop actions

- `open PowerPoint`
- `open Chrome`
- `open GitHub`
- `open WhatsApp`
- `open Instagram`
- `open Gmail`
- `open command`

### Information and utilities

- `what is time now`
- `check battery status`
- `check weather`
- `location`
- `jarvis check internet speed`
- `read PDF`
- `give me news headlines`

### Productivity

- `send email`
- `check my schedule`
- `add event`
- `create a document`
- `write code for me`

### Lifecycle

- `jarvis stop`
- `stop it jarvis`
- `goodbye jarvis`

## Validation Checklist

Run checks in this order when debugging:

1. Confirm the interpreter:

    ```powershell
    .\.venv\Scripts\python.exe -c "import sys; print(sys.executable); print(sys.version)"
    ```

2. Check the main runtime imports:

    ```powershell
    .\.venv\Scripts\python.exe -c "import myAI; print('MYAI_IMPORT_OK')"
    ```

3. Test Gemini independently before launching the voice loop.
4. Test TTS and microphone capture independently.
5. Run `myAI.py` directly and confirm the startup greeting.
6. Run `app.py` and test the dashboard process controls.

The known-good startup sequence is:

```text
JARVIS startup: audio services ready.
Good evening
Welcome Back Boss, All Systems are fully operational
JARVIS is ready for commands.
Listening to You Boss...
```

## Known Limitations

- The legacy runtime still imports many services at module load time.
- `google.generativeai` is deprecated; the live legacy path currently uses it for model compatibility, while `services/gemini_service.py` sketches the newer `google.genai` client.
- Gemini responses depend on API quota, account billing, model availability, and network access. HTTP 429 means the key quota is exhausted, not that the local runtime is broken.
- Whisper is optional in the current runtime. Active transcription uses SpeechRecognition with Google Web Speech.
- SpeechRecognition returns no command for silence; it does not invent the previous `JARVIS listen to me` fallback anymore.
- Some desktop, calendar, email, WhatsApp, and media features require external applications, credentials, permissions, or FFmpeg.
- The Flask server is a local development server, not a production deployment.
- The current command router is mostly phrase matching in `myAI.py`; it should eventually move into `core/command_router.py`.

## Structural Improvement Roadmap

The next refactor should be incremental so the working voice runtime remains available.

### Phase 1: Stabilize the current runtime

- Keep `myAI.py` runnable as a compatibility entrypoint.
- Centralize paths, model names, timeouts, and feature flags.
- Replace broad imports and wildcard imports with explicit imports.
- Add focused tests for silence, transcription errors, cleanup, command routing, and Gemini quota errors.
- Separate terminal diagnostics from dashboard conversation output.

### Phase 2: Extract core services

- Move microphone capture to an STT/audio service.
- Move TTS and playback to a single audio service.
- Move Gemini HTTP calls into `services/gemini_service.py`.
- Move environment loading and path management into `core/config.py`.
- Move phrase matching and command dispatch into `core/command_router.py`.

### Phase 3: Extract feature tools

- Create independent tools for applications, weather, news, email, calendar, documents, and system controls.
- Give each tool a narrow input/output contract.
- Make optional integrations lazy-loaded so one missing service cannot prevent startup.
- Add structured error results instead of printing errors from deep feature functions.

### Phase 4: Make the modular runtime primary

- Have `core/assistant.py` own the main loop.
- Register tools through the router.
- Keep `myAI.py` as a compatibility wrapper during migration.
- Add integration tests for the full command lifecycle.
- Only then remove duplicated legacy implementations.

## Security Notes

- Do not commit `.env`, API keys, email passwords, OAuth tokens, or generated personal documents.
- Rotate any credential that has been exposed outside the local machine.
- Restrict destructive commands such as shutdown and restart behind explicit confirmation.
- Validate file paths before reading or writing user files.
- Avoid passing unrestricted user text directly into shell commands.

## Contributing to the Next Plan

Before the next refactor, agree on:

- which runtime should become primary
- which features are essential versus optional
- whether Google Web Speech or a local STT engine should be preferred
- the desired Gemini client and model policy
- how commands, tools, errors, and logs should be represented
- the minimum test suite required before each migration step

This README describes the repository as it currently exists. It is intended to be the baseline for the next structural improvement plan.
