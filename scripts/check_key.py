import os
from dotenv import load_dotenv
load_dotenv()
print(f"Key present: {bool(os.getenv('PERPLEXITY_API_KEY'))}")
