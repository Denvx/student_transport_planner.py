from src.coordenadas import coordenadas, origem
from src.distancia import distancia_rota
from src.parser_lista import processar_lista
from src.distribuicao import distribuir


texto = """
Lista de Transporte - 09/03 (segunda -feira) 

✔ TODOS devem colocar os nomes até às 12h;
✔ Se o professor cancelar a aula, não há prejuízo em retirar o nome da lista;

É só uma questão de organização. Obrigado pela colaboração!

UNEF
1. Edmille (volta)
2. Kamilly (volta)
10. marina
11. Maine
10. marina
11. Maine
12. ⁠Cássia - volta
13. Mariana
12. ⁠Cássia - volta
13. Mariana
14. Amanda 
15. ⁠kemilly
8. ⁠Maria Clara 
9. Gustavo Tavares 
10. marina
11. Maine
12. ⁠Cássia - volta
13. Mariana
14. Amanda 
15. ⁠kemilly

UNIFAN
1. Gabriel
2. Laura (Passageiro - Ida)
3. ⁠Letícia 
4. ⁠Isabela 
5. ⁠Maria Beatriz 
6. ⁠Duda
7. Danielle 
8. ⁠Fernanda Brito 
9. ⁠Giselle 
10. ⁠Isabelli 
11. ⁠Clara 
12. ⁠João
13. ⁠Yuri 
14. Ellen
15. ⁠Bruna 
16. ⁠Andressa
17. ⁠Alisson 
18. jaci
19. ⁠Luiz Henrique (volta)
20. ⁠Hellen 
8. ⁠Maria Clara 
9. Gustavo Tavares
14. Amanda 
15. ⁠kemilly
8. ⁠Maria Clara 
9. Gustavo Tavares 
10. marina
11. Maine
12. ⁠Cássia - volta
13. Mariana
14. Amanda 
15. ⁠kemilly

UEFS
1. Gabriel
2. ⁠Larissa
3. Ícaro (ida)
4. ⁠Victor
5. Luan
6. Tiago 
7. ⁠Julia
8. ⁠Kaylanne 
8. ⁠Maria Clara 
9. Gustavo Tavares 
10. marina
11. Maine
12. ⁠Cássia - volta
13. Mariana
14. Amanda 
15. ⁠kemilly
8. ⁠Maria Clara 
9. Gustavo Tavares 
10. marina
11. Maine
12. ⁠Cássia - volta
13. Mariana
14. Amanda 
15. ⁠kemilly
9. ⁠Lavínya 
10. Samuel 
11. ⁠André 
12. ⁠Léo (volta)
13. Sérgio 

SENAI
1. Trindade
2. Yasmin 
3. ⁠Guilherme 
8. ⁠Maria Clara 
9. Gustavo Tavares 
10. marina
11. Maine
12. ⁠Cássia - volta
13. Mariana
14. Amanda 
15. ⁠kemilly
8. ⁠Maria Clara 
9. Gustavo Tavares 
10. marina
11. Maine
12. ⁠Cássia - volta
13. Mariana
14. Amanda 
15. ⁠kemilly
4. Denver

QUADRIVIUM
1. 
8. ⁠Maria Clara 
9. Gustavo Tavares 
10. marina
11. Maine
12. ⁠Cássia - volta
13. Mariana
14. Amanda 
15. ⁠kemilly
8. ⁠Maria Clara 
9. Gustavo Tavares 
10. marina
11. Maine
12. ⁠Cássia - volta
13. Mariana
14. Amanda 
15. ⁠kemilly

INSTITUTO MIX
1. 
9. Gustavo Tavares 
10. marina
11. Maine
12. ⁠Cássia - volta
13. Mariana
14. Amanda 
15. ⁠kemilly

UNIRB 
1.
9. Gustavo Tavares 
10. marina
11. Maine
12. ⁠Cássia - volta
13. Mariana
14. Amanda 
15. ⁠kemilly
9. Gustavo Tavares 
10. marina
11. Maine
12. ⁠Cássia - volta
13. Mariana
14. Amanda 
15. ⁠kemilly

IFBA 
1. Lucas
9. Gustavo Tavares 
10. marina
11. Maine
12. ⁠Cássia - volta
13. Mariana
14. Amanda 
15. ⁠kemilly
"""  
# Texto bruto da lista de transporte (substitua pelo conteúdo real)


dados = processar_lista(texto, coordenadas)

faculdades_ordenadas = sorted(
    dados.items(),
    key=lambda x: distancia_rota(origem, coordenadas.get(x[0], origem))[0]  # Ordena faculdades pela distância da origem
)


veiculos = distribuir(faculdades_ordenadas)


print("\n===== DISTRIBUIÇÃO DOS VEÍCULOS =====") 

for v in veiculos:  # Para cada veículo, imprime ocupação e faculdades alocadas
    print(f"\n{v['nome']} ({v['ocupado']}/{v['capacidade']})")

    for fac, info in v["faculdades"]:
        print(f" - {fac} | Ida:{info['ida']} | Volta:{info['volta']} | Total:{info['total']}")