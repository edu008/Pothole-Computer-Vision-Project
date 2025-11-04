# 📦 Detaillierte Installationsanleitung

Diese Anleitung führt Sie Schritt für Schritt durch die Installation des Pothole Detection Systems.

---

## 🖥️ System-Anforderungen

### **Minimum:**
- CPU: Intel i5 / AMD Ryzen 5 oder besser
- RAM: 8 GB
- Webcam: USB oder integriert
- OS: Windows 10/11, Linux (Ubuntu 20.04+), macOS 10.15+

### **Empfohlen:**
- CPU: Intel i7 / AMD Ryzen 7
- RAM: 16 GB
- GPU: NVIDIA RTX 2060 oder besser (mit CUDA)
- Webcam: 720p oder höher

---

## 1️⃣ Python Installation

### **Windows:**

1. Download: [Python 3.11](https://www.python.org/downloads/)
2. Installation:
   - ✅ **"Add Python to PATH"** aktivieren!
   - "Install Now" klicken
3. Überprüfung:
```cmd
python --version
```
Sollte zeigen: `Python 3.11.x`

### **Linux (Ubuntu/Debian):**

```bash
sudo apt update
sudo apt install python3.11 python3.11-venv python3-pip
python3.11 --version
```

### **macOS:**

```bash
brew install python@3.11
python3.11 --version
```

---

## 2️⃣ Git Installation

### **Windows:**

1. Download: [Git for Windows](https://git-scm.com/download/win)
2. Installation mit Standard-Einstellungen
3. **PowerShell NEU STARTEN** nach Installation!
4. Überprüfung:
```cmd
git --version
```

### **Linux:**

```bash
sudo apt install git
git --version
```

### **macOS:**

```bash
brew install git
git --version
```

---

## 3️⃣ Projekt Setup

### **Repository klonen:**

```bash
git clone https://github.com/IHR_USERNAME/Pothole-Computer-Vision-Project.git
cd Pothole-Computer-Vision-Project
```

**ODER ZIP herunterladen:**
1. GitHub → "Code" → "Download ZIP"
2. Entpacken
3. Terminal im Ordner öffnen

---

## 4️⃣ Virtual Environment

### **Windows (PowerShell):**

```powershell
# Virtual Environment erstellen
python -m venv venv

# Falls PowerShell-Fehler: Execution Policy ändern
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# Aktivieren
.\venv\Scripts\Activate.ps1
```

**Alternativ CMD:**
```cmd
python -m venv venv
venv\Scripts\activate.bat
```

### **Linux/Mac:**

```bash
python3 -m venv venv
source venv/bin/activate
```

**Erfolg?** Prompt zeigt `(venv)` vor dem Pfad!

---

## 5️⃣ Dependencies installieren

### **Schritt 1: Pip upgraden**

```bash
python -m pip install --upgrade pip
```

### **Schritt 2: YOLOv12 installieren**

⚠️ **WICHTIG:** Das ist NICHT das Standard-Ultralytics! Wir brauchen den YOLOv12-Fork!

```bash
# Falls Standard-Ultralytics installiert ist, entfernen:
pip uninstall -y ultralytics

# YOLOv12 installieren (benötigt Git!)
pip install git+https://github.com/sunsmarterjie/yolov12.git
```

**Falls Fehler "Cannot find command 'git'":**
- Git installieren (siehe Schritt 2)
- Terminal **NEU STARTEN**
- Nochmal probieren

### **Schritt 3: Andere Dependencies**

```bash
pip install Flask==3.1.2
pip install supervision==0.18.0
pip install "numpy<2.0"
pip install opencv-python
pip install huggingface_hub
pip install torch torchvision
```

**ODER alles auf einmal:**

```bash
pip install -r requirements.txt
# Dann separat YOLOv12:
pip install git+https://github.com/sunsmarterjie/yolov12.git
```

### **Schritt 4: Verifizierung**

```python
python -c "from ultralytics import YOLO; print('✅ YOLOv12 erfolgreich installiert!')"
```

---

## 6️⃣ YOLOv12 Modell

### **Option A: Eigenes trainiertes Modell**

Legen Sie Ihr `best.pt` ins Projektverzeichnis:
```
Pothole-Computer-Vision-Project/
├── best.pt  ← Hier!
├── app.py
└── ...
```

### **Option B: Basis-Modell (für Tests)**

Falls Sie kein eigenes Modell haben:

```python
from ultralytics import YOLO

# Download eines Basis-YOLOv12 Modells
model = YOLO('yolov12m.pt')  # Medium-Modell
# Modell wird automatisch heruntergeladen
```

Dann in `app.py` ändern:
```python
PR_MODEL_PATH = "yolov12m.pt"  # statt "best.pt"
```

---

## 7️⃣ Erster Start

```bash
# Virtual Environment aktivieren (falls nicht aktiv)
.\venv\Scripts\Activate.ps1  # Windows
source venv/bin/activate      # Linux/Mac

# Flask starten
python app.py
```

**Erfolg?** Ausgabe sollte sein:
```
Modell 'best.pt' gefunden. Starte Server...
 * Running on http://0.0.0.0:5000
```

**Browser öffnen:**
```
http://localhost:5000
```

---

## 8️⃣ Troubleshooting

### **Problem: ModuleNotFoundError**

```bash
# Virtual Environment aktiviert?
# Sollte (venv) im Prompt zeigen!

# Falls nicht:
.\venv\Scripts\Activate.ps1  # Windows
source venv/bin/activate      # Linux/Mac

# Dependencies nochmal installieren
pip install -r requirements.txt
```

### **Problem: NumPy Version Conflict**

```bash
pip uninstall numpy
pip install "numpy<2.0"
```

### **Problem: OpenCV funktioniert nicht**

```bash
# Alte Version entfernen
pip uninstall opencv-python opencv-python-headless

# Neu installieren
pip install opencv-python==4.8.1.78
```

### **Problem: Git nicht gefunden**

1. Git installieren (siehe Schritt 2)
2. **Terminal komplett schließen und neu öffnen**
3. `git --version` testen
4. Falls immer noch nicht: Windows neu starten

### **Problem: Kamera nicht gefunden**

```python
# In app.py testen welche Kamera-Indizes verfügbar sind:
import cv2
for i in range(5):
    cap = cv2.VideoCapture(i)
    if cap.isOpened():
        print(f"✅ Kamera {i} verfügbar")
        cap.release()
    else:
        print(f"❌ Kamera {i} nicht verfügbar")
```

---

## 9️⃣ GPU Setup (Optional - für bessere Performance)

### **NVIDIA GPU (CUDA):**

1. **CUDA Toolkit installieren:** [NVIDIA CUDA Downloads](https://developer.nvidia.com/cuda-downloads)
2. **cuDNN installieren:** [cuDNN Downloads](https://developer.nvidia.com/cudnn)
3. **PyTorch mit CUDA neu installieren:**

```bash
# CPU-Version entfernen
pip uninstall torch torchvision

# GPU-Version installieren (CUDA 11.8)
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu118
```

4. **Testen:**
```python
python -c "import torch; print(f'CUDA: {torch.cuda.is_available()}')"
```

Sollte zeigen: `CUDA: True`

---

## 🎉 Fertig!

Ihr System ist jetzt bereit! 

**Nächste Schritte:**
1. Browser öffnen: `http://localhost:5000`
2. GPS-Berechtigung erlauben
3. "YOLO Aktivieren" klicken
4. Pothole-Detection testen!

**Bei Problemen:** Siehe README.md → Troubleshooting

---

**Viel Erfolg! 🚀**

