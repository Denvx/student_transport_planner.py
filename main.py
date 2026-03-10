from coordenadas import coordenadas, origem
from distancia import distancia
from parser_lista import processar_lista
from distribuicao import distribuir


texto = """
COLE AQUI SUA LISTA
"""  
# Texto bruto da lista de transporte (substitua pelo conteúdo real)


dados = processar_lista(texto, coordenadas)  # Processa o texto e extrai dados das faculdades

faculdades_ordenadas = sorted(
    dados.items(),
    key=lambda x: distancia(origem, coordenadas.get(x[0], origem))  # Ordena faculdades pela distância da origem
)


veiculos = distribuir(faculdades_ordenadas)  # Distribui faculdades nos veículos


print("\n===== DISTRIBUIÇÃO DOS VEÍCULOS =====") 

for v in veiculos:  # Para cada veículo, imprime ocupação e faculdades alocadas
    print(f"\n{v['nome']} ({v['ocupado']}/{v['capacidade']})")

    for fac, info in v["faculdades"]:
        print(f" - {fac} | Ida:{info['ida']} | Volta:{info['volta']} | Total:{info['total']}")