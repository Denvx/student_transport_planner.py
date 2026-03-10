def distribuir(faculdades_ordenadas):

    veiculos = [
        {"nome": "Ônibus 1", "capacidade": 50, "ocupado": 0, "faculdades": []},
        {"nome": "Ônibus 2", "capacidade": 50, "ocupado": 0, "faculdades": []},
        {"nome": "Van 1", "capacidade": 20, "ocupado": 0, "faculdades": []},
        {"nome": "Van 2", "capacidade": 15, "ocupado": 0, "faculdades": []}
    ]

    for fac, info in faculdades_ordenadas:  # Para cada faculdade ordenada por distância
        total = info["total"]  
        colocado = False  

        for v in veiculos:  
            if v["ocupado"] + total <= v["capacidade"]:  # Verifica se cabe no veículo
                v["faculdades"].append((fac, info))
                v["ocupado"] += total
                colocado = True
                break

        if not colocado:
            print(f"Não coube em nenhum veículo: {fac}")

    return veiculos