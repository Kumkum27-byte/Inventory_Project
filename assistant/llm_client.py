from google import genai
from dotenv import load_dotenv

load_dotenv()

import os
client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))

def ask_llm(prompt : str) -> str:
    response = client.models.generate_content(model="gemini-2.5-flash", contents=prompt)
    return response.text
