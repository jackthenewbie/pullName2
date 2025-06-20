import json
from typing import List
from fetch import *
import os
import prompt
from logger import logger
import re
import random
import time
import ast
#https://aistudio.google.com/prompts/1pJ2UKH76pv_Wk8nlMDxP-cVShuGNlxD6
def check_name_capitalization(person):

    pattern_lastname = r"^[A-Z- ']+$"
    pattern_firstname = r"^[A-Z- ']+$"
    match_element_0 = re.fullmatch(pattern_lastname, person[0])
    match_element_1 = re.fullmatch(pattern_firstname, person[1])
    if match_element_0 and match_element_1:
        return True
    else:
        return False

def sanatize_response(text):
    match = re.search(r'\[.*', text)
    if match: result = match.group(0)
    else: result = text
    return result
    
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
def ai_response_to_list(text, file_path, custom_json = None):
    result = []
    if custom_json == None:
        answer = json_from_response_of_text(text, file_path)
    else:
        answer = custom_json
    if( answer == {} ):
        return result
    if( answer["firstname"] is None 
        or answer["lastname"] is None): return result
    for key in answer:
        if answer[key] is None or str(answer[key]) == "null" or str(answer[key]).strip() == "":
            answer[key] = "\u200B"
        if key == "firstname" or key == "lastname":
            answer[key] = str(answer[key]).replace("(", "").replace(")", "").replace(",", "").replace(".", "")
        if key == "b" or key == "m" or key == "c":
            if(answer[key]!="\u200B"):
                try:
                    answer[key]=str(int(answer[key]))
                except:
                    logger.error("Failed to minimize number str")
        result.append(answer[key])
    while(len(result)<5) :
        result.append("\u200B")
    if len(result) > 5: result=result[:5]
    return result
def looks_like_human(person):
    result = gemini_response(text=fprompt_reconfirm(str(person)))
    if("True" in result):
        return True
    else: return False
def total_paragraph(image_path):
    models = ["gemini-2.5-flash", "gemini-2.5-flash-preview-04-17", "gemini-2.0-flash"]
    numbers_of_paragraph = []
    for i in range(3):
        model = random.choice(models)
        guessing_total_paragraph = gemini_response(prompt.prompt_asking_total_biographical(), file_path=image_path, model=model, temperature=0.5, thinking=True)
        gemini_count_over_gemini_flash = 0
        try:
            gemini_count_over_gemini_flash = int(guessing_total_paragraph)
            numbers_of_paragraph.append(gemini_count_over_gemini_flash)
            logger.info(f"Count total has result in {gemini_count_over_gemini_flash} with model: {model}")
        except:
            logger.warning(f"Failed to check total paragraph, please manually check log at model: {model}")
            numbers_of_paragraph.append(100)
            numbers_of_paragraph.append(0)
        time.sleep(3)
    return numbers_of_paragraph
def total_scan(image_path):
    models = ["gemini-2.5-flash", "gemini-2.5-flash-preview-04-17", "gemini-2.0-flash"]
    model = random.choice(models)
    data = gemini_response(prompt_scan_whole_page, image_path, "gemini-2.0-flash", 0.8, thinking=False) 
    data = str(data).replace("```", "").replace("json", "", 1)
    data_as_dicts = json.loads(data)
    return data_as_dicts
def fetch_total(image_path):
    data = []
    for i in range(3):
        if(len(data)==0):
            data = total_scan(image_path)
        else: break
        time.sleep(30)
    if(len(data)==0): raise Exception("Something seriously wrong is happening, abort")
    return data
def reconfirm_on_number(image_path) -> List[List[str]]:
    datas=[]
    for _ in range(3):
        data = gemini_response(prompt.reconfirm_on_numberf(), image_path, "gemma-3-27b-it", 1, thinking=False)
        data = sanatize_response(data)
        data = data.replace("```","").replace("\n","").replace(" ","").replace("python","").replace("json","")
        sleep_time=3
        try:
            data = [str(x) for x in ast.literal_eval(str(data))]
            datas.append(data)
        except Exception as e:
            logger.error(f"Failed to parse data: \n{data} \nwith error: {str(e)}")
            sleep_time*=(_+1)
        time.sleep(_*3)
    return datas
def fixing_attempt(*lists):
    logger.info(f"Attempting to fix...")
    data=[max(set(column), key=column.count) for column in zip(*lists)]
    return data
def check_missing(data, person, image_moddified_person):
    for person_in_data in data:
        person_in_data_index=data.index(person_in_data)
        person_in_data = ai_response_to_list(None, None, person_in_data)
        if(len(person_in_data)==0): continue
        if(person[0] == person_in_data[0] and (person[1] in person_in_data[1] or person_in_data[1] in person[1])):
            if(person[2] == person_in_data[2] and person[3] == person_in_data[3] and person[4] == person_in_data[4]):
                logger.info("Good to go.")
            else:
                logger.warning(f"Total scan has different value.")
                logger.warning(f"person:{str(person[2:])} || person_in_data:{str(person_in_data[2:])}")
                reconfirm_data=reconfirm_on_number(image_moddified_person)
                person[2:] = fixing_attempt(person[2:], person_in_data[2:], *reconfirm_data)
            del data[person_in_data_index]
            return
        elif(person[2] == person_in_data[2] and 
             person[3] == person_in_data[3] and 
             person[4] == person_in_data[4]
             ):
            logger.info(f"Possibly person[1]=\"{str(person)}\" and person_in_data[1]=\"{str(person_in_data)}\" are the same person, updated anyway")
            #if(len(person[1]) < len(person_in_data[1])): person[1]=person_in_data[1]
            #del data[person_in_data_index]
            #return
        

    logger.warning(f"Person not exist in total scan, please manually check it.\n{person}")
        