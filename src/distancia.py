import os
from dotenv import load_dotenv
import openrouteservice

load_dotenv()

api_key = os.getenv("ORS_API_KEY")

client = openrouteservice.Client(key=api_key)

def distancia_rota(p1, p2):

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