import os
from ultralytics import YOLO

# This block is MANDATORY on Windows to prevent multiprocessing loops
if __name__ == '__main__':

    # 1. Load your best weights from the original run
    model = YOLO(r"C:\Users\ADMIN\PROJECT_LIPAD_ANALYSIS\Corrosion\LIPAD_YOLO_TRAINING\crack_detection\runs\yolov8\crack_yolov8_seg\weights\last.pt")

    # 2. Run the fine-tuning session with your exact parameter choices
    model.train(
        resume=True,
        data="dataset.yaml",   # Path to your data config file
        epochs=50,                  # Train for 50 more epochs
        project="runs/detect",       # Point to your original project directory
        name="train",               # Point to your original folder name
        exist_ok=True,               # FORCES YOLO to stay inside 'train' instead of creating 'train2'
        lr0=0.01,      # Manually set a smaller learning rate for fine-tuning
        lrf=0.01,       # Manually set a smaller learning rate for fine-tuning
    )