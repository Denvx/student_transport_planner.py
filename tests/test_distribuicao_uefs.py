import pytest
from src.distribuicao import distribuir


class TestDivisaoUefs:
    """
    UEFS não é bloco atômico como as demais faculdades — é usada pra
    completar a capacidade dos ônibus depois que o resto da demanda já foi
    alocado (confirmado com a responsável pela operação: é a mais fácil de
    servir com mais de um ônibus sem atrasar a chegada nas outras).
    """

    def test_uefs_completa_capacidade_de_um_onibus_so(self):
        faculdades = [
            ("UNEX", {"ida": 34, "volta": 36, "total": 36}),
            ("UNIFACS", {"ida": 8, "volta": 8, "total": 8}),
            ("UEFS", {"ida": 6, "volta": 6, "total": 6}),
        ]
        veiculos = distribuir(faculdades, veiculos_config=[
            {"nome": "Ônibus 1", "capacidade": 50},
        ])

        onibus1 = veiculos[0]
        assert onibus1["ocupado"] == 50

        uefs_chunks = [f for f in onibus1["faculdades"] if f[0] == "UEFS"]
        assert len(uefs_chunks) == 1
        assert uefs_chunks[0][1] == {"ida": 6, "volta": 6, "total": 6}

    def test_uefs_parcialmente_sem_vaga_nao_infla_ida_volta_do_pedaco_alocado(self):
        """
        Regressão: quando sobra gente da UEFS sem vaga em lugar nenhum, o
        pedaço que FOI alocado não pode "herdar" o ida/volta da parte que
        não coube (isso inflaria ida/volta além do total daquele pedaço).
        """
        faculdades = [
            ("UNEX", {"ida": 36, "volta": 36, "total": 36}),
            ("UNIFACS", {"ida": 8, "volta": 8, "total": 8}),
            ("UEFS", {"ida": 14, "volta": 13, "total": 16}),
        ]
        veiculos = distribuir(faculdades, veiculos_config=[
            {"nome": "Ônibus 1", "capacidade": 50},
        ])

        onibus1 = veiculos[0]
        assert onibus1["ocupado"] == 50

        uefs_chunks = [f for f in onibus1["faculdades"] if f[0] == "UEFS"]
        assert len(uefs_chunks) == 1
        ida, volta, total = uefs_chunks[0][1]["ida"], uefs_chunks[0][1]["volta"], uefs_chunks[0][1]["total"]
        assert total == 6
        assert ida <= total
        assert volta <= total

    def test_uefs_dividida_entre_dois_onibus(self):
        faculdades = [
            ("UNEX", {"ida": 34, "volta": 36, "total": 36}),
            ("UNIFAN", {"ida": 19, "volta": 19, "total": 19}),
            ("UNIFACS", {"ida": 8, "volta": 8, "total": 8}),
            ("QUADRIVIUM", {"ida": 5, "volta": 5, "total": 5}),
            ("UEFS", {"ida": 14, "volta": 13, "total": 16}),
        ]
        veiculos = distribuir(faculdades, veiculos_config=[
            {"nome": "Ônibus 1", "capacidade": 50},
            {"nome": "Ônibus 2", "capacidade": 50},
        ])

        onibus1, onibus2 = veiculos[0], veiculos[1]

        # UEFS aparece nos dois ônibus (dividida), nunca sobra ninguém sem vaga
        uefs_total_distribuido = sum(
            info["total"] for v in veiculos for fac, info in v["faculdades"] if fac == "UEFS"
        )
        assert uefs_total_distribuido == 16

        # Cada ônibus foi preenchido até a capacidade máxima com a sobra da UEFS
        assert onibus1["ocupado"] == 50
        assert onibus2["ocupado"] == 34

        # ida/volta de cada pedaço somam exatamente a demanda original da UEFS
        ida_total = sum(info["ida"] for v in veiculos for fac, info in v["faculdades"] if fac == "UEFS")
        volta_total = sum(info["volta"] for v in veiculos for fac, info in v["faculdades"] if fac == "UEFS")
        assert ida_total == 14
        assert volta_total == 13

    def test_uefs_extrapola_para_van_quando_onibus_ja_estao_cheios(self):
        faculdades = [
            ("UNEX", {"ida": 50, "volta": 50, "total": 50}),
            ("UEFS", {"ida": 10, "volta": 10, "total": 10}),
        ]
        veiculos = distribuir(faculdades, veiculos_config=[
            {"nome": "Ônibus 1", "capacidade": 50},
            {"nome": "Van 1", "capacidade": 20},
        ])

        onibus1 = veiculos[0]
        van1 = veiculos[1]

        assert onibus1["ocupado"] == 50
        assert not any(f[0] == "UEFS" for f in onibus1["faculdades"])

        uefs_chunks = [f for f in van1["faculdades"] if f[0] == "UEFS"]
        assert len(uefs_chunks) == 1
        assert uefs_chunks[0][1] == {"ida": 10, "volta": 10, "total": 10}

    def test_uefs_sem_frota_suficiente_nao_e_alocada_por_completo(self):
        """
        Sem espaço nenhum, a sobra da UEFS simplesmente não é colocada em
        lugar nenhum — quem chama (api.py) é responsável por comparar o
        total alocado contra a demanda original e avisar o admin.
        """
        faculdades = [
            ("UNEX", {"ida": 20, "volta": 20, "total": 20}),
            ("UEFS", {"ida": 10, "volta": 10, "total": 10}),
        ]
        veiculos = distribuir(faculdades, veiculos_config=[
            {"nome": "Van 1", "capacidade": 20},
        ])

        van1 = veiculos[0]
        assert van1["ocupado"] == 20

        uefs_alocada = sum(info["total"] for fac, info in van1["faculdades"] if fac == "UEFS")
        assert uefs_alocada == 0

    def test_sem_uefs_na_demanda_nao_faz_nada(self):
        faculdades = [("SENAI", {"ida": 10, "volta": 10, "total": 10})]
        veiculos = distribuir(faculdades, veiculos_config=[{"nome": "Van 1", "capacidade": 20}])

        assert veiculos[0]["ocupado"] == 10
        assert not any(f[0] == "UEFS" for f in veiculos[0]["faculdades"])
