import os
import time
from config import creds, spreadsheet_id, sheet_id
import vertical
import horizontal
import process
import prompt
from auth import auth
import random
import shutil
import fetch
from db import db
from sheetf import update_name
def clean():
    process.remove_files("vertical/")
    process.remove_files("horizontal/")
def generate_paragraph_cut(image_path):
    
    clean()
    vertical.segment_image_columns(image_path, "vertical/c")
    for f in os.listdir("vertical"):
        is_image = str(f).endswith(".png")
        if is_image:
            horizontal_to_cut = os.path.join("vertical", f)
            print(horizontal_to_cut)
            prefix_of_vertical = str(f).split("_")[0]
            horizontal.segment_image_paragraphs_refined(horizontal_to_cut, f"horizontal/{prefix_of_vertical}_p")
from logger import logger
import datetime
def main(images_path):
    images = os.listdir(images_path)
    images.sort()
    for f in images:
        is_image = str(f).endswith(".png")
        image_path = os.path.join(images_path, f)
        if is_image and (not db.get(image_path) or db.get(image_path) == "False"):
            db.set(image_path, "False")
            generate_paragraph_cut(image_path)
            number_of_scientist = 0  #recording number of biographical entry
            data = process.total_scan(image_path)
            for paragraph_png in os.listdir("horizontal"):
                sheet = auth(random.choice(creds))
                paragraph = os.path.join("horizontal", paragraph_png)
                logger.info("------------------------------------------------")
                logger.info(paragraph_png)
                person = process.ai_response_to_list(prompt.prompt(), paragraph)
                time.sleep(3)
                logger.info(person)
                if(len(person)==0): continue
                if(not process.check_name_capitalization(person)):
                    if(not process.looks_like_human(person)):
                        logger.warning("---------------SKIPPED----------------") 
                        continue
                number_of_scientist+=1
                update_name(sheet, spreadsheet_id, sheet_id, person)
                #Check if person exist
                process.check_missing(data, person)
            db.set(image_path, "True")
            #Leftover perhaps miss by code
            for person_in_data in data:
                person_as_list = process.ai_response_to_list(None, None, person_in_data)
                logger.warning(f"Missing person: {str(person_as_list)} at {image_path}")

                with open(f"to_sheet/for_{str(f).replace("png", "")}.txt", 'a') as file:
                    file.write(f"{str(person_as_list)}\n")
        done = os.path.join(os.path.dirname(image_path), "done")
        os.makedirs(done, exist_ok=True)
        shutil.move(image_path, done)
main("files")
