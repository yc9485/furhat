$Python = "$env:LOCALAPPDATA\Programs\Python\Python312\python.exe"
if (-not (Test-Path $Python)) {
    $Python = "python"
}

& $Python -m gym_guide.console_app

