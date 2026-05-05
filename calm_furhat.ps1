$Python = "$env:LOCALAPPDATA\Programs\Python\Python312\python.exe"
if (-not (Test-Path $Python)) {
    $Python = "python"
}

& $Python -c "from furhat_realtime_api import FurhatClient; f=FurhatClient('127.0.0.1'); f.connect(); f.request_face_reset(); f.request_face_config(face_id=None, visibility=True, microexpressions=False); f.request_attend_location(0.0, 0.0, 1.0); f.disconnect(); print('Furhat face reset, microexpressions disabled, attention fixed forward.')"

