import openai
from config import gemini_key
from prompt import *
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
def gemini_response(text, file_path=None, model="gemma-3-27b-it", temperature=0, thinking=False):
    content=[text]
    image=None
    client = Client(api_key=gemini_key)
    if file_path != None:
        image = client.files.upload(file=file_path)
        content.append(image)
    if(thinking):
        thinking = types.ThinkingConfig(include_thoughts=True)
    else: thinking = None
    response = client.models.generate_content(
        model=model, 
        contents=content,
        config=types.GenerateContentConfig(temperature=temperature,
                                           thinking_config=None)
        )
    if file_path != None:
        client.files.delete(name=image.name)
    return response.text
#test = gemini_response(prompt_asking_total_biographical(), "files/page_0027.png", "gemini-1.5-flash", 0, thinking=True)
#test = gemini_response(text=prompt(), file_path="horizontal/c1_p0002_c1_page_0024.png", temperature=0)
#ask = ['SUMMERS', 'spec lectr', '\u200b', '\u200b', '\u200b']
#test = gemini_response(text=fprompt_reconfirm(str(ask)))
#print(fprompt_reconfirm(str(ask)))
#print(test)
#client = Client(api_key=gemini_key)
#print('My files:')
#for f in client.files.list():
#    client.files.delete(name=f.name)