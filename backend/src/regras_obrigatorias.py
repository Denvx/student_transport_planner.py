"""
Regras obrigatórias da operação (confirmadas com a responsável pelo
transporte da AERJ) — não são otimização, são restrições que a distribuição
final NUNCA pode violar:

  - UNEX e UNEF precisam ficar em veículos diferentes, sempre que houver
    mais de um transporte.
  - UNIFAN e QUADRIVIUM precisam ficar no mesmo veículo, sempre.
  - IFBA e UNEF precisam ficar no mesmo veículo, sempre — são as faculdades
    mais distantes do centro. `distribuicao.distribuir()` já tenta priorizar
    juntá-las numa van antes de rodar o bin-packing normal (ver
    `_tentar_juntos_em_van`); esta regra aqui é a garantia final, caso essa
    tentativa não tenha sido possível e o bin-packing normal as separe.

Este módulo roda DEPOIS de `distribuicao.distribuir()` (que continua
resolvendo o bin-packing por capacidade/tamanho normalmente) e só corrige o
resultado quando ele viola uma dessas regras — nunca decide a alocação do
zero. Se não houver como corrigir sem violar capacidade, a situação é
reportada como crítica: o motor nunca aprova uma distribuição que quebre
uma regra obrigatória, nem escolhe uma solução "quase certa" sozinho.
"""

UNEX = "UNEX"
UNEF = "UNEF"
UNIFAN = "UNIFAN"
QUADRIVIUM = "QUADRIVIUM"
IFBA = "IFBA"


def _localizar(veiculos, nome_faculdade):
    """Retorna (indice_veiculo, info) da faculdade, ou None se não estiver na distribuição."""
    for i, v in enumerate(veiculos):
        for fac, info in v["faculdades"]:
            if fac == nome_faculdade:
                return i, info
    return None


def _mover(veiculos, nome_faculdade, origem_idx, destino_idx):
    origem = veiculos[origem_idx]
    destino = veiculos[destino_idx]

    item = next((f for f in origem["faculdades"] if f[0] == nome_faculdade), None)
    if item is None:
        return False

    _, info = item
    origem["faculdades"] = [f for f in origem["faculdades"] if f[0] != nome_faculdade]
    origem["ocupado"] -= info["total"]

    destino["faculdades"].append(item)
    destino["ocupado"] += info["total"]
    return True


def _tentar_mover_para_outro(veiculos, nome_faculdade, origem_idx, excluir_idx=None):
    """Tenta mover a faculdade pra qualquer outro veículo com espaço suficiente.
    Retorna o índice de destino se conseguiu, ou None."""
    _, info = _localizar(veiculos, nome_faculdade)
    total = info["total"]

    candidatos = [
        i for i, v in enumerate(veiculos)
        if i != origem_idx and i != excluir_idx
        and (v["capacidade"] - v["ocupado"]) >= total
    ]
    if not candidatos:
        return None

    # Menor sobra que ainda cabe — mesmo critério best-fit já usado em distribuicao.py
    destino_idx = min(candidatos, key=lambda i: veiculos[i]["capacidade"] - veiculos[i]["ocupado"])
    _mover(veiculos, nome_faculdade, origem_idx, destino_idx)
    return destino_idx


def _resolver_separacao_obrigatoria(veiculos, nome_a, nome_b, warnings):
    """UNEX/UNEF: se ambos existirem e estiverem no mesmo veículo, separa."""
    loc_a = _localizar(veiculos, nome_a)
    loc_b = _localizar(veiculos, nome_b)

    if loc_a is None or loc_b is None:
        return None  # uma das duas nem está na lista do dia — nada a fazer

    idx_a, info_a = loc_a
    idx_b, info_b = loc_b

    if idx_a != idx_b:
        return None  # já estão separados

    # Move o menor grupo dos dois, pra minimizar impacto na rota já calculada
    menor, maior = (nome_a, nome_b) if info_a["total"] <= info_b["total"] else (nome_b, nome_a)
    origem_idx = idx_a

    destino_idx = _tentar_mover_para_outro(veiculos, menor, origem_idx)
    if destino_idx is not None:
        warnings.append(
            f"{menor} foi realocada para outro veículo para respeitar a separação "
            f"obrigatória entre {UNEX} e {UNEF}."
        )
        return None

    return (
        f"Não foi possível separar {UNEX} e {UNEF} com a frota informada — "
        f"{info_a['total']} aluno(s) de {nome_a} e {info_b['total']} de {nome_b} "
        f"precisariam do mesmo veículo."
    )


def _resolver_agrupamento_obrigatorio(veiculos, nome_a, nome_b, warnings):
    """Genérica: se ambos existirem e estiverem em veículos diferentes, junta (usada pra UNIFAN/QUADRIVIUM e IFBA/UNEF)."""
    loc_a = _localizar(veiculos, nome_a)
    loc_b = _localizar(veiculos, nome_b)

    if loc_a is None or loc_b is None:
        return None

    idx_a, info_a = loc_a
    idx_b, info_b = loc_b

    if idx_a == idx_b:
        return None  # já estão juntas

    # Tenta mover o menor grupo pro veículo do maior; se não couber, tenta o inverso
    menor, idx_menor, maior, idx_maior = (
        (nome_a, idx_a, nome_b, idx_b) if info_a["total"] <= info_b["total"]
        else (nome_b, idx_b, nome_a, idx_a)
    )

    if _mover_se_couber(veiculos, menor, idx_menor, idx_maior):
        warnings.append(
            f"{menor} foi realocada para o mesmo veículo de {maior} para respeitar "
            f"o agrupamento obrigatório entre {nome_a} e {nome_b}."
        )
        return None

    if _mover_se_couber(veiculos, maior, idx_maior, idx_menor):
        warnings.append(
            f"{maior} foi realocada para o mesmo veículo de {menor} para respeitar "
            f"o agrupamento obrigatório entre {nome_a} e {nome_b}."
        )
        return None

    return (
        f"Não foi possível manter {nome_a} e {nome_b} no mesmo veículo com a "
        f"frota informada — juntas somam {info_a['total'] + info_b['total']} "
        f"aluno(s), mais que a capacidade livre de qualquer veículo disponível."
    )


def _mover_se_couber(veiculos, nome_faculdade, origem_idx, destino_idx):
    _, info = _localizar(veiculos, nome_faculdade)
    destino = veiculos[destino_idx]
    if (destino["capacidade"] - destino["ocupado"]) >= info["total"]:
        _mover(veiculos, nome_faculdade, origem_idx, destino_idx)
        return True
    return False


def aplicar(veiculos):
    """
    Aplica as regras obrigatórias sobre o resultado de distribuir().

    Retorna dict:
      { "veiculos": [...], "warnings": [...], "critico": bool, "motivo_critico": str|None }
    """
    warnings = []

    motivo = _resolver_separacao_obrigatoria(veiculos, UNEX, UNEF, warnings)
    if motivo:
        return {"veiculos": veiculos, "warnings": warnings, "critico": True, "motivo_critico": motivo}

    motivo = _resolver_agrupamento_obrigatorio(veiculos, UNIFAN, QUADRIVIUM, warnings)
    if motivo:
        return {"veiculos": veiculos, "warnings": warnings, "critico": True, "motivo_critico": motivo}

    motivo = _resolver_agrupamento_obrigatorio(veiculos, IFBA, UNEF, warnings)
    if motivo:
        return {"veiculos": veiculos, "warnings": warnings, "critico": True, "motivo_critico": motivo}

    return {"veiculos": veiculos, "warnings": warnings, "critico": False, "motivo_critico": None}
