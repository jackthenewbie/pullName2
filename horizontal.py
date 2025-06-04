import cv2
import numpy as np
import os

GAUSS_BLUR_KERNEL_SIZE = (5,5)
ROW_WHITE_PIXEL_RATIO_THRESHOLD = 0.98 
MIN_INTER_PARAGRAPH_GAP_HEIGHT_PX = 15 
MIN_PARAGRAPH_CONTENT_HEIGHT_PX = 10 # Minimum height for the actual content part of a paragraph

def segment_image_paragraphs_refined(image_path, output_prefix="paragraph"):
    img = cv2.imread(image_path)
    if img is None:
        print(f"Error: Image not found or unable to read at {image_path}")
        return

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, GAUSS_BLUR_KERNEL_SIZE, 0)
    _, binary_image = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

    height, width = binary_image.shape
    if height < MIN_PARAGRAPH_CONTENT_HEIGHT_PX or width < 10:
        print(f"Info: Image {image_path} is too small (h={height}, w={width}) for paragraph segmentation.")
        return

    horizontal_projection = np.sum(binary_image, axis=1)
    white_row_sum_threshold = width * 255 * ROW_WHITE_PIXEL_RATIO_THRESHOLD
    is_separator_row = horizontal_projection >= white_row_sum_threshold
    
    actual_gaps = []
    y = 0
    while y < height:
        if is_separator_row[y]:
            gap_start_y = y
            while y < height and is_separator_row[y]:
                y += 1
            gap_end_y = y
            gap_height = gap_end_y - gap_start_y
            if gap_height >= MIN_INTER_PARAGRAPH_GAP_HEIGHT_PX:
                actual_gaps.append((gap_start_y, gap_end_y))
        else:
            y += 1
            
    base_name_with_ext = os.path.basename(image_path)
    base_name, ext = os.path.splitext(base_name_with_ext)
    
    output_dir = os.path.dirname(output_prefix)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir, exist_ok=True)
    
    actual_file_prefix = os.path.basename(output_prefix)

    output_paragraph_coords = [] 
    current_para_content_start_y = 0
    current_para_slice_start_y = 0

    gaps_to_iterate = list(actual_gaps) 

    if gaps_to_iterate and gaps_to_iterate[0][0] == 0:
        first_gap_start_y, first_gap_end_y = gaps_to_iterate.pop(0)
        current_para_content_start_y = first_gap_end_y
        current_para_slice_start_y = (first_gap_start_y + first_gap_end_y) // 2
        current_para_slice_start_y = max(0, current_para_slice_start_y)

    for gap_start_y, gap_end_y in gaps_to_iterate:
        current_para_content_end_y = gap_start_y
        current_para_slice_end_y = (gap_start_y + gap_end_y) // 2
        current_para_slice_end_y = min(height, current_para_slice_end_y)

        actual_content_height = current_para_content_end_y - current_para_content_start_y
        
        if actual_content_height >= MIN_PARAGRAPH_CONTENT_HEIGHT_PX:
            if current_para_slice_end_y > current_para_slice_start_y:
                output_paragraph_coords.append((current_para_slice_start_y, current_para_slice_end_y))
        
        current_para_content_start_y = gap_end_y
        current_para_slice_start_y = current_para_slice_end_y 

    current_para_content_end_y = height
    current_para_slice_end_y = height

    actual_content_height = current_para_content_end_y - current_para_content_start_y
    if actual_content_height >= MIN_PARAGRAPH_CONTENT_HEIGHT_PX:
        if current_para_slice_end_y > current_para_slice_start_y:
             output_paragraph_coords.append((current_para_slice_start_y, current_para_slice_end_y))

    if not output_paragraph_coords:
        if height > 0 and width > 0:
             output_paragraph_coords.append((0, height))

    paragraph_counter = 0
    for y_start, y_end in output_paragraph_coords:
        if y_end <= y_start: 
            continue

        paragraph_counter += 1
        paragraph_img = img[y_start:y_end, :]
        
        if paragraph_img.size == 0:
            print(f"Warning: Skipping empty paragraph segment for slice {y_start}-{y_end}")
            continue
        
        formatted_counter = f"{paragraph_counter:04d}"
        output_filename = f"{actual_file_prefix}{formatted_counter}_{base_name}{ext}"
        output_path = os.path.join(output_dir, output_filename) if output_dir else output_filename
        cv2.imwrite(output_path, paragraph_img)

    if paragraph_counter == 0:
        print(f"Info: No paragraphs were segmented and saved for {image_path} based on the criteria.")

def horizontal_cut(input_image_path, output_images):
    # --- ASSUMING THE INPUT FILE EXISTS AS PER YOUR INSTRUCTION ---
    input_image_filepath_main = input_image_path 
    test_files_dir_main = output_images
    
    # Create output directory if it doesn't exist
    # (This is for output, not input, so I assume this part is okay)
    if not os.path.exists(test_files_dir_main):
        os.makedirs(test_files_dir_main, exist_ok=True)
    else:
        # Optional: Clean up old test files if any for a fresh run
        for f in os.listdir(test_files_dir_main):
            if f.startswith(os.path.basename(os.path.join(test_files_dir_main, "p_"))): # Be more specific
                try:
                    os.remove(os.path.join(test_files_dir_main, f))
                except OSError as e:
                    print(f"Error deleting file {os.path.join(test_files_dir_main, f)}: {e}")

    output_prefix_main = os.path.join(test_files_dir_main, "p_")
    
    # Check if the input file actually exists before trying to process
    if not os.path.exists(input_image_filepath_main):
        print(f"CRITICAL ERROR: The specified input file '{input_image_filepath_main}' does not exist. Please ensure the path is correct.")
    else:
        print(f"Segmenting {input_image_filepath_main} into {output_prefix_main}...")
        segment_image_paragraphs_refined(input_image_filepath_main, output_prefix=output_prefix_main)
        print("Segmentation complete.")