"""POST /planejar de ponta a ponta (sem rede: rota cai em linha reta, sinalizada)."""
import pytest

import api
from test_parser_formato_real import LISTA


@pytest.fixture
def client(monkeypatch):
    def sem_rede(*_a, **_k):
        raise RuntimeError("sem rede no teste")
    monkeypatch.setattr(api, "distancia_rota", sem_rede)
    return api.app.test_client()


def planejar(client, lista, veiculos):
    return client.post("/planejar", json={"lista": lista, "veiculos": veiculos})


def test_lista_real_distribui_todos_os_alunos(client):
    r = planejar(client, LISTA, [{"nome": "Ônibus 1", "capacidade": 50}])
    body = r.get_json()
    assert r.status_code == 200
    assert body["critical"] is False
    s = body["suggestion"]
    assert s["totais"]["alunos"] == 18
    assert sum(v["ocupado"] for v in s["veiculos"]) == 18
    assert s["sem_veiculo"] == []
    assert body["lista"]["data"] == "09/11/26"


def test_rota_estimada_vira_aviso_unico_por_faculdade(client):
    body = planejar(client, LISTA, [{"nome": "Ônibus 1", "capacidade": 50}]).get_json()
    avisos = [w for w in body["warnings"] if w.startswith("Distância até UNEF")]
    assert len(avisos) == 1
    assert body["status"] == "WARNING"


def test_regra_unifan_quadrivium_juntas(client):
    body = planejar(client, LISTA, [
        {"nome": "Ônibus 1", "capacidade": 50},
        {"nome": "Van 1", "capacidade": 15},
    ]).get_json()
    def veiculos_com(fac):
        return {v["nome"] for v in body["suggestion"]["veiculos"]
                if any(f["nome"] == fac for f in v["faculdades"])}
    assert veiculos_com("QUADRIVIUM")
    assert veiculos_com("QUADRIVIUM") == veiculos_com("UNIFAN")


def test_unex_e_unef_sem_espaco_para_separar_e_critico(client):
    lista = "UNEX\n1. Ana\n2. Bia\n\nUNEF\n1. Caio\n2. Davi"
    body = planejar(client, lista, [{"nome": "Van 1", "capacidade": 15}]).get_json()
    assert body["status"] == "CRITICAL"
    assert body["suggestion"] is None
    assert body["warnings"]


def test_faculdade_desconhecida_aparece_nos_avisos(client):
    lista = "UNEF\n1. Ana\n\nFACULDADE NOVA\n1. Bia"
    body = planejar(client, lista, [{"nome": "Ônibus 1", "capacidade": 50}]).get_json()
    assert any("FACULDADE NOVA" in w for w in body["warnings"])
    assert body["suggestion"]["totais"]["alunos"] == 1


def test_validacoes_de_entrada(client):
    assert planejar(client, "", [{"nome": "Ônibus 1", "capacidade": 50}]).status_code == 400
    assert planejar(client, "UNEF\n1. Ana", []).status_code == 400
    assert planejar(client, "texto sem faculdade", [{"nome": "Ônibus 1", "capacidade": 50}]).status_code == 422


# ── ajuste manual (/validar-ajuste) ─────────────────────────────

FROTA = [{"nome": "Ônibus 1", "capacidade": 50}, {"nome": "Van 1", "capacidade": 15},
         {"nome": "Van 2", "capacidade": 15}]


def validar(client, lista, veiculos):
    return client.post("/validar-ajuste", json={"lista": lista, "veiculos": veiculos})


def test_sugestao_devolve_todos_os_veiculos_mesmo_vazios(client):
    s = planejar(client, LISTA, FROTA).get_json()["suggestion"]
    assert [v["nome"] for v in s["veiculos"]] == ["Ônibus 1", "Van 1", "Van 2"]


def test_sugestao_do_motor_passa_na_validacao_do_ajuste(client):
    s = planejar(client, LISTA, FROTA).get_json()["suggestion"]
    r = validar(client, LISTA, s["veiculos"]).get_json()
    assert r == {"valido": True, "erros": []}


def test_mover_faculdade_para_veiculo_vazio_continua_valido(client):
    s = planejar(client, LISTA, FROTA).get_json()["suggestion"]
    veiculos = s["veiculos"]
    origem = next(v for v in veiculos if any(f["nome"] == "UEFS" for f in v["faculdades"]))
    destino = next(v for v in veiculos if not v["faculdades"])
    uefs = [f for f in origem["faculdades"] if f["nome"] == "UEFS"]
    origem["faculdades"] = [f for f in origem["faculdades"] if f["nome"] != "UEFS"]
    destino["faculdades"] = uefs
    r = validar(client, LISTA, veiculos).get_json()
    assert r["valido"], r["erros"]


def test_ajuste_com_aluno_inventado_e_recusado(client):
    s = planejar(client, LISTA, FROTA).get_json()["suggestion"]
    s["veiculos"][0]["faculdades"][0]["total"] += 1
    r = validar(client, LISTA, s["veiculos"]).get_json()
    assert r["valido"] is False and r["erros"]


def test_sobra_parcial_da_uefs_tem_ida_e_volta(client):
    lista = "UEFS\n" + "\n".join(f"{i}. Aluno {i}" for i in range(1, 21)) + "\n21. Ana (ida)"
    s = planejar(client, lista, [{"nome": "Ônibus 1", "capacidade": 15}]).get_json()["suggestion"]
    sobra = next(f for f in s["sem_veiculo"] if f["nome"] == "UEFS")
    assert sobra["total"] == 6
    assert sobra["ida"] is not None and sobra["volta"] is not None
    alocado = sum(f["volta"] for v in s["veiculos"] for f in v["faculdades"])
    assert alocado + sobra["volta"] == 20


def test_validar_ajuste_entrada_invalida(client):
    assert validar(client, "", FROTA).status_code == 400
    assert validar(client, LISTA, []).status_code == 400
