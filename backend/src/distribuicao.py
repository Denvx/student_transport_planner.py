def distribuir(faculdades_ordenadas, veiculos_config=None):
    """
    Estratégia:
    1. Grandes (nao cabem em van) → ônibus, first-fit decreasing.
    2. Pequenos → tenta completar ônibus que já tem gente (best-fit),
       aproveitando espaço ocioso.
    3. Pequenos que ainda sobraram → vans (best-fit).
    4. Fallback: qualquer veiculo com espaço.

    Ordem de distância preservada dentro de cada veículo no final.
    """

    if veiculos_config:
        veiculos = [
            {"nome": v["nome"], "capacidade": int(v["capacidade"]), "ocupado": 0, "faculdades": []}
            for v in veiculos_config
        ]
    else:
        veiculos = [
            {"nome": "Ônibus 1", "capacidade": 50, "ocupado": 0, "faculdades": []},
        ]

    VAN_CAP = 25
    vans   = [v for v in veiculos if v["capacidade"] <= VAN_CAP]
    onibus = [v for v in veiculos if v["capacidade"] >  VAN_CAP]
    cap_van_max = max((v["capacidade"] for v in vans), default=0)

    grupos = list(faculdades_ordenadas)
    grandes  = sorted([(f,i) for f,i in grupos if i["total"] > cap_van_max],  key=lambda x: x[1]["total"], reverse=True)
    pequenos = sorted([(f,i) for f,i in grupos if i["total"] <= cap_van_max], key=lambda x: x[1]["total"], reverse=True)

    def best_fit(fac, info, pool):
        """Coloca no veículo do pool com menor sobra que ainda cabe. Retorna True se alocou."""
        total = info["total"]
        melhor, menor_sobra = None, float("inf")
        for v in pool:
            sobra = v["capacidade"] - v["ocupado"] - total
            if 0 <= sobra < menor_sobra:
                menor_sobra = sobra
                melhor = v
        if melhor:
            melhor["faculdades"].append((fac, info))
            melhor["ocupado"] += total
            return True
        return False

    sobraram = []
    for fac, info in grandes:
        if not best_fit(fac, info, onibus):
            sobraram.append((fac, info))

    restantes = []
    for fac, info in pequenos:
        onibus_ocupados = [v for v in onibus if v["ocupado"] > 0]
        if onibus_ocupados and best_fit(fac, info, onibus_ocupados):
            continue

        if best_fit(fac, info, onibus):
            continue

        if best_fit(fac, info, vans):
            continue

        restantes.append((fac, info))

    for fac, info in sobraram:
        if not best_fit(fac, info, vans):
            restantes.append((fac, info))

    for fac, info in restantes:
        colocado = False
        for v in sorted(veiculos, key=lambda x: x["capacidade"] - x["ocupado"], reverse=True):
            if v["ocupado"] + info["total"] <= v["capacidade"]:
                v["faculdades"].append((fac, info))
                v["ocupado"] += info["total"]
                colocado = True
                break
        if not colocado:
            print(f"Nao coube: {fac} ({info['total']} alunos)")

    ordem = {fac: i for i, (fac, _) in enumerate(grupos)}
    for v in veiculos:
        v["faculdades"].sort(key=lambda x: ordem.get(x[0], 9999))

    return veiculos