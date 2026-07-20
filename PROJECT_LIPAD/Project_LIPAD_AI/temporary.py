from ultralytics import YOLO

# This forces the ultralytics engine to automatically convert and import the structure
model = YOLO("C:\\Users\\ADMIN\\PROJECT_LIPAD\\Project_LIPAD_AI\\models\\yolov5s_best.pt")
print("[SUCCESS] Model successfully refactored for modern runtime engines!")