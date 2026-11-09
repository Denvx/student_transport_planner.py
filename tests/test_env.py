import os
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("ORS_API_KEY")

# Nunca imprimir o valor da chave (iria para logs do CI) — só se ela está definida.
print("ORS_API_KEY definida:", bool(api_key))