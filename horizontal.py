import cv2
import numpy as np
import os
import shutil

# --- Parameters from the successful new code ---
ROW_WHITE_PIXEL_RATIO_THRESHOLD = 0.95 
MIN_INTER_PARAGRAPH_GAP_HEIGHT_PX = 20 
MIN_PARAGRAPH_CONTENT_HEIGHT_PX = 30 

def segment_image_paragraphs_refined(input_image_path, output_prefix):
    """
    Segments an image into paragraphs using refined logic, and implements
    the desired flexible file naming convention.

    Args:
        input_image_path (str): The path to the input image file.
        output_prefix (str): A path-like string that defines the output directory
                             and the prefix for the output filenames. 
                             Example: 'output_folder/p_' will save files in
                             'output_folder/' with names like 'p_0001_original.png'.
    """
    # 1. Read Image
    img = cv2.imread(input_image_path)
    if img is None:
        print(f"Error: Could not read image at {input_image_path}")
        return

    # 2. Handle paths and prefixes (from Old Logic)
    base_name_with_ext = os.path.basename(input_image_path)
    base_name, ext = os.path.splitext(base_name_with_ext)
    
    output_dir = os.path.dirname(output_prefix)
    actual_file_prefix = os.path.basename(output_prefix)

    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir, exist_ok=True)
        print(f"Created output directory: {output_dir}")

    # 3. Gentle Crop Attempt (from New Logic)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if contours:
        x_min, y_min, x_max, y_max = img.shape[1], img.shape[0], 0, 0
        for cnt in contours:
            x, y, w, h = cv2.boundingRect(cnt)
            x_min, y_min = min(x_min, x), min(y_min, y)
            x_max, y_max = max(x_max, x + w), max(y_max, y + h)
        cropped_img = img[y_min:y_max, x_min:x_max]
    else:
        cropped_img = img

    # 4. Segmentation Logic (from New Logic)
    blurred = cv2.GaussianBlur(cropped_img, (5, 5), 0)
    gray_cropped = cv2.cvtColor(blurred, cv2.COLOR_BGR2GRAY)
    _, binary_image = cv2.threshold(gray_cropped, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

    height, width = binary_image.shape
    horizontal_projection = np.sum(binary_image, axis=1) / 255
    white_pixel_count_threshold = width * ROW_WHITE_PIXEL_RATIO_THRESHOLD
    is_separator_row = horizontal_projection >= white_pixel_count_threshold
    
    gaps = []
    y = 0
    while y < height:
        if is_separator_row[y]:
            gap_start = y
            while y < height and is_separator_row[y]:
                y += 1
            if y - gap_start >= MIN_INTER_PARAGRAPH_GAP_HEIGHT_PX:
                gaps.append((gap_start, y))
        else:
            y += 1
            
    # 5. Slicing and Saving (Combined Logic)
    cut_points = [0] + [g[0] + (g[1] - g[0]) // 2 for g in gaps] + [height]
    
    output_coords = []
    for i in range(len(cut_points) - 1):
        y_start, y_end = cut_points[i], cut_points[i+1]
        if y_end - y_start >= MIN_PARAGRAPH_CONTENT_HEIGHT_PX:
            output_coords.append((y_start, y_end))

    paragraph_counter = 0
    for y_start, y_end in output_coords:
        if y_end <= y_start: 
            continue

        paragraph_counter += 1
        paragraph_img = cropped_img[y_start:y_end, :]
        
        if paragraph_img.size == 0:
            print(f"Warning: Skipping empty paragraph segment for slice {y_start}-{y_end}")
            continue
        
        # Naming logic from old script
        formatted_counter = f"{paragraph_counter:04d}"
        output_filename = f"{actual_file_prefix}{formatted_counter}_{base_name}{ext}"
        output_path = os.path.join(output_dir, output_filename) if output_dir else output_filename
        
        cv2.imwrite(output_path, paragraph_img)
        print(f"Saved: {output_path}")

    if paragraph_counter == 0:
        print(f"Info: No paragraphs were segmented for {input_image_path} based on the criteria.")