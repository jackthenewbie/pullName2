import json
from fetch import *
import os
import prompt
import re
#https://aistudio.google.com/prompts/1pJ2UKH76pv_Wk8nlMDxP-cVShuGNlxD6
def check_name_capitalization(person):

    pattern_lastname = r"^[A-Z- ]+$"
    pattern_firstname = r"^[A-Z- ]+$"
    match_element_0 = re.fullmatch(pattern_lastname, person[0])
    match_element_1 = re.fullmatch(pattern_firstname, person[1])
    if match_element_0 and match_element_1:
        return True
    else:
        return False

    
def remove_files(dir_path):
    """Removes all files directly within dir_path using os.scandir."""
    if not os.path.isdir(dir_path):
        print(f"Error: Directory '{dir_path}' not found.")
        return

    print(f"Attempting to remove files from: {dir_path}")
    with os.scandir(dir_path) as entries:
        for entry in entries:
            try:
                # entry.is_file() is True for regular files and symlinks to files.
                # If you wanted to be explicit about symlinks (e.g., only remove symlinks to files):
                # if entry.is_file(follow_symlinks=False) or (entry.is_symlink() and os.path.isfile(entry.path)):
                if entry.is_file(): # This correctly handles symlinks to files
                    os.remove(entry.path)
                    print(f"  Removed: {entry.name} (path: {entry.path})")
                else:
                    print(f"  Skipped (not a file): {entry.name}")
            except OSError as e:
                print(f"  Error removing {entry.name}: {e}")

def json_from_response_of_text(text, file_path):
    ai_response = get_ai_response(text, file_path)
    extracted_json_string = None
    current_pos = len(ai_response)
    #print(ai_response)
    while current_pos > 0:
        start_index = ai_response.rfind('{', 0, current_pos)
        if start_index == -1:
            break  # No '{' found
        try:
            # Attempt to decode from this point
            # raw_decode returns (python_object, index_of_end_in_substring)
            _, length = json.JSONDecoder().raw_decode(ai_response[start_index:])
            extracted_json_string = ai_response[start_index : start_index + length]
            extracted_json_string = json.loads(extracted_json_string)
            break  # Successfully extracted a JSON object string
        except json.JSONDecodeError:
            # This '{' was not the start of a valid JSON object, or json is malformed from here
            # Continue searching from before this problematic '{'
            current_pos = start_index
    return extracted_json_string
def ai_response_to_list(text, file_path):
    result = []
    answer = json_from_response_of_text(text, file_path)
    if( answer == {} ):
        return result
    if( answer["firstname"] is None 
        or answer["lastname"] is None): return result
    for key in answer:
        if answer[key] is None or str(answer[key]) == "null":
            answer[key] = "\u200B"
        if key == "firstname" or key == "lastname":
            answer[key] = str(answer[key]).replace("(", "").replace(")", "").replace(",", "").replace(".", "")
        result.append(answer[key])
    return result
