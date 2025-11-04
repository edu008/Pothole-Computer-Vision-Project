# ⚡ Quick Start - In 5 Minuten starten!

Für erfahrene Nutzer - minimale Setup-Schritte.

---

## 🚀 Schnelle Installation

```bash
# 1. Repository klonen
git clone https://github.com/IHR_USERNAME/Pothole-Computer-Vision-Project.git
cd Pothole-Computer-Vision-Project

# 2. Virtual Environment
python -m venv venv

# Windows:
.\venv\Scripts\Activate.ps1

# Linux/Mac:
source venv/bin/activate

# 3. YOLOv12 installieren (benötigt Git!)
pip install --upgrade pip
pip install git+https://github.com/sunsmarterjie/yolov12.git

# 4. Dependencies
pip install Flask supervision "numpy<2.0" opencv-python huggingface_hub

# 5. Model ins Projektverzeichnis legen
# → best.pt hier ablegen!

# 6. Starten
python app.py
```

**Browser:** `http://localhost:5000`

---

## 🎮 Verwendung

1. **GPS erlauben** (Browser fragt)
2. **"YOLO Aktivieren"** klicken
3. **Kamera** auf Potholes richten
4. **Karte anzeigen** → `🗺️` Button klicken
5. **CSV Download** → Alle Daten exportieren

---

## 🐛 Häufige Probleme

| Problem | Lösung |
|---------|--------|
| `ModuleNotFoundError` | Virtual Environment aktivieren! |
| `Cannot find command 'git'` | Git installieren, Terminal neu starten |
| `AAttn attribute error` | YOLOv12 installieren (nicht Standard-Ultralytics!) |
| Kamera nicht gefunden | Andere Programme schließen, Index ändern |
| GPS funktioniert nicht | Nur auf `localhost` oder HTTPS! Browser-Berechtigung erlauben |

Mehr Details: Siehe **[INSTALL.md](INSTALL.md)** und **[README.md](README.md)**

---

**Viel Erfolg! 🎉**

