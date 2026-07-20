from ultralytics import YOLO

model = YOLO(r'C:\Users\ADMIN\PROJECT_LIPAD\Project_LIPAD_AI\runs\segment\train-2\weights\best.pt')
model.export(format='onnx')

print("[SUCCESS] Model exported to ONNX format. Ready for deployment!")