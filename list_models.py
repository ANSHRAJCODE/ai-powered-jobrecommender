# list_models.py
import os
# import google.generativai as genai
import google.generativeai as genai
from dotenv import load_dotenv

# Load and configure API key
load_dotenv()
try:
    genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
    print("--- Available Gemini Models for Your API Key ---")

    # List all models and filter for the ones that can generate content
    for model in genai.list_models():
        if 'generateContent' in model.supported_generation_methods:
            print(model.name)

    print("\n-------------------------------------------------")
except Exception as e:
    print(f"An error occurred: {e}")