"""
Validação do ajuste manual (mesmo papel do validarAjuste do sistema da AERJ):
o servidor nunca confia na distribuição montada no navegador.
"""
from src.validacao_ajuste import validar

DEMANDA = {
    "UNEF": {"ida": 8, "volta": 10, "total": 10},
    "IFBA": {"ida": 2, "volta": 2, "total": 2},
    "UNIFAN": {"ida": 20, "volta": 20, "total": 20},
    "QUADRIVIUM": {"ida": 5, "volta": 5, "total": 5},
    "UEFS": {"ida": 30, "volta": 30, "total": 30},
}


def fac(nome, total=None, ida=None, volta=None):
    d = DEMANDA[nome]
    return {"nome": nome, "ida": d["ida"] if ida is None else ida,
            "volta": d["volta"] if volta is None else volta,
            "total": d["total"] if total is None else total}


def ajuste_valido():
    return [
        {"nome": "Ônibus 1", "capacidade": 50, "faculdades": [fac("UNIFAN"), fac("QUADRIVIUM"), fac("UEFS", 25, 25, 25)]},
        {"nome": "Van 1", "capacidade": 15, "faculdades": [fac("UNEF"), fac("IFBA")]},
        {"nome": "Van 2", "capacidade": 15, "faculdades": [fac("UEFS", 5, 5, 5)]},
    ]


def test_ajuste_valido():
    r = validar(ajuste_valido(), DEMANDA)
    assert r["valido"] is True, r["erros"]
    assert r["erros"] == []


def test_excede_capacidade():
    v = ajuste_valido()
    v[1]["faculdades"].append(v[2]["faculdades"].pop())  # Van 1 fica com 17/15
    r = validar(v, DEMANDA)
    assert not r["valido"]
    assert any("Van 1" in e and "capacidade" in e for e in r["erros"])


def test_aluno_faltando():
    v = ajuste_valido()
    v[2]["faculdades"] = []  # 5 da UEFS somem
    r = validar(v, DEMANDA)
    assert not r["valido"]
    assert any("UEFS" in e and "5" in e for e in r["erros"])


def test_aluno_a_mais_ou_faculdade_de_fora():
    v = ajuste_valido()
    v[2]["faculdades"].append({"nome": "UNEX", "ida": 1, "volta": 1, "total": 1})
    r = validar(v, DEMANDA)
    assert not r["valido"]
    assert any("UNEX" in e for e in r["erros"])


def test_ida_volta_adulterado():
    v = ajuste_valido()
    v[0]["faculdades"][0]["ida"] = 0
    r = validar(v, DEMANDA)
    assert not r["valido"]


def test_unex_e_unef_juntas():
    demanda = {**DEMANDA, "UNEX": {"ida": 1, "volta": 1, "total": 1}}
    v = ajuste_valido()
    v[1]["capacidade"] = 20
    v[1]["faculdades"].append({"nome": "UNEX", "ida": 1, "volta": 1, "total": 1})
    r = validar(v, demanda)
    assert not r["valido"]
    assert any("UNEX" in e and "UNEF" in e for e in r["erros"])


def test_unifan_e_quadrivium_separadas():
    v = ajuste_valido()
    v[2]["capacidade"] = 50
    v[2]["faculdades"].append(v[0]["faculdades"].pop(1))  # QUADRIVIUM vai pra Van 2
    r = validar(v, DEMANDA)
    assert not r["valido"]
    assert any("UNIFAN" in e and "QUADRIVIUM" in e for e in r["erros"])


def test_ifba_e_unef_separadas():
    v = ajuste_valido()
    v[2]["faculdades"].append(v[1]["faculdades"].pop())  # IFBA vai pra Van 2
    r = validar(v, DEMANDA)
    assert not r["valido"]
    assert any("IFBA" in e and "UNEF" in e for e in r["erros"])


def test_faculdade_dividida_em_dois_veiculos_e_permitida_se_somar_certo():
    # UEFS em 2 veículos (25 + 5) já está no ajuste válido
    assert validar(ajuste_valido(), DEMANDA)["valido"]


def test_veiculo_repetido():
    v = ajuste_valido()
    v[2]["nome"] = "Van 1"
    r = validar(v, DEMANDA)
    assert not r["valido"]
    assert any("mais de uma vez" in e for e in r["erros"])


def test_valores_invalidos_nao_quebram():
    v = ajuste_valido()
    v[0]["faculdades"][0]["total"] = "abc"
    r = validar(v, DEMANDA)
    assert not r["valido"]
