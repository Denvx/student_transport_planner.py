import os
from dotenv import load_dotenv
import openrouteservice

load_dotenv()

api_key = os.getenv("ORS_API_KEY")

client = openrouteservice.Client(key=api_key)

origem = (-11.810503167138526, -39.382493942430905)  # Riachão
destino = (-12.200186611506028, -38.97186855898357)  # UEFS

rota = client.directions(
    coordinates=[
        (origem[1], origem[0]),
        (destino[1], destino[0])
    ],
    profile='driving-car'
)

distancia = rota['routes'][0]['summary']['distance']
tempo = rota['routes'][0]['summary']['duration']

print("Distância:", distancia/1000, "km")
print("Tempo:", tempo/60, "minutos")