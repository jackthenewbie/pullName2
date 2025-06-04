import os
import time
from config import creds, spreadsheet_id, sheet_id
import vertical
import horizontal
import process
import prompt
from auth import auth
import random
import fetch
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
    
    for f in os.listdir(images_path):
        is_image = str(f).endswith(".png")
        if is_image:
            image_path = os.path.join(images_path, f)
            generate_paragraph_cut(image_path)
            number_of_scientist = 0  #recording number of biographical entry
            for paragraph_png in os.listdir("horizontal"):
                sheet = auth(random.choice(creds))
                paragraph = os.path.join("horizontal", paragraph_png)
                logger.info("------------------------------------------------")
                logger.info(paragraph_png)
                person = process.ai_response_to_list(prompt.prompt2_5, paragraph)
                time.sleep(3)
                if(len(person)==0): continue
                if(not process.check_name_capitalization(person)): continue
                number_of_scientist+=1
                update_name(sheet, spreadsheet_id, sheet_id, person)
            gemini_count_over_gemini_flash = int(fetch.gemini_response(prompt.prompt_asking_total_biographical(), image_path, "gemini-2.5-flash-preview-05-20", 0))
            if(number_of_scientist!=gemini_count_over_gemini_flash):
                print("Something wrong, check with the logs and sheet before continuing.")
                logger.info("Mismatch ")
                logger.info(f"number_of_scientist record: {number_of_scientist}")
                logger.info(f"gemini_count_over_gemini_flash: {gemini_count_over_gemini_flash}")
                break
main("files")

#count = fetch.gemini_response(prompt.prompt_asking_total_biographical(), "files/page_017.png", "gemini-2.5-flash-preview-05-20")
#print(count)

#count = fetch.gemini_response(prompt.prompt_asking_total_biographical(), "files/page_017.png", "gemini-2.5-flash-preview-05-20", 0)
#print(count)