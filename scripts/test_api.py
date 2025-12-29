
import google.generativeai as genai
import os
import sys
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))

from config.settings import GEMINI_API_KEY

genai.configure(api_key=GEMINI_API_KEY)
print("Listing available models...")
for m in genai.list_models():
    if 'generateContent' in m.supported_generation_methods:
        print(m.name)
