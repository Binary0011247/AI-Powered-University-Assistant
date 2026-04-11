import os
import google.generativeai as genai
from dotenv import load_dotenv

# Load your API key
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    print("❌ No API key found in .env")
else:
    genai.configure(api_key=api_key)
    print("✅ Connected to Google! Here are the models you can use for text generation:")
    
    # Ask Google for a list of all valid models
    for m in genai.list_models():
        if 'generateContent' in m.supported_generation_methods:
            print(f" - {m.name.replace('models/', '')}")