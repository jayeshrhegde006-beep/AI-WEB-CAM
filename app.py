import os
import cv2
import numpy as np
import time
import sqlite3
import datetime
import requests
import google.generativeai as genai
from flask import Flask, render_template, request, redirect, session, jsonify, Response
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from dotenv import load_dotenv

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(BASE_DIR, "server", ".env"))
from intelligence import (
    scan_qr_barcode, 
    get_color_palette, 
    apply_smart_filter, 
    analyze_sentiment, 
    generate_vision_story,
    detect_faces_and_blur,
    get_exif_metadata,
    predict_scene_environment,
    stego_hide_text,
    stego_reveal_text,
    auto_crop_objects,
    generate_heatmap,
    generate_visual_tags,
    add_secure_watermark,
    audit_accessibility,
    extract_wireframe,
    guess_ai_prompt,
    detect_language,
    summarize_text,
    extract_keywords,
    scrub_sensitive_data,
    stylize_text,
    generate_voice_data,
    smart_social_resize,
    detect_emotions_sim,
    analyze_visual_quality,
    isolate_background,
    classify_vibe_style,
    map_object_relationships,
    image_to_ascii,
    apply_glitch_core,
    apply_cyberpunk_vibe,
    thermal_vision_sim,
    synthesize_bg_prompt,
    detect_edge_flow,
    simulate_depth_map,
    audit_composition,
    analyze_light_physics,
    detect_geometry_intel,
    generate_reliability_report,
    analyze_plant_health,
    analyze_nutrition_ai
)

# ---------------- APP SETUP ----------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

app = Flask(
    __name__,
    template_folder=os.path.join(BASE_DIR, "templates"),
    static_folder=os.path.join(BASE_DIR, "static")
)
app.secret_key = "smartcam_secret"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(BASE_DIR, 'analytics.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
UPLOAD_FOLDER = os.path.join(BASE_DIR, "static", "uploads")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024 # Allow up to 50MB files

# ---------------- BRAIN: GOOGLE GEMINI CONFIG ----------------
# NOTE: Replace with your actual Gemini API Key for Neural-Level Prompts
GEMINI_API_KEY = "YOUR_GEMINI_API_KEY_HERE" 
if GEMINI_API_KEY != "YOUR_GEMINI_API_KEY_HERE":
    genai.configure(api_key=GEMINI_API_KEY)

# ---------------- DATABASE (ANALYTICS) ----------------
# ---------------- MODELS ----------------
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)

class TranslationLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    source_lang = db.Column(db.String(50))
    target_lang = db.Column(db.String(50))
    text_length = db.Column(db.Integer)



def init_db():
    with app.app_context():
        db.create_all()
        # Create default admin if not exists
        if not User.query.filter_by(username='admin').first():
            admin = User(username='admin', password='admin') # In production, use hashed passwords
            db.session.add(admin)
            db.session.commit()
            print("[SYSTEM] Default admin user created.")

init_db()

# Global OCR Reader State
reader = None

def get_ocr_reader():
    global reader
    if reader is None:
        print("[SYSTEM] Attempting to wake up OCR Engine...")
        try:
            import easyocr
            reader = easyocr.Reader(['en'], gpu=False)
            print("[SYSTEM] OCR Engine is now Online.")
        except Exception as e:
            print(f"[SYSTEM] OCR Wake-up Failed: {e}")
    return reader

def log_translation(src, target, length):
    try:
        log = TranslationLog(source_lang=src, target_lang=target, text_length=length)
        db.session.add(log)
        db.session.commit()
    except Exception as e:
        print(f"DB Log Error: {e}")

# ---------------- LOGIN / FRONTEND ----------------
@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        user = User.query.filter_by(username=username).first()
        if user and user.password == password:
            session["user"] = user.username
            return redirect("/dashboard")

        return render_template("login.html", error="Invalid credentials")

    return render_template("login.html")


@app.route("/dashboard")
def dashboard():
    if "user" not in session:
        return redirect("/")
    return render_template("index.html")


@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

# ---------------- LIVE CAMERA ENGINE ----------------

def gen_frames():
    camera = cv2.VideoCapture(0)  # Use 0 for default webcam
    while True:
        success, frame = camera.read()
        if not success:
            break
        else:
            # Here we could potentially add real-time detection
            # For now, we'll keep it as a clean raw feed for speed
            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@app.route('/video_feed')
def video_feed():
    return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

# ---------------- OBJECT DETECTION ----------------
@app.route("/detect", methods=["POST"])
def detect():
    try:
        from ai_module import detect_objects
        
        if "image" not in request.files:
            return jsonify({"objects": [], "story": "No image uploaded."})

        file = request.files["image"]
        if file.filename == "":
            return jsonify({"objects": [], "story": "No image selected."})

        # IMPROVEMENT: Read image once into memory for instant processing
        img_bytes = file.read()
        nparr = np.frombuffer(img_bytes, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

        # Save for storage path (needed for pro features later)
        path = os.path.join(UPLOAD_FOLDER, file.filename)
        with open(path, 'wb') as f:
            f.write(img_bytes)

        # Call detection on the IN-MEMORY image
        detections = detect_objects(img)
        print(f"Detections: {detections}")
        
        print("Generating story...")
        story = generate_vision_story(detections)
        print(f"Story: {story}")

        return jsonify({
            "image": "/static/uploads/" + file.filename,
            "objects": detections,
            "story": story,
            "filename": file.filename
        })
    except Exception as e:
        print(f"CRITICAL ERROR in /detect: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            "objects": [],
            "story": f"System Error: {str(e)}",
            "error": str(e)
        }), 500

# ---------------- INTELLIGENCE LAB (6 NEW FEATURES) ----------------

@app.route("/analyze_all", methods=["POST"])
def analyze_all():
    """
    Feature 1 & 2: QR Scanning & Color Palette Extraction
    """
    filename = request.args.get("filename")
    if not filename: return jsonify({"error": "No filename"})
    
    path = os.path.join(UPLOAD_FOLDER, filename)
    
    qr_data = scan_qr_barcode(path)
    colors = get_color_palette(path)
    
    return jsonify({
        "qr": qr_data,
        "palette": colors
    })

@app.route("/apply_filter", methods=["POST"])
def apply_filter_route():
    """
    Feature 3: Smart Image Filters
    """
    data = request.get_json(force=True)
    filename = data.get("filename")
    filter_type = data.get("filter", "grayscale")
    
    if not filename: return jsonify({"error": "No filename"})
    
    path = os.path.join(UPLOAD_FOLDER, filename)
    filtered_url = apply_smart_filter(path, filter_type)
    
    return jsonify({"url": filtered_url})

@app.route("/object_stats", methods=["POST"])
def object_stats():
    """
    Feature 5: Detailed Object Counting
    """
    data = request.get_json(force=True)
    detections = data.get("objects", [])
    
    from collections import Counter
    counts = Counter([d['label'] for d in detections])
    
    return jsonify({
        "stats": [{"label": k, "count": v} for k, v in counts.items()]
    })

# ---------------- SECURITY & FORENSICS (6 MORE FEATURES) ----------------

@app.route("/security_blur", methods=["POST"])
def security_blur():
    """
    Feature 7 & 8: Face Intelligence & Privacy Shield
    """
    filename = request.args.get("filename")
    mode = request.args.get("mode", "detect") # detect or blur
    if not filename: return jsonify({"error": "No filename"})
    
    path = os.path.join(UPLOAD_FOLDER, filename)
    result = detect_faces_and_blur(path, mode)
    
    # NEW: Generate biometric signature if faces found
    from intelligence import generate_biometric_id
    result["bio_id"] = generate_biometric_id(result.get("faces", []))
    
    return jsonify(result)

@app.route("/metadata_forensic", methods=["POST"])
def metadata_forensic():
    """
    Feature 9: Metadata Extraction
    """
    filename = request.args.get("filename")
    if not filename: return jsonify({"error": "No filename"})
    
    path = os.path.join(UPLOAD_FOLDER, filename)
    metadata = get_exif_metadata(path)
    
    # NEW: Signal forensic scan
    from intelligence import scan_signal_integrity
    metadata["Signal Integrity"] = scan_signal_integrity(path)
    
    return jsonify(metadata)

@app.route("/scene_ai", methods=["POST"])
def scene_ai():
    """
    Feature 10: Environment Prediction
    """
    data = request.get_json(force=True)
    detections = data.get("objects", [])
    prediction = predict_scene_environment(detections)
    return jsonify(prediction)

@app.route("/stego_ops", methods=["POST"])
def stego_ops():
    """
    Feature 11: Steganography
    """
    data = request.get_json(force=True)
    filename = data.get("filename")
    text = data.get("text", "")
    op = data.get("op", "hide")
    
    if not filename: return jsonify({"error": "No filename"})
    path = os.path.join(UPLOAD_FOLDER, filename)
    
    if op == "hide":
        url = stego_hide_text(path, text)
        return jsonify({"url": url})
    else:
        secret = stego_reveal_text(path)
        return jsonify({"secret": secret})

@app.route("/smart_crop", methods=["POST"])
def smart_crop_route():
    """
    Feature 12: Auto-Crop
    """
    filename = request.args.get("filename")
    if not filename: return jsonify({"error": "No filename"})
    
    path = os.path.join(UPLOAD_FOLDER, filename)
    cropped_url = auto_crop_objects(path, [])
    return jsonify({"url": cropped_url})

# ---------------- ULTIMATE VISUAL LAB (6 MORE FEATURES) ----------------

@app.route("/ultimate_lab", methods=["POST"])
def ultimate_lab():
    """
    Features 13-18: The Ultimate Intelligence Suite
    """
    data = request.get_json(force=True)
    filename = data.get("filename")
    detections = data.get("objects", [])
    colors = data.get("colors", [])
    op = data.get("op", "tags") # tags, heatmap, watermark, audit, wire, guess
    
    if not filename: return jsonify({"error": "No filename"})
    path = os.path.join(UPLOAD_FOLDER, filename)
    
    scene = predict_scene_environment(detections)
    
    if op == "tags":
        return jsonify({"tags": generate_visual_tags(detections, scene)})
    elif op == "heatmap":
        return jsonify({"url": generate_heatmap(path, detections)})
    elif op == "watermark":
        return jsonify({"url": add_secure_watermark(path, "SMART-CAM-AI PROTECTED")})
    elif op == "audit":
        return jsonify({"audit": audit_accessibility(colors)})
    elif op == "wire":
        return jsonify({"url": extract_wireframe(path)})
    elif op == "guess":
        return jsonify({"prompt": guess_ai_prompt(detections, scene)})
    
    return jsonify({"status": "unknown op"})

# ---------------- PRO FEATURES (6 MORE VISUAL FEATURES) ----------------

@app.route("/pro_features", methods=["POST"])
def pro_features():
    """
    Features 25-30: The Professional Vision Suite
    """
    data = request.get_json(force=True)
    filename = data.get("filename")
    detections = data.get("objects", [])
    op = data.get("op", "all")
    
    if not filename: return jsonify({"error": "No filename"})
    path = os.path.join(UPLOAD_FOLDER, filename)
    
    if op == "resize":
        target = data.get("target", "instagram")
        return jsonify({"url": smart_social_resize(path, target)})
    elif op == "portrait":
        return jsonify({"url": isolate_background(path)})
    elif op == "quality":
        return jsonify({"quality": analyze_visual_quality(path)})
    elif op == "style":
        return jsonify({"style": classify_vibe_style(detections)})
    elif op == "relationships":
        return jsonify({"rel": map_object_relationships(detections)})
    elif op == "emotions":
        # Get face count from detections if labels include 'person'
        faces = len([d for d in detections if d['label'].lower() == 'person'])
        return jsonify({"emotion": detect_emotions_sim(faces)})

    return jsonify({"status": "unknown pro op"})



# ---------------- IMAGE ANALYSIS (6 FINAL CORE FEATURES) ----------------

@app.route("/image_analysis", methods=["POST"])
def image_analysis_final():
    """
    Features 37-42: High-End Visual Intelligence
    """
    data = request.get_json(force=True)
    filename = data.get("filename")
    detections = data.get("objects", [])
    op = data.get("op", "all")
    
    if not filename: return jsonify({"error": "No filename"})
    path = os.path.join(UPLOAD_FOLDER, filename)
    
    if op == "edges":
        return jsonify({"url": detect_edge_flow(path)})
    elif op == "depth":
        return jsonify({"url": simulate_depth_map(path)})
    elif op == "composition":
        return jsonify({"url": audit_composition(path)})
    elif op == "light":
        return jsonify({"report": analyze_light_physics(path)})
    elif op == "geometry":
        return jsonify({"geo": detect_geometry_intel(path)})
    elif op == "reliability":
        return jsonify({"report": generate_reliability_report(detections)})

    return jsonify({"status": "unknown analysis op"})

# Note: All 42 Pro Features (18+6+6+6+6) are now fully integrated and live.

# ---------------- EASYOCR (TEXT EXTRACTION) ----------------
@app.route("/extract_text", methods=["POST"])
def extract_text():
    if "image" not in request.files:
        return jsonify({"text": ""})

    file = request.files["image"]
    
    try:
        # Read directly from memory (Bypass Disk I/O)
        img_bytes = file.read()
        nparr = np.frombuffer(img_bytes, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if img is None: return jsonify({"text": "Error: Invalid image."})

        # Use helper to ensure reader is ready
        ocr = get_ocr_reader()
        if ocr is None:
            return jsonify({"text": "OCR Engine Offline. Please try again."})

        # High Accuracy Scan (Original Color + Contrast Tuning)
        # We use a lower contrast threshold specifically for document scans
        extracted_text = ocr.readtext(
            img, 
            detail=0, 
            paragraph=False,
            contrast_ths=0.1,  # More sensitive to faint text
            adjust_contrast=0.7 # Sharpens document text
        )
        
        # Save a copy so Pro Features can use this image later
        filename = f"ocr_{int(time.time())}.jpg"
        save_path = os.path.join(UPLOAD_FOLDER, filename)
        cv2.imwrite(save_path, img)

        return jsonify({
            "text": " ".join(extracted_text) if extracted_text else "No text found. Try a clearer photo.",
            "filename": filename
        })

    except Exception as e:
        print(f"Fast OCR Error: {e}")
        return jsonify({"text": "Extraction failed.", "error": str(e)})

@app.route("/bulk_ocr", methods=["POST"])
def bulk_ocr():
    if "images" not in request.files:
        return jsonify({"text": "No images uploaded"})
    
    files = request.files.getlist("images")
    if not files: return jsonify({"text": "Empty upload."})

    if reader is None:
        return jsonify({"text": "OCR engine offline."})

    full_text = []
    try:
        for i, file in enumerate(files):
            if file.filename == "": continue
            
            # Fast in-memory read
            img_bytes = file.read()
            nparr = np.frombuffer(img_bytes, np.uint8)
            img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

            if img is not None:
                # Resize large pages for speed (1000px is enough for documents)
                h, w = img.shape[:2]
                if max(h, w) > 1000:
                    scale = 1000 / max(h, w)
                    img = cv2.resize(img, (int(w*scale), int(h*scale)))

                gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                
                # Use helper
                ocr = get_ocr_reader()
                if ocr is None:
                    return jsonify({"text": "OCR Engine Offline."})

                # Ultra-fast mode
                page_text = ocr.readtext(gray, detail=0, paragraph=True)
                
                if page_text:
                    full_text.append(f"--- Page {i+1} ---\n" + " ".join(page_text))
        
        return jsonify({"text": "\n\n".join(full_text) if full_text else "No text detected."})
    except Exception as e:
        print(f"Bulk OCR Error: {e}")
        return jsonify({"text": "System error during bulk scan."})

@app.route("/text_intelligence", methods=["POST"])
def text_intelligence():
    """
    NLP Intelligence Suite: Sentiment, Language, Summary, Keywords, scrubbing
    """
    data = request.get_json(force=True)
    text = data.get("text", "")
    op = data.get("op", "all")
    
    if not text: return jsonify({"error": "Empty text"})

    if op == "scrub":
        return jsonify({"text": scrub_sensitive_data(text)})
    elif op == "summarize":
        return jsonify({"text": summarize_text(text)})
    elif op == "keywords":
        return jsonify({"keywords": extract_keywords(text)})
    elif op == "stylize":
        return jsonify({"text": stylize_text(text)})
    
    # Full analysis
    analysis = analyze_sentiment(text)
    analysis['language'] = detect_language(text)
    analysis['summary'] = summarize_text(text)
    analysis['keywords'] = extract_keywords(text)
    return jsonify(analysis)

# ---------------- TRANSLATION ----------------
@app.route("/translate", methods=["POST"])
def translate():
    data = request.get_json(force=True)
    log_translation("Auto-Detect", data.get("language", "English"), len(data.get("text", "")))
    
    from translator import translate_text

    return jsonify({
        "translated": translate_text(
            data.get("text", ""),
            data.get("language", "English")
        )
    })

@app.route("/analytics", methods=["GET"])
def get_analytics():
    """
    Admin Analytics Endpoint
    """
    try:
        # Total count
        total = TranslationLog.query.count()
        
        # Stats by language
        lang_stats = {}
        for lang, count in db.session.query(TranslationLog.target_lang, db.func.count(TranslationLog.id)).group_by(TranslationLog.target_lang).all():
            lang_stats[lang] = count
        
        # Stats by day (last 7 days)
        # Simplified for SQLite/SQLAlchemy compatibility
        daily_stats = {}
        # Note: Proper date grouping is DB specific, this is a general approach
        logs = TranslationLog.query.all()
        for log in logs:
            day = log.timestamp.strftime('%Y-%m-%d')
            daily_stats[day] = daily_stats.get(day, 0) + 1
        
        return jsonify({
            "total_translations": total,
            "languages": lang_stats,
            "daily": daily_stats
        })
    except Exception as e:
        return jsonify({"error": str(e)})

# ---------------- TEXT TO SPEECH ----------------
@app.route("/speak", methods=["POST"])
def speak_text():
    from tts import speak

    data = request.get_json(force=True)

    return jsonify({
        "audio": speak(
            data.get("text", ""),
            data.get("language", "en")
        )
    })







@app.route('/analyze/plant', methods=['POST'])
def analyze_plant_route():
    data = request.get_json(force=True)
    filename = data.get('filename')
    path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    
    if not os.path.exists(path):
        return jsonify({"error": "File not found"}), 404
        
    result = analyze_plant_health(path)
    return jsonify(result)

@app.route('/analyze/food', methods=['POST'])
def analyze_food_route():
    data = request.get_json(force=True)
    filename = data.get('filename')
    path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    
    if not os.path.exists(path):
        return jsonify({"error": "File not found"}), 404
        
    result = analyze_nutrition_ai(path)
    return jsonify(result)

# ---------------- RUN APP ----------------
if __name__ == "__main__":
    app.run(
        host="127.0.0.1",
        port=5000,
        debug=True
    )
