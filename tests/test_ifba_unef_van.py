import pytest
from src.distribuicao import distribuir
from src import regras_obrigatorias as ro


class TestPrioridadeVanIfbaUnef:
    """
    IFBA e UNEF são as faculdades mais distantes do centro — confirmado com
    a responsável pela operação: sempre juntas no mesmo veículo, e sempre
    que der pra completar uma van com as duas, prioriza van em vez de
    ônibus (ver `distribuicao._tentar_juntos_em_van`).
    """

    def test_ifba_e_unef_priorizam_van_quando_cabem_juntas(self):
        faculdades = [
            ("IFBA", {"ida": 1, "volta": 1, "total": 1}),
            ("UNEF", {"ida": 15, "volta": 16, "total": 16}),
        ]
        veiculos = distribuir(faculdades, veiculos_config=[
            {"nome": "Ônibus 1", "capacidade": 50},
            {"nome": "Van 1", "capacidade": 20},
        ])

        onibus1 = next(v for v in veiculos if v["nome"] == "Ônibus 1")
        van1 = next(v for v in veiculos if v["nome"] == "Van 1")

        assert onibus1["ocupado"] == 0
        nomes_van = {f[0] for f in van1["faculdades"]}
        assert nomes_van == {"IFBA", "UNEF"}
        assert van1["ocupado"] == 17

    def test_prioriza_a_van_com_menor_sobra_que_ainda_cabe(self):
        faculdades = [
            ("IFBA", {"ida": 1, "volta": 1, "total": 1}),
            ("UNEF", {"ida": 5, "volta": 5, "total": 5}),
        ]
        veiculos = distribuir(faculdades, veiculos_config=[
            {"nome": "Van 1", "capacidade": 20},
            {"nome": "Van 2", "capacidade": 6},
        ])

        van2 = next(v for v in veiculos if v["nome"] == "Van 2")
        van1 = next(v for v in veiculos if v["nome"] == "Van 1")

        assert van2["ocupado"] == 6  # 1 + 5, sobra exata
        assert van1["ocupado"] == 0

    def test_nao_junta_em_van_quando_nao_cabem_juntas_mas_nao_perde_ninguem(self):
        """Sem van com espaço pras duas juntas, cai no fluxo normal de
        bin-packing (a regra obrigatória de agrupamento garante que fiquem
        juntas depois — ver TestAgrupamentoObrigatorioIfbaUnef)."""
        faculdades = [
            ("IFBA", {"ida": 1, "volta": 1, "total": 1}),
            ("UNEF", {"ida": 16, "volta": 16, "total": 16}),
        ]
        veiculos = distribuir(faculdades, veiculos_config=[
            {"nome": "Ônibus 1", "capacidade": 50},
            {"nome": "Van 1", "capacidade": 10},
        ])

        assert sum(v["ocupado"] for v in veiculos) == 17

    def test_sem_ifba_nao_prioriza_van_pra_unef(self):
        """Só UNEF (sem IFBA) não deve disparar a prioridade de van — segue
        o bin-packing normal como qualquer outra faculdade pequena."""
        faculdades = [
            ("UNEF", {"ida": 16, "volta": 16, "total": 16}),
        ]
        veiculos = distribuir(faculdades, veiculos_config=[
            {"nome": "Ônibus 1", "capacidade": 50},
            {"nome": "Van 1", "capacidade": 20},
        ])

        # Comportamento normal do bin-packing: nenhum onibus_ocupado ainda,
        # então tenta ônibus vazio antes de van (ordem do best_fit padrão).
        assert sum(v["ocupado"] for v in veiculos) == 16


class TestAgrupamentoObrigatorioIfbaUnef:

    def test_garante_juntas_quando_bin_packing_as_separa(self):
        faculdades = [
            ("IFBA", {"ida": 5, "volta": 5, "total": 5}),
            ("UNEF", {"ida": 16, "volta": 16, "total": 16}),
            ("SENAI", {"ida": 29, "volta": 29, "total": 29}),
        ]
        # Sem van (nenhuma sobra pra priorizar) e capacidades escolhidas
        # pra forçar o bin-packing normal a separar IFBA e UNEF em ônibus
        # diferentes — a regra obrigatória corrige depois.
        veiculos = distribuir(faculdades, veiculos_config=[
            {"nome": "Ônibus 1", "capacidade": 34},
            {"nome": "Ônibus 2", "capacidade": 21},
        ])

        resultado = ro.aplicar(veiculos)

        assert resultado["critico"] is False
        loc_ifba = [i for i, v in enumerate(resultado["veiculos"]) if any(f[0] == "IFBA" for f in v["faculdades"])][0]
        loc_unef = [i for i, v in enumerate(resultado["veiculos"]) if any(f[0] == "UNEF" for f in v["faculdades"])][0]
        assert loc_ifba == loc_unef

    def test_critico_quando_nao_ha_veiculo_para_juntar(self):
        faculdades = [
            ("IFBA", {"ida": 10, "volta": 10, "total": 10}),
            ("UNEF", {"ida": 10, "volta": 10, "total": 10}),
        ]
        veiculos = distribuir(faculdades, veiculos_config=[
            {"nome": "Van 1", "capacidade": 10},
            {"nome": "Van 2", "capacidade": 10},
        ])

        resultado = ro.aplicar(veiculos)

        assert resultado["critico"] is True
        assert "IFBA" in resultado["motivo_critico"]
        assert "UNEF" in resultado["motivo_critico"]
