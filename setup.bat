@echo off
echo ========================================
echo  Pothole Detection System - Setup
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python ist nicht installiert oder nicht im PATH!
    echo Bitte installieren Sie Python 3.8+ von: https://www.python.org/downloads/
    pause
    exit /b 1
)

echo [1/5] Python gefunden!
echo.

REM Check if Git is installed
git --version >nul 2>&1
if %errorlevel% neq 0 (
    echo WARNING: Git ist nicht installiert!
    echo YOLOv12 Installation wird fehlschlagen ohne Git.
    echo Bitte installieren Sie Git von: https://git-scm.com/download/win
    echo.
    pause
)

echo [2/5] Erstelle Virtual Environment...
python -m venv venv
if %errorlevel% neq 0 (
    echo ERROR: Virtual Environment konnte nicht erstellt werden!
    pause
    exit /b 1
)
echo Virtual Environment erstellt!
echo.

echo [3/5] Aktiviere Virtual Environment...
call venv\Scripts\activate.bat
if %errorlevel% neq 0 (
    echo ERROR: Virtual Environment konnte nicht aktiviert werden!
    pause
    exit /b 1
)
echo.

echo [4/5] Installiere Dependencies...
echo.
echo Upgrade pip...
python -m pip install --upgrade pip

echo.
echo Installiere YOLOv12 (das kann einige Minuten dauern)...
pip install git+https://github.com/sunsmarterjie/yolov12.git
if %errorlevel% neq 0 (
    echo.
    echo WARNING: YOLOv12 Installation fehlgeschlagen!
    echo Möglicherweise ist Git nicht installiert oder nicht im PATH.
    echo Bitte installieren Sie Git, starten Sie das System neu, und führen Sie dieses Script erneut aus.
    echo.
)

echo.
echo Installiere andere Dependencies...
pip install Flask==3.1.2
pip install supervision==0.18.0
pip install "numpy<2.0"
pip install opencv-python
pip install huggingface_hub

echo.
echo [5/5] Installation abgeschlossen!
echo.
echo ========================================
echo  NAECHSTE SCHRITTE:
echo ========================================
echo.
echo 1. Legen Sie Ihr 'best.pt' Modell ins Projektverzeichnis
echo 2. Starten Sie die App mit: python app.py
echo 3. Öffnen Sie im Browser: http://localhost:5000
echo.
echo Bei Problemen siehe: README.md oder INSTALL.md
echo.
pause

