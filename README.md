# 🕳️ Pothole Detection System - YOLOv12 Computer Vision

Ein Echtzeit-Schlagloch-Erkennungssystem mit **YOLOv12**, **GPS-Tracking** und **interaktiver Karten-Visualisierung**.

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![Flask](https://img.shields.io/badge/Flask-3.0+-green.svg)
![YOLOv12](https://img.shields.io/badge/YOLOv12-Ultralytics-orange.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

## 📋 Features

- ✅ **Echtzeit-Pothole-Detection** mit YOLOv12
- 📹 **Live-Kamera-Stream** im Browser (HD-Qualität bis 1280x720)
- 🎯 **Toggle YOLO On/Off** - Kamera läuft auch ohne Detection
- 📍 **GPS-Tracking** - Automatische Standort-Erfassung
- 💾 **CSV-Export** - Alle Detections mit Zeitstempel & GPS
- 🗺️ **Interaktive Karte** - Visualisierung aller erkannten Potholes (OpenStreetMap + Leaflet.js)
- 📊 **Live-Statistiken** - Detection Counter, Confidence, Anzahl
- 🔄 **Kamera-Wechsel** - Mehrere Kameras auswählbar (wie Zoom/Teams)
- 💻 **GPU-Support** - CUDA-kompatibel für schnellere Verarbeitung

---

## 🎬 Screenshot

```
┌─────────────────────────────────────────────┐
│  PyResearch - Pothole Detection System     │
│                                   [🗺️ Karte]│
├─────────────────────────────────────────────┤
│                                             │
│     📹 Live-Kamera mit YOLO Detection       │
│         (Rote Boxen um Potholes)            │
│                                             │
├─────────────────────────────────────────────┤
│ 🎯 Detections: 42  📍 GPS: 51.165, 10.451  │
└─────────────────────────────────────────────┘
```

---

## 🚀 Installation

### **Voraussetzungen**

- **Python 3.8+** (empfohlen: Python 3.11)
- **Webcam** (USB oder integriert)
- **Git** (für YOLOv12 Installation)
- **CUDA** (optional, für GPU-Beschleunigung)

### **Schritt 1: Repository klonen**

```bash
git clone https://github.com/IHR_USERNAME/Pothole-Computer-Vision-Project.git
cd Pothole-Computer-Vision-Project
```

### **Schritt 2: Virtual Environment erstellen**

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**Linux/Mac:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### **Schritt 3: Git installieren (falls noch nicht vorhanden)**

**Windows:** [Git für Windows herunterladen](https://git-scm.com/download/win)  
**Linux:** `sudo apt install git`  
**Mac:** `brew install git`

### **Schritt 4: Dependencies installieren**

```bash
# Upgrade pip
python -m pip install --upgrade pip

# Installiere YOLOv12 (spezieller Fork!)
pip uninstall -y ultralytics
pip install git+https://github.com/sunsmarterjie/yolov12.git

# Installiere andere Dependencies
pip install Flask==3.1.2
pip install supervision==0.18.0
pip install "numpy<2.0"
pip install opencv-python
pip install huggingface_hub
```

**ODER nutze requirements.txt:**
```bash
pip install -r requirements.txt
```

### **Schritt 5: YOLOv12 Model**

Legen Sie Ihr trainiertes **`best.pt`** Modell ins Projektverzeichnis.

Falls Sie kein Modell haben, können Sie ein vortrainiertes YOLOv12 Modell verwenden:
```bash
# Download eines Basis-Modells (falls benötigt)
# yolo12m.pt oder eigenes trainiertes Modell verwenden
```

---

## 🎮 Verwendung

### **1. Flask-Server starten**

```bash
python app.py
```

**Ausgabe:**
```
Modell 'best.pt' gefunden. Starte Server...
 * Running on http://0.0.0.0:5000
```

### **2. Browser öffnen**

```
http://localhost:5000
```

### **3. GPS-Berechtigung erlauben**

Der Browser fragt nach GPS-Zugriff → **"Zulassen"** klicken!

> **Hinweis:** Wenn GPS nicht verfügbar ist, nutzt die App automatisch Fallback-Koordinaten (Deutschland - Mitte).

### **4. YOLO aktivieren**

- Klicken Sie auf **"YOLO Aktivieren"** (grüner Button)
- Warten Sie 5-10 Sekunden (YOLO lädt)
- Zeigen Sie der Kamera ein Bild von Potholes/Schlaglöchern
- ✅ Rote Boxen erscheinen um erkannte Objekte!

### **5. Detections anschauen**

- Klicken Sie auf **🗺️ "Karte anzeigen"** (rechts oben)
- Sehen Sie alle erkannten Potholes auf einer interaktiven Karte
- Klicken Sie auf Marker für Details
- Laden Sie die CSV herunter: **"📥 CSV Download"**

---

## 📁 Projektstruktur

```
Pothole-Computer-Vision-Project/
│
├── app.py                 # Flask Backend + YOLO Logic
├── best.pt               # Ihr trainiertes YOLOv12 Modell
├── detections.csv        # Gespeicherte Detections (auto-generiert)
├── flask_app.log         # Log-Datei
├── requirements.txt      # Python Dependencies
├── README.md            # Diese Datei
│
├── templates/
│   ├── index.html       # Hauptseite (Kamera + YOLO)
│   └── map.html         # Karten-Visualisierung
│
└── venv/                # Virtual Environment (nicht in Git)
```

---

## ⚙️ Konfiguration

### **Kamera-Auflösung ändern**

In `app.py` (Zeile ~145):
```python
camera_capture.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)  # Standard: 1280
camera_capture.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)  # Standard: 720
```

**Für Laptops** (bessere Performance):
```python
camera_capture.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
camera_capture.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
```

**Für Desktops mit GPU** (höchste Qualität):
```python
camera_capture.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
camera_capture.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)
```

### **JPEG-Qualität ändern**

In `app.py` (Zeile ~243):
```python
cv2.imencode('.jpg', output_frame, [cv2.IMWRITE_JPEG_QUALITY, 95])  # 0-100
```

### **GPS Fallback-Position ändern**

In `templates/index.html` (Zeile ~518):
```javascript
currentGPS.latitude = 51.1657;   // Ihre Standard-Position
currentGPS.longitude = 10.4515;
```

---

## 🐛 Troubleshooting

### **Problem: "ModuleNotFoundError: No module named 'flask'"**

**Lösung:**
```bash
# Virtual Environment aktivieren!
venv\Scripts\activate    # Windows
source venv/bin/activate # Linux/Mac
```

### **Problem: "Cannot find command 'git'"**

**Lösung:** Git installieren (siehe Installation Schritt 3), dann Terminal **NEU STARTEN**.

### **Problem: "AAttn object has no attribute 'qkv'"**

**Lösung:** Sie haben Standard-Ultralytics statt YOLOv12 installiert:
```bash
pip uninstall ultralytics
pip install git+https://github.com/sunsmarterjie/yolov12.git
```

### **Problem: Kamera wird nicht erkannt**

**Lösung:**
1. Prüfen Sie ob andere Programme die Kamera nutzen (Zoom, Teams, etc.)
2. Im Code: Kamera-Index ändern (0, 1, 2, ...)
3. Windows: Kamera-Berechtigungen prüfen (Einstellungen → Datenschutz → Kamera)

### **Problem: GPS funktioniert nicht**

**Lösung:**
- **HTTPS erforderlich:** GPS funktioniert nur auf `localhost` oder HTTPS!
- Browser-Berechtigung: Erlauben Sie Standort-Zugriff
- Fallback wird automatisch verwendet wenn GPS nicht verfügbar

### **Problem: YOLO ist sehr langsam**

**Lösungen:**
1. **Niedrigere Auflösung** verwenden (siehe Konfiguration)
2. **FPS reduzieren:** `camera_capture.set(cv2.CAP_PROP_FPS, 15)`
3. **GPU nutzen:** CUDA Toolkit installieren
4. **Laptop:** YOLO nur kurz aktivieren wenn nötig

---

## 🗺️ CSV-Format

Die Datei `detections.csv` hat folgendes Format:

```csv
timestamp,latitude,longitude,confidence,pothole_count
2025-11-04 15:30:12,51.165700,10.451500,87.5,2
2025-11-04 15:35:45,51.166000,10.452000,92.3,1
```

**Spalten:**
- `timestamp`: Wann wurde erkannt? (YYYY-MM-DD HH:MM:SS)
- `latitude`: Breitengrad (GPS)
- `longitude`: Längengrad (GPS)
- `confidence`: Durchschnittliche Confidence (%)
- `pothole_count`: Anzahl erkannter Potholes

**Import in Excel/Google Sheets:** Einfach öffnen oder importieren!

---

## 🎯 Verwendungszwecke

- 🚗 **Straßen-Monitoring** - Automatische Pothole-Erfassung während der Fahrt
- 🗺️ **Karten-Integration** - Export für GIS-Systeme (QGIS, ArcGIS)
- 📊 **Datenanalyse** - CSV-Export für Auswertungen
- 🏗️ **Infrastruktur-Management** - Priorisierung von Reparaturen
- 📱 **Mobile Erfassung** - Mit Laptop/Tablet im Fahrzeug

---

## 🔧 Technologie-Stack

- **Backend:** Flask 3.1.2, Python 3.11
- **Computer Vision:** YOLOv12 (Ultralytics Fork), OpenCV
- **Detection:** Supervision 0.18.0
- **Deep Learning:** PyTorch 2.9.0, TorchVision 0.24.0
- **Frontend:** HTML5, CSS3, Vanilla JavaScript
- **Karten:** Leaflet.js, OpenStreetMap
- **Daten:** CSV (NumPy, Pandas-kompatibel)

---

## 📊 Performance

### **Laptop (CPU):**
- ~5-15 FPS mit YOLO
- ~30 FPS ohne YOLO (reine Kamera)

### **Desktop (GPU - z.B. RTX 3060):**
- ~30-60 FPS mit YOLO
- ~30 FPS ohne YOLO

### **Optimierungen:**
- Niedrigere Auflösung → Höhere FPS
- GPU → 10-50x schneller als CPU
- YOLO nur aktivieren wenn nötig

---

## 🤝 Mitwirken

Beiträge sind willkommen! Erstellen Sie einen Pull Request oder öffnen Sie ein Issue.

---

## 📄 Lizenz

Dieses Projekt steht unter der MIT-Lizenz.

---

## 👨‍💻 Autor

PyResearch - Pothole Detection System

---

## 🙏 Danksagungen

- [YOLOv12](https://github.com/sunsmarterjie/yolov12) - Improved YOLO Architecture
- [Ultralytics](https://github.com/ultralytics/ultralytics) - Original YOLO Framework
- [Leaflet.js](https://leafletjs.com/) - Interactive Maps
- [OpenStreetMap](https://www.openstreetmap.org/) - Open Source Kartenmaterial

---

## 📞 Support

Bei Fragen oder Problemen:
1. Lesen Sie das **Troubleshooting** oben
2. Öffnen Sie ein **Issue** auf GitHub
3. Prüfen Sie die **Browser Console** (F12) für Fehler

---

**⭐ Wenn Ihnen dieses Projekt gefällt, geben Sie einen Stern auf GitHub!**
