import cv2
import numpy as np
import os

def segment_image_columns(image_path, output_prefix="c"):
    img = cv2.imread(image_path)
    if img is None:
        return

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (5,5), 0)
    _, binary_image = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

    height, width = binary_image.shape
    
    if width < 3:
        return

    vertical_projection = np.sum(binary_image, axis=0) / 255.0

    search_start_x = width // 3
    search_end_x = 2 * width // 3
    
    if search_start_x >= search_end_x:
        split_x = width // 2
    else:
        gutter_candidate_sums = vertical_projection[search_start_x:search_end_x]
        
        if len(gutter_candidate_sums) == 0 or np.max(gutter_candidate_sums) == 0:
            split_x = width // 2
        else:
            peak_idx_in_candidates = np.argmax(gutter_candidate_sums)
            peak_value = gutter_candidate_sums[peak_idx_in_candidates]
            
            gutter_threshold = peak_value * 0.90 

            gutter_start_relative = peak_idx_in_candidates
            while gutter_start_relative > 0 and \
                  gutter_candidate_sums[gutter_start_relative - 1] >= gutter_threshold:
                gutter_start_relative -= 1
            
            gutter_end_relative = peak_idx_in_candidates
            while gutter_end_relative < len(gutter_candidate_sums) - 1 and \
                  gutter_candidate_sums[gutter_end_relative + 1] >= gutter_threshold:
                gutter_end_relative += 1
            
            center_of_gutter_relative = (gutter_start_relative + gutter_end_relative) // 2
            split_x = search_start_x + center_of_gutter_relative

    if split_x <= 0 or split_x >= width:
        split_x = width // 2

    img_col1 = img[:, :split_x]
    img_col2 = img[:, split_x:]

    if img_col1.size == 0 or img_col2.size == 0:
        return

    base, ext = os.path.splitext(os.path.basename(image_path))
    output_path1 = f"{output_prefix}1_{base}{ext}"
    output_path2 = f"{output_prefix}2_{base}{ext}"

    cv2.imwrite(output_path1, img_col1)
    cv2.imwrite(output_path2, img_col2)
