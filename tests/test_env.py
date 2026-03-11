import os
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("ORS_API_KEY")

print("Chave carregada:", api_key)