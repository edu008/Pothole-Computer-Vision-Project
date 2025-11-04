#!/bin/bash

echo "========================================"
echo " Pothole Detection System - Setup"
echo "========================================"
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 ist nicht installiert!"
    echo "Ubuntu/Debian: sudo apt install python3 python3-venv python3-pip"
    echo "macOS: brew install python@3.11"
    exit 1
fi

echo "[1/5] Python gefunden!"
echo ""

# Check if Git is installed
if ! command -v git &> /dev/null; then
    echo "WARNING: Git ist nicht installiert!"
    echo "YOLOv12 Installation wird fehlschlagen ohne Git."
    echo "Ubuntu/Debian: sudo apt install git"
    echo "macOS: brew install git"
    echo ""
    read -p "Drücken Sie Enter zum Fortfahren..."
fi

echo "[2/5] Erstelle Virtual Environment..."
python3 -m venv venv
if [ $? -ne 0 ]; then
    echo "ERROR: Virtual Environment konnte nicht erstellt werden!"
    exit 1
fi
echo "Virtual Environment erstellt!"
echo ""

echo "[3/5] Aktiviere Virtual Environment..."
source venv/bin/activate
if [ $? -ne 0 ]; then
    echo "ERROR: Virtual Environment konnte nicht aktiviert werden!"
    exit 1
fi
echo ""

echo "[4/5] Installiere Dependencies..."
echo ""
echo "Upgrade pip..."
python -m pip install --upgrade pip

echo ""
echo "Installiere YOLOv12 (das kann einige Minuten dauern)..."
pip install git+https://github.com/sunsmarterjie/yolov12.git
if [ $? -ne 0 ]; then
    echo ""
    echo "WARNING: YOLOv12 Installation fehlgeschlagen!"
    echo "Möglicherweise ist Git nicht installiert."
    echo "Bitte installieren Sie Git und führen Sie dieses Script erneut aus."
    echo ""
fi

echo ""
echo "Installiere andere Dependencies..."
pip install Flask==3.1.2
pip install supervision==0.18.0
pip install "numpy<2.0"
pip install opencv-python
pip install huggingface_hub

echo ""
echo "[5/5] Installation abgeschlossen!"
echo ""
echo "========================================"
echo " NAECHSTE SCHRITTE:"
echo "========================================"
echo ""
echo "1. Legen Sie Ihr 'best.pt' Modell ins Projektverzeichnis"
echo "2. Aktivieren Sie das Virtual Environment: source venv/bin/activate"
echo "3. Starten Sie die App: python app.py"
echo "4. Öffnen Sie im Browser: http://localhost:5000"
echo ""
echo "Bei Problemen siehe: README.md oder INSTALL.md"
echo ""

