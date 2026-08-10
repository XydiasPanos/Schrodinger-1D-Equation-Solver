@echo off

if "%1"=="deps" (
    echo Installing dependencies...
    pip install --upgrade pip
    pip install -r requirements.txt
    goto end
)

if "%1"=="clean" (
    echo Cleaning build artifacts...
    if exist build rmdir /s /q build
    if exist dist rmdir /s /q dist
    if exist *.spec del /f /q *.spec
    echo Cleaned!
    goto end
)

if "%1"=="run" (
    python main.py
    goto end
)

echo Building Schrodinger1DSolver.exe with custom icon...
pyinstaller --onefile --windowed ^
  --icon=app_icon.ico ^
  --name=Schrodinger1DSolver ^
  --exclude-module torch ^
  --exclude-module onnx ^
  --exclude-module pandas ^
  --exclude-module sympy ^
  --exclude-module IPython ^
  --exclude-module jupyter ^
  --exclude-module PySide6 ^
  --exclude-module PyQt6 ^
  --exclude-module PySide2 ^
  main.py

:end