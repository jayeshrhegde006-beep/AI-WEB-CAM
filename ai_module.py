from ultralytics import YOLO
import cv2

MODEL_PATH = "yolov8n.pt"
_model = None


def get_model():
    global _model
    if _model is None:
        _model = YOLO(MODEL_PATH)
    return _model


def detect_objects(image_source):
    """
    detect_objects now supports both file paths AND numpy arrays (images in memory).
    This is crucial for sub-1-second detection.
    """
    if isinstance(image_source, str):
        img = cv2.imread(image_source)
    else:
        img = image_source

    if img is None:
        return []

    model = get_model()
    # conf=0.25 is standard, imgsz=640 is default but explicit for speed consistency
    results = model(img, conf=0.25, verbose=False, imgsz=640)

    detections = []
    for r in results:
        for box in r.boxes:
            cls_id = int(box.cls[0])
            label = r.names[cls_id]
            confidence = float(box.conf[0])

            detections.append({
                "label": label,
                "confidence": round(confidence, 2)
            })

    return detections
