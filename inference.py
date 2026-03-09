model = YOLO("yolov8s.pt")
model.train(
    data="/kaggle/input/vehicle-detection-image-dataset/No_Apply_Grayscale/No_Apply_Grayscale/Vehicles_Detection.v8i.yolov8/data.yaml",
    epochs=10,
    imgsz=640,
    batch=16,
    device=0
)



model = YOLO("runs/detect/train/weights/best.pt")
results = model.predict(
    source="/kaggle/input/vehicle-detection-image-dataset/Sample_Video_HighQuality.mp4",
    conf=0.5,
    save=True
)
import cv2
from IPython.display import display, Image

cap = cv2.VideoCapture("Sample_Video_HQ.mp4")
count = 0

while True:
    ret, frame = cap.read()
    if not ret or count > 5:  # juste 50 frames pour test rapide
        break
    # convertir BGR → RGB pour affichage
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    _, im_buf = cv2.imencode(".png", frame_rgb)
    display(Image(data=im_buf.tobytes()))
    count += 1

cap.release()
