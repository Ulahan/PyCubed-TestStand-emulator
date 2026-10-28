@echo off
cd /d %~dp0\..
if "%~1"=="" (
  echo Usage: RUN_EMULATOR.bat OPERATOR_ID [SERIAL_NUMBER]
  exit /b 1
)
if "%~2"=="" (
  python -m emulator.sequence_runner --operator "%~1"
) else (
  python -m emulator.sequence_runner --operator "%~1" --serial "%~2"
)
pause
