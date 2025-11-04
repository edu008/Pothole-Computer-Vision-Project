from flask import Flask, render_template, Response, jsonify, send_file, request
import cv2
import supervision as sv
from ultralytics import YOLO
import time
import os
import threading
import sys
import logging
import csv
from datetime import datetime

# Flask App Initialization
app = Flask(__name__)

# Konfiguriere Logging für bessere Sichtbarkeit
log_file = 'flask_app.log'
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(log_file, mode='a', encoding='utf-8')
    ]
)
logger = logging.getLogger(__name__)

# Deaktiviere Werkzeug/Flask's eigene Logs für klarere Ausgabe
logging.getLogger('werkzeug').setLevel(logging.WARNING)

# Helper function für sofortige Console-Ausgabe
def log(message):
    """Logging mit sofortiger Ausgabe in Terminal UND Datei"""
    logger.info(message)
    print(f"[LOG] {message}", flush=True)
    sys.stdout.flush()

# PyResearch Configuration Constants
PR_MODEL_PATH = "best.pt"
CSV_FILE_PATH = "detections.csv"  # CSV-Datei für Pothole-Detections
PR_DISPLAY_CONFIG = {
    'window_title': "PyResearch - Pothole Computer Vision Project",
    'window_size': (1280, 720),
    'color_scheme': "PR_DARK_BLUE",
    'fps_display': True
}

# Global variables
detection_count = 0
camera_index = 0  # Standard-Kamera-Index (0 = erste verfügbare Kamera)
visualizer_instance = None
camera_capture = None
camera_lock = threading.Lock()  # Lock für Thread-Safe Kamera-Zugriff
yolo_error_logged = False  # Flag um YOLO-Fehler nur einmal zu loggen
yolo_enabled = False  # YOLO ist standardmäßig deaktiviert

def check_model_exists():
    """Prüft ob das Modell existiert"""
    if not os.path.exists(PR_MODEL_PATH):
        raise FileNotFoundError(f"Modell-Datei '{PR_MODEL_PATH}' nicht gefunden!")
    return True

class PyResearchVisualizer:
    """PyResearch Standard Visualization Engine"""
    
    def __init__(self):
        try:
            check_model_exists()
            # PyTorch 2.6 Fix: Deaktiviere weights_only für vertrauenswürdige Modelle
            import torch
            
            # Setze die globale torch.load Einstellung auf weights_only=False
            # Dies ist sicher, da wir unserem eigenen trainierten Modell vertrauen
            original_load = torch.load
            def patched_load(*args, **kwargs):
                kwargs['weights_only'] = False
                return original_load(*args, **kwargs)
            torch.load = patched_load
            
            log("Lade YOLO Modell mit PyTorch 2.6 Fix (weights_only=False)...")
            self.model = YOLO(PR_MODEL_PATH)
            log("✓✓✓ YOLO Modell erfolgreich geladen!")
            
            # Stelle torch.load wieder her
            torch.load = original_load
        except FileNotFoundError as e:
            raise e
        except Exception as e:
            raise Exception(f"Fehler beim Laden des Modells: {str(e)}")
        
        self.box_annotator = sv.BoundingBoxAnnotator(
            thickness=2,
            color=sv.Color.from_hex("#0055FF")
        )
        self.label_annotator = sv.LabelAnnotator(
            text_scale=0.7,
            text_thickness=1,
            text_color=sv.Color.WHITE,
            text_padding=10
        )
        
    def process_frame(self, frame):
        """PyResearch Standard Processing Pipeline"""
        global detection_count
        results = self.model(frame)[0]
        detections = sv.Detections.from_ultralytics(results)
        
        # Update detection count
        detection_count = len(detections)  # Count the number of detections in the current frame
        
        # Apply PyResearch Visualization Standards
        annotated_frame = self.box_annotator.annotate(
            scene=frame,
            detections=detections
        )
        annotated_frame = self.label_annotator.annotate(
            scene=annotated_frame,
            detections=detections
        )
        
        return annotated_frame

def generate_frames():
    """Generiert Live-Kamera-Frames für den Stream"""
    global camera_index, visualizer_instance, camera_capture, camera_lock, yolo_enabled, yolo_error_logged
    
    log(f"generate_frames() gestartet - camera_index={camera_index}, YOLO={yolo_enabled}")
    
    # Thread-Safe Kamera-Öffnung
    log("Versuche Camera-Lock zu erwerben...")
    with camera_lock:
        log("Camera-Lock erworben!")
        # Öffne Kamera (falls noch nicht geöffnet)
        # Windows-spezifisch: Verwende DirectShow (CAP_DSHOW) für bessere Kompatibilität
        if camera_capture is None or not camera_capture.isOpened():
            log(f">>> Öffne Kamera {camera_index} für Video-Stream...")
            # Versuche mit DirectShow Backend (besser für Windows)
            camera_capture = cv2.VideoCapture(camera_index, cv2.CAP_DSHOW)
            log(f"VideoCapture erstellt, isOpened={camera_capture.isOpened()}")
            
            # Falls DirectShow nicht funktioniert, versuche Standard
            if not camera_capture.isOpened():
                log("DirectShow fehlgeschlagen, versuche Standard-Backend...")
                camera_capture = cv2.VideoCapture(camera_index)
                log(f"Standard-Backend versucht, isOpened={camera_capture.isOpened()}")
            
            # Setze Kamera-Auflösung für gute Qualität
            camera_capture.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)  # Hohe Qualität
            camera_capture.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)   # 720p HD
            camera_capture.set(cv2.CAP_PROP_FPS, 30)              # 30 FPS
            camera_capture.set(cv2.CAP_PROP_BUFFERSIZE, 1)
            
            # Verbessere Bildqualität
            camera_capture.set(cv2.CAP_PROP_AUTO_EXPOSURE, 1)    # Auto-Exposure an
            camera_capture.set(cv2.CAP_PROP_AUTOFOCUS, 1)         # Autofocus an
            camera_capture.set(cv2.CAP_PROP_BRIGHTNESS, 128)      # Helligkeit (0-255)
            camera_capture.set(cv2.CAP_PROP_CONTRAST, 128)        # Kontrast
            camera_capture.set(cv2.CAP_PROP_SATURATION, 128)      # Sättigung
            camera_capture.set(cv2.CAP_PROP_SHARPNESS, 128)       # Schärfe
            
            log("Kamera-Eigenschaften gesetzt (HD-Qualität)")
        else:
            log(f"Kamera {camera_index} ist bereits geöffnet")
        
        # Prüfe ob Kamera geöffnet werden konnte
        if not camera_capture.isOpened():
            log(f"✗✗✗ FEHLER: Kamera {camera_index} konnte nicht geöffnet werden!")
            error_frame = cv2.zeros((480, 640, 3), dtype=cv2.uint8)
            cv2.putText(error_frame, "Kamera konnte nicht geoffnet werden!", 
                       (50, 220), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
            cv2.putText(error_frame, f"Versuche Kamera-Index: {camera_index}", 
                       (50, 260), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
            _, buffer = cv2.imencode('.jpg', error_frame)
            frame_bytes = buffer.tobytes()
            while True:
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
                time.sleep(1)
            return
        
        log(f"✓✓✓ Kamera {camera_index} erfolgreich geöffnet! Starte Video-Stream...")
    
    log("Camera-Lock freigegeben, starte Frame-Loop...")
    
    # Lese kontinuierlich Frames von der Kamera
    while True:
        success, frame = camera_capture.read()
        
        if not success:
            # Fehler beim Lesen - versuche Kamera neu zu öffnen
            log("⚠ Fehler beim Lesen der Kamera. Versuche erneut...")
            camera_capture.release()
            time.sleep(0.5)
            camera_capture = cv2.VideoCapture(camera_index)
            if not camera_capture.isOpened():
                error_frame = cv2.zeros((480, 640, 3), dtype=cv2.uint8)
                cv2.putText(error_frame, "Kamera-Verbindung verloren!", 
                           (50, 240), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
                _, buffer = cv2.imencode('.jpg', error_frame)
                frame_bytes = buffer.tobytes()
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
            continue
        
        try:
            # Spiegele Frame horizontal für bessere UX (wie bei Webcam-Ansicht)
            frame = cv2.flip(frame, 1)
            
            # Verarbeite Frame mit YOLO nur wenn aktiviert
            if yolo_enabled:
                # YOLO ist aktiviert - versuche Detection
                if visualizer_instance is None:
                    # YOLO wurde aktiviert, aber noch nicht initialisiert
                    log("YOLO wurde aktiviert - Initialisiere Visualizer...")
                    try:
                        visualizer_instance = PyResearchVisualizer()
                        log("✓ YOLO Visualizer erfolgreich initialisiert!")
                    except Exception as e:
                        log(f"✗ FEHLER beim Laden des YOLO Modells: {str(e)}")
                        yolo_enabled = False  # Deaktiviere YOLO wieder
                        visualizer_instance = None
                
                if visualizer_instance is not None:
                    try:
                        output_frame = visualizer_instance.process_frame(frame)
                    except Exception as yolo_error:
                        # YOLO Fehler - zeige unverarbeitetes Bild als Fallback
                        if not yolo_error_logged:
                            log(f"⚠⚠⚠ YOLO Modell-Fehler: {str(yolo_error)}")
                            log("→ Fallback: Zeige Kamera-Rohbild ohne Pothole-Detection")
                            yolo_error_logged = True
                        output_frame = frame
                        # Füge Warnung zum Bild hinzu
                        cv2.putText(output_frame, "WARNUNG: YOLO Fehler - Rohbild", 
                                   (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
                else:
                    output_frame = frame
            else:
                # YOLO ist deaktiviert - zeige nur Rohbild
                output_frame = frame
                # Zeige Status
                cv2.putText(output_frame, "Live Camera (YOLO deaktiviert)", 
                           (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            
            # Encode Frame als JPEG mit hoher Qualität
            _, buffer = cv2.imencode('.jpg', output_frame, [cv2.IMWRITE_JPEG_QUALITY, 95])  # Erhöht von 85 auf 95
            frame_bytes = buffer.tobytes()
            
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
        except Exception as e:
            log(f"⚠ Kritischer Fehler bei Frame-Verarbeitung: {str(e)}")
            continue

@app.route('/')
def index():
    log("========== INDEX SEITE WURDE GELADEN ==========")
    return render_template('index.html')

@app.route('/test')
def test():
    log("========== TEST ENDPOINT WURDE AUFGERUFEN ==========")
    return jsonify({
        'status': 'OK',
        'message': 'Flask funktioniert!',
        'camera_index': camera_index
    })

@app.route('/video_feed')
def video_feed():
    log("========== VIDEO_FEED WURDE AUFGERUFEN ==========")
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/detection_count')
def get_detection_count():
    return jsonify({'detections': detection_count})

@app.route('/camera_info')
def get_camera_info():
    """Gibt Informationen über die verfügbare Kamera zurück"""
    global camera_index, camera_capture
    
    # Versuche die bereits geöffnete Kamera zu verwenden
    if camera_capture is not None and camera_capture.isOpened():
        width = int(camera_capture.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(camera_capture.get(cv2.CAP_PROP_FRAME_HEIGHT))
        fps = camera_capture.get(cv2.CAP_PROP_FPS)
        return jsonify({
            'available': True,
            'index': camera_index,
            'width': width,
            'height': height,
            'fps': fps
        })
    else:
        # Kamera ist noch nicht geöffnet oder nicht verfügbar
        return jsonify({
            'available': False,
            'index': camera_index,
            'message': 'Kamera wird gestartet oder ist nicht verfügbar'
        })

@app.route('/available_cameras')
def available_cameras():
    """Findet alle verfügbaren Kameras"""
    cameras = []
    # Teste die ersten 5 Kamera-Indizes
    for i in range(5):
        cap = cv2.VideoCapture(i, cv2.CAP_DSHOW)
        if cap.isOpened():
            # Versuche einen Frame zu lesen um sicherzustellen, dass die Kamera funktioniert
            success, _ = cap.read()
            if success:
                cameras.append({
                    'index': i,
                    'name': f'Kamera {i}'
                })
            cap.release()
    return jsonify({'cameras': cameras})

@app.route('/toggle_yolo')
def toggle_yolo():
    """Aktiviert/Deaktiviert YOLO Detection"""
    global yolo_enabled
    
    yolo_enabled = not yolo_enabled
    status = "aktiviert" if yolo_enabled else "deaktiviert"
    log(f"========== YOLO {status.upper()} ==========")
    
    return jsonify({
        'success': True,
        'yolo_enabled': yolo_enabled,
        'message': f'YOLO wurde {status}'
    })

@app.route('/yolo_status')
def yolo_status():
    """Gibt den aktuellen YOLO-Status zurück"""
    global yolo_enabled
    return jsonify({
        'yolo_enabled': yolo_enabled
    })

@app.route('/switch_camera/<int:index>')
def switch_camera(index):
    """Wechselt zu einer anderen Kamera"""
    global camera_index, camera_capture, camera_lock
    
    log(f"========== WECHSLE ZU KAMERA {index} ==========")
    
    # Thread-Safe Kamera-Wechsel
    with camera_lock:
        # Schließe die aktuelle Kamera
        if camera_capture is not None:
            log(f"Schließe alte Kamera {camera_index}...")
            camera_capture.release()
            camera_capture = None
            time.sleep(0.5)  # Kurze Pause damit Windows die Kamera freigeben kann
        
        # Setze neuen Index
        old_index = camera_index
        camera_index = index
        log(f"Kamera-Index geändert von {old_index} zu {camera_index}")
    
    # Teste die neue Kamera (außerhalb des Locks)
    log(f"Teste Kamera {camera_index}...")
    test_cap = cv2.VideoCapture(camera_index, cv2.CAP_DSHOW)
    if test_cap.isOpened():
        # Teste ob wir einen Frame lesen können
        success, _ = test_cap.read()
        test_cap.release()
        time.sleep(0.2)  # Kleine Pause
        
        if success:
            log(f"✓ Kamera {index} erfolgreich getestet!")
            return jsonify({
                'success': True,
                'message': f'Kamera {index} ausgewählt',
                'index': index
            })
        else:
            log(f"✗ Kamera {index} konnte keinen Frame lesen!")
            return jsonify({
                'success': False,
                'message': f'Kamera {index} kann keine Frames lesen',
                'index': camera_index
            })
    else:
        log(f"✗ Kamera {index} konnte nicht geöffnet werden!")
        return jsonify({
            'success': False,
            'message': f'Kamera {index} konnte nicht geöffnet werden',
            'index': camera_index
        })

@app.route('/map')
def map_page():
    """Zeigt die Karten-Seite mit allen Pothole-Detections"""
    log("Karten-Seite aufgerufen")
    return render_template('map.html')

@app.route('/get_detections')
def get_detections():
    """Liest alle Detections aus der CSV und gibt sie als JSON zurück"""
    log("Detections werden geladen...")
    
    detections = []
    
    # Prüfe ob CSV existiert
    if not os.path.exists(CSV_FILE_PATH):
        log("Keine CSV-Datei gefunden - erstelle neue")
        # Erstelle CSV mit Header
        with open(CSV_FILE_PATH, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['timestamp', 'latitude', 'longitude', 'confidence', 'pothole_count'])
        return jsonify({'detections': []})
    
    # Lese CSV
    try:
        with open(CSV_FILE_PATH, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                detections.append({
                    'timestamp': row['timestamp'],
                    'latitude': float(row['latitude']),
                    'longitude': float(row['longitude']),
                    'confidence': float(row['confidence']),
                    'pothole_count': int(row['pothole_count'])
                })
        
        log(f"✓ {len(detections)} Detections geladen")
        return jsonify({'detections': detections})
    
    except Exception as e:
        log(f"✗ Fehler beim Lesen der CSV: {str(e)}")
        return jsonify({'detections': [], 'error': str(e)})

@app.route('/save_detection', methods=['POST'])
def save_detection():
    """Speichert eine neue Detection in die CSV"""
    try:
        data = request.json
        
        latitude = data.get('latitude')
        longitude = data.get('longitude')
        confidence = data.get('confidence', 0)
        pothole_count = data.get('pothole_count', 1)
        
        # Validierung
        if latitude is None or longitude is None:
            log("⚠ Fehler: GPS-Koordinaten fehlen")
            return jsonify({'success': False, 'error': 'GPS-Koordinaten fehlen'}), 400
        
        # Erstelle CSV wenn nicht vorhanden
        file_exists = os.path.exists(CSV_FILE_PATH)
        
        # Speichere in CSV
        with open(CSV_FILE_PATH, 'a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            
            # Header schreiben wenn Datei neu
            if not file_exists:
                writer.writerow(['timestamp', 'latitude', 'longitude', 'confidence', 'pothole_count'])
            
            # Timestamp
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            # Daten schreiben
            writer.writerow([timestamp, latitude, longitude, confidence, pothole_count])
        
        log(f"✓ Detection gespeichert: GPS({latitude}, {longitude}), Confidence: {confidence}%, Count: {pothole_count}")
        
        return jsonify({
            'success': True,
            'message': 'Detection gespeichert',
            'timestamp': timestamp
        })
    
    except Exception as e:
        log(f"✗ Fehler beim Speichern: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/download_csv')
def download_csv():
    """Download der CSV-Datei"""
    log("CSV-Download angefordert")
    
    if not os.path.exists(CSV_FILE_PATH):
        log("Keine CSV-Datei vorhanden")
        return jsonify({'error': 'Keine Daten vorhanden'}), 404
    
    return send_file(CSV_FILE_PATH, 
                     mimetype='text/csv',
                     as_attachment=True,
                     download_name='pothole_detections.csv')

if __name__ == "__main__":
    try:
        check_model_exists()
        print(f"Modell '{PR_MODEL_PATH}' gefunden. Starte Server...")
    except FileNotFoundError as e:
        print(f"WARNUNG: {str(e)}")
        print("Die Anwendung kann ohne Modell-Datei nicht funktionieren.")
    
    app.run(debug=True, host='0.0.0.0', port=5000)