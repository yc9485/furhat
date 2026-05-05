# Gym Guide Furhat Project

This project is a Python Realtime API application for a Furhat social robot. Furhat acts as a gym guide: it asks a gym-goer about their goal, experience, available time, training focus, and injury status, then recommends a simple workout and gives motivational prompts during the session.

The project is based on `Project_spec (3).pdf` and the HRI lab instructions for using Furhat with Python.

## Project Location

Open PowerShell and load the project folder:

```powershell
cd C:\Users\Lenovo\Documents\Codex\2026-05-05\files-mentioned-by-the-user-project\GymGuideSkill
```

All commands below assume PowerShell is in this folder.

## Files

- `gym_guide/furhat_app.py`: main Furhat Realtime API application.
- `gym_guide/workout.py`: rule-based workout planner.
- `gym_guide/console_app.py`: terminal-only rehearsal version.
- `requirements.txt`: Python dependency list.
- `start_furhat_sdk.ps1`: starts the Furhat SDK server using Furhat's bundled Java.
- `run_furhat.ps1`: runs the robot interaction.
- `run_console.ps1`: runs the terminal rehearsal.
- `calm_furhat.ps1`: resets the virtual face and disables microexpressions.
- `STUDY_DESIGN.md`: research questions, hypotheses, literature grounding, and analysis plan.

## One-Time Requirements

The machine should have:

- Furhat SDK installed.
- Python 3.12 installed.
- `furhat-realtime-api` installed.

If dependencies need to be installed again:

```powershell
C:\Users\Lenovo\AppData\Local\Programs\Python\Python312\python.exe -m pip install -r requirements.txt
```

## Start From Everything Closed

### 1. Open The Project

Open PowerShell and run:

```powershell
cd C:\Users\Lenovo\Documents\Codex\2026-05-05\files-mentioned-by-the-user-project\GymGuideSkill
```

### 2. Start The Furhat SDK Server

PowerShell scripts may be blocked on this computer, so use the bypass command:

```powershell
powershell -ExecutionPolicy Bypass -File .\start_furhat_sdk.ps1
```

Wait about 10 seconds.

### 3. Open The Furhat Web Interface

Open a browser and go to:

```text
http://localhost:8080
```

Password:

```text
admin
```

### 4. Launch Virtual Furhat

In the Furhat web interface, click:

```text
Launch Virtual Furhat
```

The Furhat head opens in a separate window. It is not inside the browser. If you do not see it, use `Alt + Tab` or check the Windows taskbar.

### 5. Enable The Realtime API

In the Furhat web interface, go to:

```text
Realtime API -> Access control
```

Set:

```text
Local network: Enabled
```

Use without authentication if possible. If authentication is enabled, copy the API key.

### 6. Set English Voice If Needed

If Furhat speaks German or another language, change the voice/language in the Furhat web interface:

```text
Settings or Voice -> English / en-US
```

The Python app also requests `en-US` when it connects, but the web UI voice setting can still matter.

### 7. Run The Gym Guide

Without API key:

```powershell
powershell -ExecutionPolicy Bypass -File .\run_furhat.ps1
```

With API key:

```powershell
powershell -ExecutionPolicy Bypass -File .\run_furhat.ps1 -ApiKey YOUR_KEY
```

To run a fixed HRI study condition instead of asking the participant to choose:

```powershell
powershell -ExecutionPolicy Bypass -File .\run_furhat.ps1 -Condition supportive
```

```powershell
powershell -ExecutionPolicy Bypass -File .\run_furhat.ps1 -Condition energetic
```

```powershell
powershell -ExecutionPolicy Bypass -File .\run_furhat.ps1 -Condition neutral
```

Gestures are disabled by default because the Virtual Furhat face can shake or over-act. Only enable them if the simulator is stable:

```powershell
powershell -ExecutionPolicy Bypass -File .\run_furhat.ps1 -Motion
```

Timers are shortened by default so the classroom demo does not take a full workout length. To use real exercise timing:

```powershell
powershell -ExecutionPolicy Bypass -File .\run_furhat.ps1 -RealTiming
```

## How To Interact With Furhat

Wait until Furhat finishes speaking, then answer out loud.

Example demo answers:

```text
yes
I want strength
beginner
thirty minutes
full body
no
yes
next
next
next
```

Expected dialogue:

1. Furhat asks if you want to start.
2. Furhat asks which coaching style to use, unless a fixed condition was provided.
3. Furhat asks for a motivation rating from 1 to 5.
4. Furhat asks your workout goal.
5. Furhat asks your experience level.
6. Furhat asks how many minutes you have.
7. Furhat asks your focus area.
8. Furhat asks if you have pain or injury.
9. Furhat summarizes the workout plan.
10. Furhat asks if you want guidance through the session.
11. For cardio, Furhat gives timed status updates such as minutes completed and minutes left.
12. For lifting, Furhat gives posture cues, asks if you are ready, then counts reps for each set.
13. For plank or holds, Furhat counts down each round.
14. Say `continue`, `ready`, or `stop` when asked.
15. Furhat asks for a final motivation rating and usefulness response.

The app saves study data to:

```text
data/sessions.csv
```

For the report, use `STUDY_DESIGN.md` as the starting point for research questions, hypotheses, and HRI literature framing.

## Guided Workout Behavior

The robot now stays with the user during the workout instead of only giving a plan.

For treadmill or bike exercises, Furhat:

- announces the total duration
- gives progress check-ins
- says how many minutes are left
- asks whether to continue or stop

For lifting exercises, Furhat:

- gives beginner posture instructions
- gives safety warnings
- asks the user to get into position
- counts each rep out loud
- guides each set separately
- reminds the user to rest between sets

For beginners, the robot gives extra detail about posture and injury prevention. Examples include avoiding locked knees on leg press, keeping the back against the chest press pad, and avoiding sharp pain.

## Run Without Furhat

Use this for rehearsal or debugging:

```powershell
powershell -ExecutionPolicy Bypass -File .\run_console.ps1
```

This uses the terminal instead of the robot but follows the same workout logic.

## Troubleshooting

If `.\start_furhat_sdk.ps1` says scripts are disabled, use:

```powershell
powershell -ExecutionPolicy Bypass -File .\start_furhat_sdk.ps1
```

If `http://localhost:8080` does not open, the SDK server is not running. Start it again with the command above.

If the head is missing but `localhost:8080` works, launch Virtual Furhat again from the web interface. The head is a separate window and may be behind the browser.

If the Python app cannot connect, check:

- Virtual Furhat is launched.
- `Realtime API -> Access control -> Local network` is enabled.
- If authentication is enabled, run with `-ApiKey YOUR_KEY`.

If Furhat speaks the wrong language, set the voice to English in the Furhat web UI and rerun:

```powershell
powershell -ExecutionPolicy Bypass -File .\run_furhat.ps1
```

If the virtual face is shaking or making strange eyebrow movements, reset it:

```powershell
powershell -ExecutionPolicy Bypass -File .\calm_furhat.ps1
```

The main app also disables microexpressions and makes Furhat look forward when it connects.

If PowerShell cannot find the scripts, make sure you are in the project folder:

```powershell
cd C:\Users\Lenovo\Documents\Codex\2026-05-05\files-mentioned-by-the-user-project\GymGuideSkill
```

## Safety Note

This robot is not a doctor or professional trainer. It gives a simple demo workout only. If the user reports pain or injury, the robot recommends using light resistance and asking gym staff before continuing.
