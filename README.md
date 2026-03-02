# 🎥 AI WEB CAM Layer

AI WEB CAM Layer is a real-time AI-powered computer vision web application that integrates Object Detection, OCR, NLP, Translation, and Speech Synthesis using modern AI frameworks.

It uses YOLOv8 for object detection, EasyOCR for text extraction, Google Gemini for AI insights, and multiple NLP tools for intelligent text processing.

---

## 🚀 Features

- 🎯 Real-time Object Detection (YOLOv8)
- 📝 Optical Character Recognition (EasyOCR)
- 🌍 Language Translation Support
- 😊 Sentiment Analysis (TextBlob)
- 🔊 Text-to-Speech Output (gTTS)
- 🧠 AI Insights with Google Gemini
- 🔐 Secure Authentication System
- 📦 SQLite Database Integration
- 🌐 Interactive Web Dashboard

---

## 🏗️ Tech Stack

### Backend
- Python
- Flask
- Flask-SQLAlchemy
- Werkzeug

### Frontend
- HTML5
- CSS3
- JavaScript (ES6)
- Jinja2

### Database
- SQLite

### Machine Learning / AI
- YOLOv8 (Ultralytics)
- Google Gemini
- EasyOCR
- OpenCV
- PyTorch (Torch)

### NLP / Speech
- TextBlob
- Deep-Translator
- gTTS

---

## 📂 Project Structure

```
AI-WEB-CAM-Layer/
│
├── app.py
├── models.py
├── static/
│   ├── css/
│   ├── js/
│   └── uploads/
├── templates/
│   ├── index.html
│   ├── dashboard.html
│   └── login.html
├── instance/
│   └── database.db
├── requirements.txt
└── README.md
```

---

## ⚙️ Installation Guide

### 1️⃣ Clone Repository

```bash
git clone https://github.com/your-username/AI-WEB-CAM-Layer.git
cd AI-WEB-CAM-Layer
```

### 2️⃣ Create Virtual Environment

```bash
python -m venv venv
```

Activate:

Windows:
```bash
venv\Scripts\activate
```

Mac/Linux:
```bash
source venv/bin/activate
```

### 3️⃣ Install Dependencies

```bash
pip install -r requirements.txt
```

### 4️⃣ Run Application

```bash
python app.py
```

Open in browser:
```
http://127.0.0.1:5000
```

---

## 🔄 How It Works

1. Webcam captures live video.
2. YOLOv8 detects objects in real-time.
3. EasyOCR extracts visible text.
4. Extracted text is:
   - Analyzed for sentiment
   - Translated into selected language
   - Sent to Gemini for AI interpretation
5. Output can be converted into speech.
6. Results are displayed on dashboard and optionally stored in database.

---

## 📊 Use Cases

- Smart Surveillance
- AI Learning Assistant
- Live Text Translation
- Accessibility Tools
- Intelligent Document Scanner

---

## 🔐 Security

- Password hashing with Werkzeug
- Flask session authentication
- SQLAlchemy ORM protection
- Secure file handling

---

## 📌 Future Improvements

- Real-time streaming optimization
- Docker deployment
- Cloud hosting (AWS / GCP)
- REST API integration
- Multi-language speech recognition

---

## 🤝 Contributing

1. Fork the repo
2. Create feature branch
3. Commit changes
4. Push branch
5. Open Pull Request

---

## 📜 License

MIT License

---

## 👨‍💻 Author

Jayesh Hegde
