"""
Formato real da lista do WhatsApp (09/11/2026), com nomes fictícios:
título com data, avisos com emoji, faculdades vazias ("1."), cabeçalho com
apelido ("Curso Aprovado", "UFRB (FIAT)") e direção em vários formatos.
"""
from src.coordenadas import coordenadas
from src.parser_lista import analisar_lista, processar_lista

LISTA = """Lista de Transporte - 09/11/26 (segunda-feira)

✔️ TODOS devem colocar os nomes até às 12h;
✔️ Se o professor cancelar a aula, não há prejuízo em retirar o nome da lista;

É só uma questão de organização. Obrigado pela colaboração!

UFRB (FIAT)
1.

UNEF
1. Ana - volta
2. Bruno
3. Carla (volta)
4. Davi volta
5. Elisa ( volta)
6. Fábio

UNIFAN
1. Gael
2. Helena (ida)
3. Igor - volta
4. Joana(ida)
5. Lucas Almeida

UEFS
1. Marta (ida)
2. Nilo
3. Otávio - volta

SENAI
1.

QUADRIVIUM
  1. Paula
  2.  Rui

INSTITUTO MIX
1.

Curso Aprovado
1. sara
2. tiago
"""


def test_conta_por_faculdade_e_direcao():
    dados = processar_lista(LISTA, coordenadas)
    assert dict(dados["UNEF"]) == {"ida": 2, "volta": 6, "total": 6}
    assert dict(dados["UNIFAN"]) == {"ida": 4, "volta": 3, "total": 5}
    assert dict(dados["UEFS"]) == {"ida": 2, "volta": 2, "total": 3}
    assert dict(dados["QUADRIVIUM"]) == {"ida": 2, "volta": 2, "total": 2}


def test_curso_aprovado_reconhecido_e_nao_vira_a_faculdade_anterior():
    dados = processar_lista(LISTA, coordenadas)
    assert dict(dados["CURSO_APROVADO"]) == {"ida": 2, "volta": 2, "total": 2}
    assert "INSTITUTO MIX" not in dados


def test_faculdades_vazias_nao_aparecem():
    dados = processar_lista(LISTA, coordenadas)
    for vazia in ("UFRB", "SENAI", "INSTITUTO MIX"):
        assert vazia not in dados


def test_total_de_alunos():
    dados = processar_lista(LISTA, coordenadas)
    assert sum(i["total"] for i in dados.values()) == 18


def test_titulo_e_avisos_nao_geram_aviso_de_faculdade_desconhecida():
    r = analisar_lista(LISTA, coordenadas)
    assert r["desconhecidas"] == []
    assert r["data"] == "09/11/26"


def test_faculdade_desconhecida_e_ignorada_com_aviso():
    texto = "UNEF\n1. Ana\n\nFACULDADE NOVA\n1. Bia\n2. Caio\n\nUEFS\n1. Davi"
    r = analisar_lista(texto, coordenadas)
    assert r["desconhecidas"] == [{"nome": "FACULDADE NOVA", "alunos": 2}]
    # Os alunos da desconhecida não podem cair na faculdade anterior (UNEF)
    assert r["dados"]["UNEF"]["total"] == 1
    assert r["dados"]["UEFS"]["total"] == 1


def test_faculdade_conhecida_sem_coordenada_e_contada():
    texto = "UFRB (FIAT)\n1. Ana\n2. Bia (ida)"
    r = analisar_lista(texto, coordenadas)
    assert dict(r["dados"]["UFRB"]) == {"ida": 2, "volta": 1, "total": 2}
    assert r["sem_coordenada"] == ["UFRB"]


def test_estacio_com_e_sem_acento():
    for cab in ("ESTÁCIO", "Estacio", "estácio"):
        dados = processar_lista(f"{cab}\n1. Ana", coordenadas)
        assert dados["ESTACIO"]["total"] == 1, cab


def test_negrito_do_whatsapp_no_cabecalho():
    dados = processar_lista("*UNEF*\n1. Ana\n*Curso Aprovado*\n1. Bia", coordenadas)
    assert dados["UNEF"]["total"] == 1
    assert dados["CURSO_APROVADO"]["total"] == 1
