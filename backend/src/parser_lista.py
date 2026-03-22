import re
from collections import defaultdict


def processar_lista(texto, coordenadas):

    texto = texto.replace("*", "")
    for fac in coordenadas:
        texto = texto.replace(fac, f"\n{fac}")

    faculdade_atual = None 

    dados = defaultdict(lambda: {"ida":0,"volta":0,"total":0})  

    for linha in texto.split("\n"):
        linha = linha.strip().upper()

        if not linha:
            continue

        if re.match(r"\d+\s*[\.\)\-]?\s*\S+", linha) and faculdade_atual:
    
            nome_limpo = re.sub(r"\d+\s*[\.\)\-]?", "", linha).strip()

            if len(nome_limpo) < 2:
                continue

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