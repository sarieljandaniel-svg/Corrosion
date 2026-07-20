# C:\Users\ADMIN\PROJECT_LIPAD\Project_LIPAD_AI\resume_train.py
from ultralytics import YOLO

if __name__ == '__main__':
    # 1. Point directly to the 'last.pt' weights generated in your crash run folder
    # Note: Check if your directory is 'train' or 'train-2' based on the error log!
    model = YOLO(r"C:\Users\ADMIN\PROJECT_LIPAD\Project_LIPAD_AI\runs\segment\train-2\weights\last.pt")
    
    # 2. Instruct the engine to resume from that exact checkpoint
    model.train(resume=True)