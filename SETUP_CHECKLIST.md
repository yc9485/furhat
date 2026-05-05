# Furhat Python Setup Checklist

## Install

1. Install Python 3.12 or newer.
2. Download and start the Furhat SDK Launcher.
3. Start SDK Server.
4. Launch Virtual Furhat.
5. Open `http://localhost:8080`.
6. Go to `Realtime API -> Access control -> Local network`.
7. Enable access, either with authentication or without authentication depending on your lab instructions.
8. Configure microphone and speaker in the web interface.

If the SDK server does not open on `http://localhost:8080`, start it from this project:

```powershell
.\start_furhat_sdk.ps1
```

## Install Python Dependencies

From this folder:

```powershell
python -m pip install -r requirements.txt
```

## Test Without Furhat

```powershell
.\run_console.ps1
```

This dry run uses the same workout planner but speaks through the terminal.

## Run With Furhat

Without API key:

```powershell
.\run_furhat.ps1
```

With API key:

```powershell
.\run_furhat.ps1 -ApiKey YOUR_KEY
```

## User Study Notes

- Keep the routine short for a first demo.
- Ask every participant the same opening questions.
- Log whether they accepted the plan, completed it, and rated it useful.
- Do not collect health details beyond a simple safety check unless your study ethics plan covers it.
