"""
Validação do ajuste manual da distribuição — mesmo papel do `validarAjuste`
do sistema da AERJ: o navegador monta o ajuste, mas o servidor revalida
tudo antes de aceitar, sem confiar no que veio do cliente.

  - nenhum veículo repetido, nenhum acima da capacidade;
  - todos os alunos da lista em algum veículo, sem sobra e sem aluno a mais
    (conferido contra a demanda lida da própria lista, por faculdade e por
    ida/volta);
  - regras obrigatórias (as mesmas de `regras_obrigatorias`):
      UNEX e UNEF em veículos diferentes;
      UNIFAN e QUADRIVIUM no mesmo veículo;
      IFBA e UNEF no mesmo veículo.

Uma faculdade pode aparecer em mais de um veículo (ex.: UEFS dividida),
desde que a soma bata com a lista. Para as faculdades das regras de
agrupamento, "no mesmo veículo" significa: cada uma inteira num veículo só,
e o mesmo veículo para as duas.
"""
from src.regras_obrigatorias import UNEX, UNEF, UNIFAN, QUADRIVIUM, IFBA

SEPARAR = [(UNEX, UNEF)]
JUNTAR = [(UNIFAN, QUADRIVIUM), (IFBA, UNEF)]


def _inteiro(valor):
    if isinstance(valor, bool):
        raise ValueError
    n = int(valor)
    if n < 0:
        raise ValueError
    return n


def _fmt(nome):
    return nome.replace("_", " ")


def validar(veiculos, demanda):
    """
    veiculos: [{"nome", "capacidade", "faculdades": [{"nome", "ida", "volta", "total"}]}]
    demanda:  {faculdade: {"ida", "volta", "total"}} — lida da lista no servidor
    Retorna {"valido": bool, "erros": [str]}.
    """
    erros = []
    alocado = {}            # faculdade -> {"ida", "volta", "total"}
    veiculos_por_fac = {}   # faculdade -> {nome do veículo}
    nomes_vistos = set()

    for v in veiculos or []:
        nome = str(v.get("nome") or "").strip() or "(sem nome)"
        if nome in nomes_vistos:
            erros.append(f"O veículo “{nome}” aparece mais de uma vez.")
        nomes_vistos.add(nome)

        try:
            capacidade = _inteiro(v.get("capacidade"))
        except (TypeError, ValueError):
            erros.append(f"Capacidade inválida no veículo “{nome}”.")
            continue

        ocupado = 0
        for f in v.get("faculdades") or []:
            fac = str(f.get("nome") or "").strip().upper()
            try:
                ida, volta, total = (_inteiro(f.get(k)) for k in ("ida", "volta", "total"))
            except (TypeError, ValueError):
                erros.append(f"Quantidade inválida para {_fmt(fac) or '(sem nome)'} no veículo “{nome}”.")
                continue
            if total == 0:
                continue
            ocupado += total
            a = alocado.setdefault(fac, {"ida": 0, "volta": 0, "total": 0})
            a["ida"] += ida
            a["volta"] += volta
            a["total"] += total
            veiculos_por_fac.setdefault(fac, set()).add(nome)

        if ocupado > capacidade:
            erros.append(
                f"“{nome}” excede a capacidade: {ocupado} alunos para {capacidade} lugares."
            )

    # Todos os alunos da lista, nem mais nem menos
    for fac in sorted(set(demanda) | set(alocado)):
        d = demanda.get(fac)
        a = alocado.get(fac, {"ida": 0, "volta": 0, "total": 0})
        if d is None:
            erros.append(f"{_fmt(fac)} não está na lista ({a['total']} aluno(s) a mais).")
            continue
        if a["total"] < d["total"]:
            erros.append(f"{d['total'] - a['total']} aluno(s) de {_fmt(fac)} sem veículo.")
        elif a["total"] > d["total"]:
            erros.append(f"{_fmt(fac)} tem {a['total'] - d['total']} aluno(s) a mais que a lista.")
        elif a["ida"] != d["ida"] or a["volta"] != d["volta"]:
            erros.append(f"Ida/volta de {_fmt(fac)} não confere com a lista.")

    for a, b in SEPARAR:
        juntos = veiculos_por_fac.get(a, set()) & veiculos_por_fac.get(b, set())
        if juntos:
            erros.append(f"{a} e {b} precisam ficar em veículos diferentes (juntas em: {', '.join(sorted(juntos))}).")

    for a, b in JUNTAR:
        va, vb = veiculos_por_fac.get(a), veiculos_por_fac.get(b)
        if not va or not vb:
            continue
        if len(va) != 1 or va != vb:
            erros.append(f"{_fmt(a)} e {_fmt(b)} precisam ficar juntas, inteiras, no mesmo veículo.")

    return {"valido": not erros, "erros": erros}
