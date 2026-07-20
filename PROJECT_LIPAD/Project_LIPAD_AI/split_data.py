import os
import random
import shutil
from tqdm import tqdm

# ==================== CONFIGURATION ====================
# Point these to where your raw METU images and masks currently live:
RAW_IMG_DIR = r"C:\Users\ADMIN\OneDrive\Desktop\RAW_IMAGES_ALL" 
RAW_MASK_DIR = r"C:\Users\ADMIN\OneDrive\Desktop\RAW_MASKS_ALL"

# Destination directories (Phase 1 structure)
DEST_IMG_TRAIN = r"datasets/images/train"
DEST_IMG_VAL = r"datasets/images/val"
# =======================================================

def split_dataset(train_percent=0.8):
    # Ensure destination directories exist
    os.makedirs(DEST_IMG_TRAIN, exist_ok=True)
    os.makedirs(DEST_IMG_VAL, exist_ok=True)

    # Get and shuffle all raw images
    images = [f for f in os.listdir(RAW_IMG_DIR) if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
    if not images:
        print("Error: No images found in the raw images directory! Check your path.")
        return
        
    random.seed(42)  # Fixed seed so splits are reproducible
    random.shuffle(images)

    # Calculate index split point
    split_idx = int(len(images) * train_percent)
    train_images = images[:split_idx]
    val_images = images[split_idx:]

    print(f"Total found: {len(images)} images.")
    print(f"Splitting: {len(train_images)} to Train, {len(val_images)} to Val.")

    # Helper function to copy images
    def copy_files(file_list, dest_folder):
        for filename in tqdm(file_list, desc=f"Copying to {os.path.basename(dest_folder)}"):
            src_path = os.path.join(RAW_IMG_DIR, filename)
            dest_path = os.path.join(dest_folder, filename)
            shutil.copy(src_path, dest_path)

    copy_files(train_images, DEST_IMG_TRAIN)
    copy_files(val_images, DEST_IMG_VAL)
    print("Dataset successfully split into Train and Val folders!\n")

if __name__ == "__main__":
    split_dataset()