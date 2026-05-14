param(
    [string]$HostAddress = "127.0.0.1",
    [string]$ApiKey = "",
    [ValidateSet("ask", "supportive", "neutral")]
    [string]$Condition = "ask",
    [switch]$Motion,
    [switch]$RealTiming
)

$Python = "$env:LOCALAPPDATA\Programs\Python\Python312\python.exe"
if (-not (Test-Path $Python)) {
    $Python = "python"
}

if ($ApiKey) {
    $Args = @("-m", "gym_guide.furhat_app", "--host", $HostAddress, "--api-key", $ApiKey, "--condition", $Condition)
    if ($Motion) {
        $Args += "--motion"
    }
    if ($RealTiming) {
        $Args += "--real-timing"
    }
    & $Python @Args
} else {
    $Args = @("-m", "gym_guide.furhat_app", "--host", $HostAddress, "--condition", $Condition)
    if ($Motion) {
        $Args += "--motion"
    }
    if ($RealTiming) {
        $Args += "--real-timing"
    }
    & $Python @Args
}
