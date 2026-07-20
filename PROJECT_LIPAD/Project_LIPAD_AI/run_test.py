from ultralytics import YOLO

# 1. Load your newly trained high-resolution model
# This points to the best-performing weights generated during your 150-epoch run
model = YOLO(r'C:\Users\ADMIN\PROJECT_LIPAD\Project_LIPAD_AI\runs\segment\train-2\weights\best.pt')

# 2. Run inference on your unseen test images
# We set imgsz=640 to match your training resolution for maximum precision
results = model.predict(
    source='datasets/images/test', 
    save=True,        # Saves the visual images with orange masks
    save_txt=True,    # Saves the raw polygon coordinates in labels/
    imgsz=640, 
    conf=0.5          # Only shows cracks the model is >50% sure about
)

print("[SUCCESS] Testing complete. Results saved in runs/segment/predict/")