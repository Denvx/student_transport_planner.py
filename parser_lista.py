import re
from collections import defaultdict


def processar_lista(texto, coordenadas):

    for fac in coordenadas.keys():
        texto = texto.replace(fac, f"\n{fac}")

    faculdade_atual = None 

    dados = defaultdict(lambda: {"ida":0,"volta":0,"total":0})  

    for linha in texto.split("\n"):
        linha = linha.strip()

        if not linha:
            continue

        if linha.isupper() and len(linha) < 30:
            faculdade_atual = linha  # Identifica o nome da faculdade (em maiúsculo)
            continue

        if re.match(r"\d+\.", linha) and faculdade_atual:
            linha_lower = linha.lower()

            ida = False
            volta = False

            if "ida" in linha_lower:
                ida = True

            if "volta" in linha_lower:
                volta = True

            if not ida and not volta:
                ida = True
                volta = True

            if ida:
                dados[faculdade_atual]["ida"] += 1

            if volta:
                dados[faculdade_atual]["volta"] += 1

            dados[faculdade_atual]["total"] += 1

    return dados