import re
import unicodedata
from collections import defaultdict

# Faculdades que existem no sistema da AERJ mas ainda não têm coordenada em
# coordenadas.py: são contadas normalmente, só ficam sem distância (vão para o
# fim da ordem de rota e geram aviso).
SEM_COORDENADA = ("UFRB", "UNEB", "UNIFTC", "CATOLICA", "CEEP", "SENAC", "SEST_SENAT")

_INVISIVEIS = re.compile(r"[​‌‍⁠﻿\xa0]")
_NUMERADA = re.compile(r"\d+\s*[\.\)\-]?")
_DATA = re.compile(r"\b(\d{1,2}/\d{1,2}/\d{2,4})\b")


def _normalizar(texto):
    """'*Curso Aprovado*' -> 'CURSO APROVADO'; 'UFRB (FIAT)' -> 'UFRB'; tira acento."""
    texto = unicodedata.normalize("NFKD", _INVISIVEIS.sub("", texto))
    texto = "".join(c for c in texto if not unicodedata.combining(c)).upper()
    texto = re.sub(r"\(.*?\)", " ", texto)
    return re.sub(r"[^A-Z0-9]+", " ", texto).strip()


def _mapa_faculdades(coordenadas):
    nomes = list(coordenadas) + [f for f in SEM_COORDENADA if f not in coordenadas]
    return {_normalizar(f.replace("_", " ")): f for f in nomes}


def analisar_lista(texto, coordenadas):
    """
    Lê a lista do WhatsApp e devolve:
      dados          {faculdade: {"ida", "volta", "total"}}
      desconhecidas  [{"nome", "alunos"}] — cabeçalho seguido de nomes que não é
                     faculdade conhecida; os nomes são ignorados (nunca caem na
                     faculdade anterior)
      sem_coordenada faculdades contadas que não têm coordenada
      data           data do título ("09/11/26"), se houver
    """
    faculdades = _mapa_faculdades(coordenadas)
    linhas = [l.strip() for l in texto.replace("*", "").split("\n")]
    numerada = [bool(_NUMERADA.match(l)) for l in linhas]

    dados = defaultdict(lambda: {"ida": 0, "volta": 0, "total": 0})
    desconhecidas = []
    data = None
    faculdade_atual = None
    desconhecida_atual = None

    for i, linha in enumerate(linhas):
        if not linha:
            continue

        if not numerada[i]:
            chave = faculdades.get(_normalizar(linha))
            if chave:
                faculdade_atual, desconhecida_atual = chave, None
                continue
            proxima = next((j for j in range(i + 1, len(linhas)) if linhas[j]), None)
            if proxima is not None and numerada[proxima]:
                # Cabeçalho de faculdade que não conhecemos
                faculdade_atual = None
                desconhecida_atual = {"nome": _normalizar(linha), "alunos": 0}
                desconhecidas.append(desconhecida_atual)
            elif data is None and faculdade_atual is None:
                m = _DATA.search(linha)
                if m:
                    data = m.group(1)
            continue

        nome_limpo = re.sub(r"^\d+\s*[\.\)\-]?\s*", "", linha)
        nome_limpo = re.sub(r"\(.*?\)", "", nome_limpo)
        nome_limpo = _INVISIVEIS.sub("", nome_limpo).strip()
        if len(nome_limpo) < 2 or not re.search(r"[A-Za-zÀ-ÿ]", nome_limpo):
            continue

        if desconhecida_atual is not None:
            desconhecida_atual["alunos"] += 1
            continue
        if faculdade_atual is None:
            continue

        linha_lower = linha.lower()
        # \b garante palavra isolada — evita falso positivo em nomes que
        # contêm "ida"/"volta" como substring (ex.: sobrenome "Almeida").
        ida = bool(re.search(r"\bida\b", linha_lower))
        volta = bool(re.search(r"\bvolta\b", linha_lower))
        if not ida and not volta:
            ida = volta = True

        if ida:
            dados[faculdade_atual]["ida"] += 1
        if volta:
            dados[faculdade_atual]["volta"] += 1
        dados[faculdade_atual]["total"] += 1

    return {
        "dados": dados,
        "desconhecidas": [d for d in desconhecidas if d["alunos"] > 0],
        "sem_coordenada": sorted(f for f in dados if f not in coordenadas),
        "data": data,
    }


def processar_lista(texto, coordenadas):
    return analisar_lista(texto, coordenadas)["dados"]
