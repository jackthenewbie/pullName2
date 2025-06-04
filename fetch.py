import openai
from config import gemini_key
from prompt import *
from google.genai import types, Client
def get_ai_response(text, file_path=""):
    return gemini_response(text, file_path)

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
def gemini_response(text, file_path, model="gemma-3-27b-it", temperature=1):
    
    client = Client(api_key=gemini_key)
    image = client.files.upload(file=file_path)
    response = client.models.generate_content(
        model=model, 
        contents=[image, text],
        config=types.GenerateContentConfig(temperature=temperature,
                                           thinking_config=types.ThinkingConfig(include_thoughts=True))
        )
    return response.text
