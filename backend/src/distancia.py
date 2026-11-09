import os
from dotenv import load_dotenv
import openrouteservice

load_dotenv()

api_key = os.getenv("ORS_API_KEY")

# Sem ORS_API_KEY, `client` fica None em vez de derrubar o processo no import
# (openrouteservice.Client(key=None) levanta ValueError na hora da criação).
# O erro só aparece quando alguém de fato tenta calcular uma rota, com
# mensagem clara — não mais um crash silencioso no boot da aplicação.
client = openrouteservice.Client(key=api_key) if api_key else None


def distancia_rota(p1, p2):

    if client is None:
        raise RuntimeError(
            "ORS_API_KEY não configurada — não é possível calcular rota real."
        )

    rota = client.directions(
        coordinates=[
            (p1[1], p1[0]),  # longitude, latitude
            (p2[1], p2[0])
        ],
        profile='driving-car'
    )

    distancia = rota['routes'][0]['summary']['distance']
    tempo = rota['routes'][0]['summary']['duration']

    return distancia, tempo