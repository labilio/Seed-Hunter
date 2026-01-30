
import os
from dotenv import load_dotenv
from config import config

load_dotenv()

print(f"LLM_PROVIDER: {config.LLM_PROVIDER}")
print(f"LLM_MODEL: {config.LLM_MODEL}")
print(f"DEEPSEEK_API_KEY: {os.getenv('DEEPSEEK_API_KEY')}")
print(f"OPENAI_API_KEY: {os.getenv('OPENAI_API_KEY')}")
