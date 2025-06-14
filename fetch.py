import random
import time
import openai
from config import gemini_key
from prompt import *
from logger import logger
from google.genai import types, Client
def get_ai_response(text, file_path=""):
    return gemini_response(text, file_path=file_path)

def openai_response(text, file_path=""):
    client = openai.Client(
        base_url="http://localhost:11434/v1",
        api_key="key"
    )
    response = client.chat.completions.create(
        model="qwen3:1.7b",  # change to your model name
        temperature = 0.4,
        messages=[{
            'role': 'user',
            'content': prompt(text, think=False),
        }]
    )
    return response.choices[0].message.content
def tryupload(client: Client, file_path: str):
    image=None
    index=0
    while(image==None and index<3):
        try:
            image = client.files.upload(file=file_path)
        except:
            index+=1
            time.sleep(5*index)
    return image
def gemini_response(text, file_path=None, model="random", temperature=0.75, thinking=False):
    models=["gemini-2.0-flash-lite", "gemini-1.5-flash"]
    if(model=="random"):
        model = random.choice(models)
    content=[text]
    image=None
    client = Client(api_key=gemini_key)
    if file_path != None:
        image = tryupload(client, file_path)
        content.append(image)
    if(thinking):
        thinking = types.ThinkingConfig(include_thoughts=True)
    else: thinking = None
    response=None
    while(len(models)!=0):
        try:
            response = client.models.generate_content(
                model=model, 
                contents=content,
                config=types.GenerateContentConfig(temperature=temperature,
                                                   thinking_config=None)
                )
            break
        except Exception as e:
            logger.error(str(e))
            models.remove(model)
            model=random.choice(models)
    if(response is None): raise Exception("Something has gone wrong, check logs")
    if file_path != None:
        client.files.delete(name=image.name)
    return response.text