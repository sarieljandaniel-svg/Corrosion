import os
# Keep offline mode active to avoid GitHub API errors
os.environ["YOLO_OFFLINE"] = "true"

from ultralytics import YOLO

if __name__ == '__main__':

    # 1. Point directly to the 'last.pt' file in the folder you manually stopped
    # Check your runs/detect/ directory to make sure 'train2' (or train3, etc.) matches your current run
    model = YOLO(r"C:\Users\ADMIN\PROJECT_LIPAD_ANALYSIS\Corrosion\LIPAD_YOLO_TRAINING\crack_detection\runs\yolov8\crack_yolov8_seg\weights\last.pt")

    # 2. Kick off the resume and clamp it to your 50-epoch target
    # You don't need to re-state parameters (augment, close_mosaic, etc.) 
    # because YOLO reads them directly from the run's existing configuration logs.
    model.train(
        resume=True,
        epochs=50
    )