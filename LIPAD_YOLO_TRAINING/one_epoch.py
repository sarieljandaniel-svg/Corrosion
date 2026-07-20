import os
import sys
import time
from pathlib import Path

WORKSPACE = r"C:\Users\ADMIN\PROJECT_LIPAD_ANALYSIS\Corrosion\LIPAD_YOLO_TRAINING"
sys.path.insert(0, WORKSPACE)
os.chdir(WORKSPACE)

from ultralytics import YOLO

dataset_yaml = os.path.join(WORKSPACE, "crack_detection", "dataset.yaml")

print("[TEST] 1-epoch local training...\n")
print(f"Workspace: {WORKSPACE}")
print(f"Dataset YAML: {dataset_yaml}")

start = time.time()

try:
    model = YOLO('yolo12n-seg.yaml')
    results = model.train(
        data=dataset_yaml,
        epochs=1,
        imgsz=640,
        batch=8,
        device=0,
        workers=0,  # Windows: use 0 workers
        project=os.path.join(WORKSPACE, "crack_detection/runs"),
        name="test_1epoch_local",
        verbose=False
    )
    elapsed = time.time() - start
    
    print(f"\n{'='*70}")
    print(f"✓ 1 EPOCH COMPLETED in {elapsed:.1f} seconds ({elapsed/60:.2f} minutes)")
    print(f"{'='*70}")
    print(f"\n📊 TIME ESTIMATES FOR 150 EPOCHS:")
    print(f"   yolov12n-seg: {elapsed * 150 / 3600:.2f} hours")
    print(f"   yolov11n-seg: ~{elapsed * 150 / 3600 * 0.9:.2f} hours [~10% faster]")
    print(f"   yolov8n-seg:  ~{elapsed * 150 / 3600 * 0.85:.2f} hours [~15% faster]")
    print(f"\n   ALL 3 SEQUENTIAL: ~{elapsed * 150 / 3600 * (1 + 0.9 + 0.85):.2f} hours")
    print(f"{'='*70}")
    
except Exception as e:
    print(f"\n✗ FAILED: {str(e)}")
    import traceback
    traceback.print_exc()