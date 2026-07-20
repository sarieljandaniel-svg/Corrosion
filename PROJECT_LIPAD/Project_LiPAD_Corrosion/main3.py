import cv2
import numpy as np
import os

# --- 1. SETUP & PATHS ---
base_dir = os.path.dirname(os.path.abspath(__file__))
dataset_path = os.path.join(base_dir, 'datasetCorrosion/images')

# Deterministic Model Constants (Empirical Data Placeholder)
K_CONSTANT = 0.05  
N_EXPONENT = 0.5   

# Simulation settings for Phase 1
SIMULATED_DISTANCE = 500 # mm
FOCAL_LENGTH = 1400

# Get images from your folder
images = [f for f in os.listdir(dataset_path) if f.lower().endswith(('.jpg', '.png', '.jpeg', '.jfif', '.webp'))]

def get_severity(rar):
    """Classifies rust status based on study [62]"""
    if rar == 0:
        return "Rust-Free", (0, 255, 0)       # Green
    elif rar < 5:
        return "Slight Rust", (0, 255, 255)   # Yellow
    elif rar < 15:
        return "Medium Rust", (0, 165, 255)   # Orange
    else:
        return "Severe Rust", (0, 0, 255)     # Red

for img_name in images:
    path = os.path.join(dataset_path, img_name)
    frame = cv2.imread(path)
    if frame is None: continue

    frame = cv2.resize(frame, (800, 600))
    output_img = frame.copy()

    # --- 2. IMAGE ENHANCEMENT (Reference [60]) ---
    # Convert to YUV to equalize the Luminance (Y) channel for better contrast
    yuv = cv2.cvtColor(frame, cv2.COLOR_BGR2YUV)
    yuv[:,:,0] = cv2.equalizeHist(yuv[:,:,0])
    enhanced_img = cv2.cvtColor(yuv, cv2.COLOR_YUV2BGR)

    # --- UNBIASED THRESHOLDING (Ref [59, 61]) ---
    # Use the standard Hue range for Iron Oxide
    hsv = cv2.cvtColor(enhanced_img, cv2.COLOR_BGR2HSV)
    lower_hsv = np.array([0, 100, 40]) 
    upper_hsv = np.array([25, 255, 200])
    mask_hsv = cv2.inRange(hsv, lower_hsv, upper_hsv)

    # Add the Cr (Chroma) constraint to remove background bias [61]
    ycrcb = cv2.cvtColor(enhanced_img, cv2.COLOR_BGR2YCrCb)
    # Use Otsu's Method to automatically find the "Red-Chroma" threshold
    #removes bias in picking the Cr value manually
    cr_channel = ycrcb[:,:,1]
    _, mask_cr = cv2.threshold(cr_channel, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

    # Final Intersection (Only pixels that pass BOTH are counted)
    final_mask = cv2.bitwise_and(mask_hsv, mask_cr)
    
    # --- STANDARDIZED MORPHOLOGICAL CLEANUP ---

    # 1. Define the Standard Kernel (5x5 Square is the SHM standard)
    kernel = np.ones((1,1), np.uint8)

    # 2. Apply OPENING (Removes tiny noise/dust pixels)
    # This addresses the "False Positives" mentioned in [59]
    cleaned_mask = cv2.morphologyEx(final_mask, cv2.MORPH_OPEN, kernel)

    # 3. Apply CLOSING (Fills small holes inside the rust)
    # This ensures "measurement of ununiform corrosion" is accurate [61]
    cleaned_mask = cv2.morphologyEx(cleaned_mask, cv2.MORPH_CLOSE, kernel)

    # 4. Final Result for RAR Calculation
    final_mask = cleaned_mask
    # --- 6. METRICS & CATEGORIZATION (Reference [62]) ---
    total_pixels = frame.shape[0] * frame.shape[1]
    rust_pixels = cv2.countNonZero(final_mask)
    
    # Rusty Area Ratio (RAR)
    rar = (rust_pixels / total_pixels) * 100
    severity_label, color_code = get_severity(rar)

    # Physical Area Calculation for Deterministic Model
    actual_area_mm2 = (rust_pixels * (SIMULATED_DISTANCE**2)) / (FOCAL_LENGTH**2)
    forecast_30d = actual_area_mm2 + (K_CONSTANT * (30**N_EXPONENT))

    # --- 7. VISUALIZATION (Segmentation Overlay) ---
    tint = np.zeros_like(frame)
    tint[:] = color_code # Tint matches the severity color
    segmentation = cv2.bitwise_and(tint, tint, mask=final_mask)
    cv2.addWeighted(segmentation, 0.6, output_img, 1.0, 0, output_img)

    # UI Display Panel
    cv2.rectangle(output_img, (5, 5), (450, 155), (0,0,0), -1)
    cv2.putText(output_img, f"File: {img_name}", (15, 30), 1, 1.1, (255,255,255), 2)
    cv2.putText(output_img, f"Status: {severity_label}", (15, 60), 1, 1.3, color_code, 2)
    cv2.putText(output_img, f"RAR: {rar:.2f}%", (15, 90), 1, 1.1, (255,255,255), 1)
    cv2.putText(output_img, f"Current Area: {actual_area_mm2:.1f} mm2", (15, 120), 1, 1.1, (255,255,255), 1)
    cv2.putText(output_img, f"30D Forecast: {forecast_30d:.1f} mm2", (15, 150), 1, 1.1, (0,255,255), 2)

    # --- 8. OUTPUT ---
    cv2.imshow("Enhanced Image [60]", enhanced_img)
    cv2.imshow("Corrosion Segmentation System", output_img)
    
    print(f"Processed {img_name}. Severity: {severity_label} (RAR: {rar:.2f}%)")
    
    key = cv2.waitKey(0) & 0xFF
    if key == ord('q'): break

cv2.destroyAllWindows()