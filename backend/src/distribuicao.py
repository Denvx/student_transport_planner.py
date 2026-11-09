VAN_CAP = 25

NOME_UEFS = "UEFS"
NOME_IFBA = "IFBA"
NOME_UNEF = "UNEF"


def _localizar_grupo(grupos, nome):
    """Índice de `nome` em `grupos` (lista de tuplas (fac, info)), ou None."""
    for i, (fac, _info) in enumerate(grupos):
        if fac == nome:
            return i
    return None


def _tentar_juntos_em_van(vans, grupos, nome_a, nome_b):
    """
    Prioridade de van pra IFBA e UNEF (confirmado com a responsável pela
    operação: são as faculdades mais distantes do centro, e sempre que der
    pra completar a van com as duas, prioriza van em vez de ônibus). Só age
    se AMBAS existirem na demanda do dia e couberem juntas em alguma van —
    se não couber, não faz nada aqui: o resto do pipeline aloca normalmente
    e a regra obrigatória de agrupamento (`regras_obrigatorias.py`) garante
    que elas fiquem juntas de qualquer jeito, mesmo que seja num ônibus.
    """
    idx_a = _localizar_grupo(grupos, nome_a)
    idx_b = _localizar_grupo(grupos, nome_b)
    if idx_a is None or idx_b is None:
        return

    fac_a, info_a = grupos[idx_a]
    fac_b, info_b = grupos[idx_b]
    total_combinado = info_a["total"] + info_b["total"]

    candidatas = [v for v in vans if (v["capacidade"] - v["ocupado"]) >= total_combinado]
    if not candidatas:
        return

    destino = min(candidatas, key=lambda v: v["capacidade"] - v["ocupado"])
    destino["faculdades"].append((fac_a, info_a))
    destino["faculdades"].append((fac_b, info_b))
    destino["ocupado"] += total_combinado

    for idx in sorted((idx_a, idx_b), reverse=True):
        grupos.pop(idx)


def _dividir_uefs_entre_onibus(onibus, vans, info_uefs):
    """
    UEFS não é tratada como bloco atômico como as demais faculdades — é a
    faculdade usada pra completar a capacidade dos veículos quando o resto
    da demanda não enche exatamente (confirmado com a responsável pela
    operação: UEFS é a mais fácil de servir com mais de um ônibus, sem
    atrasar a chegada nas demais faculdades da rota). Enche cada ônibus até
    a capacidade máxima, na ordem da frota; sobra vai pra vans no mesmo
    critério. Se ainda sobrar gente da UEFS depois disso, a frota não tem
    capacidade suficiente pro dia — quem chama é responsável por comparar
    o total alocado contra a demanda original e avisar o admin.

    ida/volta de cada pedaço são proporcionais ao tamanho do pedaço em
    relação ao total original (arredondado; a sobra do arredondamento vai
    pro último pedaço, pra garantir que a soma bata exatamente com a
    demanda original).
    """
    total_restante = info_uefs["total"]
    if total_restante <= 0:
        return

    pedacos = []
    for pool in (onibus, vans):
        for v in pool:
            if total_restante <= 0:
                break
            espaco = v["capacidade"] - v["ocupado"]
            if espaco <= 0:
                continue
            pedaco = min(espaco, total_restante)
            pedacos.append((v, pedaco))
            v["ocupado"] += pedaco
            total_restante -= pedaco
        if total_restante <= 0:
            break

    # Se sobrou gente da UEFS sem vaga (total_restante > 0), o "último pedaço
    # colocado" NÃO é o último pedaço real da divisão — tem uma fatia
    # invisível (a que não coube) depois dele. Nesse caso não dá pra jogar
    # a sobra do arredondamento nele (inflaria ida/volta além do total do
    # pedaço) — cada pedaço usa proporção simples, e a fatia que não coube
    # simplesmente não é contabilizada em lugar nenhum.
    tudo_alocado = total_restante <= 0
    total_original = info_uefs["total"]
    ida_acumulado = volta_acumulado = 0
    for i, (v, pedaco) in enumerate(pedacos):
        ultimo = tudo_alocado and i == len(pedacos) - 1
        if ultimo:
            ida_pedaco = info_uefs["ida"] - ida_acumulado
            volta_pedaco = info_uefs["volta"] - volta_acumulado
        else:
            ida_pedaco = round(info_uefs["ida"] * pedaco / total_original)
            volta_pedaco = round(info_uefs["volta"] * pedaco / total_original)
        ida_acumulado += ida_pedaco
        volta_acumulado += volta_pedaco

        v["faculdades"].append((NOME_UEFS, {"ida": ida_pedaco, "volta": volta_pedaco, "total": pedaco}))


def distribuir(faculdades_ordenadas, veiculos_config=None):
    """
    Estratégia:
    0. IFBA + UNEF: tenta juntar as duas numa única van, se couberem juntas
       (prioridade de van — ver `_tentar_juntos_em_van`). Se não, seguem o
       fluxo normal abaixo como blocos atômicos separados.
    1. Grandes (nao cabem em van) → ônibus, first-fit decreasing.
    2. Pequenos → tenta completar ônibus que já tem gente (best-fit),
       aproveitando espaço ocioso.
    3. Pequenos que ainda sobraram → vans (best-fit).
    4. Fallback: qualquer veiculo com espaço.
    5. UEFS: não passa pelos passos acima — é usada pra completar a
       capacidade que sobrou nos veículos depois de tudo (ver
       `_dividir_uefs_entre_onibus`).

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

    vans   = [v for v in veiculos if v["capacidade"] <= VAN_CAP]
    onibus = [v for v in veiculos if v["capacidade"] >  VAN_CAP]
    cap_van_max = max((v["capacidade"] for v in vans), default=0)

    ordem = {fac: i for i, (fac, _info) in enumerate(faculdades_ordenadas)}

    grupos = list(faculdades_ordenadas)

    _tentar_juntos_em_van(vans, grupos, NOME_IFBA, NOME_UNEF)

    idx_uefs = _localizar_grupo(grupos, NOME_UEFS)
    info_uefs = grupos.pop(idx_uefs)[1] if idx_uefs is not None else None

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

    if info_uefs is not None:
        _dividir_uefs_entre_onibus(onibus, vans, info_uefs)

    for v in veiculos:
        v["faculdades"].sort(key=lambda x: ordem.get(x[0], 9999))

    return veiculos
