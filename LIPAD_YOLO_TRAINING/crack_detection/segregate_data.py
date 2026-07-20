import os
import random
import shutil
import yaml

def segregate_dataset(base_path, output_base, split_ratio=[0.33, 0.33, 0.34]):
    """
    Automates dataset segregation into 3 distinct subsets for Ensemble training.
    Assumes layout: base_path/images/train and base_path/labels/train
    """
    img_dir = os.path.join(base_path, 'images', 'train')
    lbl_dir = os.path.join(base_path, 'labels', 'train')
    
    # Get all matching image-label pairs
    all_files = [f for f in os.listdir(img_dir) if f.endswith(('.jpg', '.png'))]
    random.shuffle(all_files)
    
    subsets = ['subset_s', 'subset_m', 'subset_x']
    start_idx = 0
    
    for i, subset in enumerate(subsets):
        # Calculate split indices
        end_idx = start_idx + int(len(all_files) * split_ratio[i])
        if i == len(subsets) - 1: end_idx = len(all_files) # Ensure last slice takes remainder
        
        current_files = all_files[start_idx:end_idx]
        subset_path = os.path.join(output_base, subset)
        
        # Create directories
        for folder in ['images/train', 'labels/train']:
            os.makedirs(os.path.join(subset_path, folder), exist_ok=True)
            
        # Copy files to respective subset
        for f in current_files:
            base_name, _ = os.path.splitext(f)
            shutil.copy(os.path.join(img_dir, f), os.path.join(subset_path, 'images/train', f))
            shutil.copy(os.path.join(lbl_dir, base_name + '.txt'), os.path.join(subset_path, 'labels/train', base_name + '.txt'))
        
        # Generate the unique YAML config for this model size
        yaml_data = {
            'path': os.path.abspath(subset_path),
            'train': 'images/train',
            'val': os.path.abspath(os.path.join(base_path, 'images/val')), # Unified validation
            'names': {0: 'crack'}
        }
        with open(f'{subset}.yaml', 'w') as yfile:
            yaml.dump(yaml_data, yfile)
            
        print(f"[SUCCESS] {subset} prepared with {len(current_files)} images.")
        start_idx = end_idx

if __name__ == "__main__":
    PROJECT_ROOT = r"C:\Users\ADMIN\PROJECT_LIPAD_ANALYSIS\Corrosion\LIPAD_YOLO_TRAINING\crack_detection\datasets\datasets"
    segregate_dataset(PROJECT_ROOT, PROJECT_ROOT)