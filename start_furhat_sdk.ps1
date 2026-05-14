$SdkRoot = "$env:USERPROFILE\.furhat\launcher\SDK\2.9.1"
$BundledJava = "$env:USERPROFILE\.furhat\launcher\JDK\jdk8u265-b01"

if (-not (Test-Path "$BundledJava\bin\java.exe")) {
    throw "Bundled Furhat Java was not found at $BundledJava"
}

if (-not (Test-Path "$SdkRoot\launchSDK.bat")) {
    throw "Furhat SDK was not found at $SdkRoot"
}

$env:JAVA_HOME = $BundledJava
$env:Path = "$BundledJava\bin;$env:Path"

Start-Process -FilePath "$SdkRoot\launchSDK.bat" -WorkingDirectory $SdkRoot -WindowStyle Hidden
Write-Host "Starting Furhat SDK server from $SdkRoot"
Write-Host "Open http://localhost:8080 after a few seconds."

