import pytest
from src.distribuicao import distribuir
from src import regras_obrigatorias as ro


class TestSeparacaoUnexUnef:

    def test_separa_quando_ha_espaco_em_outro_veiculo(self):
        faculdades = [
            ("UNEX", {"ida": 10, "volta": 10, "total": 10}),
            ("UNEF", {"ida": 8, "volta": 8, "total": 8}),
        ]
        veiculos = distribuir(faculdades, veiculos_config=[
            {"nome": "Van 1", "capacidade": 20},
            {"nome": "Van 2", "capacidade": 15},
        ])

        resultado = ro.aplicar(veiculos)

        assert resultado["critico"] is False
        loc_unex = [i for i, v in enumerate(resultado["veiculos"]) if any(f[0] == "UNEX" for f in v["faculdades"])][0]
        loc_unef = [i for i, v in enumerate(resultado["veiculos"]) if any(f[0] == "UNEF" for f in v["faculdades"])][0]
        assert loc_unex != loc_unef

    def test_critico_quando_nao_ha_veiculo_para_separar(self):
        faculdades = [
            ("UNEX", {"ida": 10, "volta": 10, "total": 10}),
            ("UNEF", {"ida": 8, "volta": 8, "total": 8}),
        ]
        veiculos = distribuir(faculdades, veiculos_config=[
            {"nome": "Van 1", "capacidade": 20},
        ])

        resultado = ro.aplicar(veiculos)

        assert resultado["critico"] is True
        assert "UNEX" in resultado["motivo_critico"]
        assert "UNEF" in resultado["motivo_critico"]

    def test_nao_mexe_quando_apenas_uma_das_duas_existe(self):
        faculdades = [("UNEX", {"ida": 10, "volta": 10, "total": 10})]
        veiculos = distribuir(faculdades, veiculos_config=[{"nome": "Van 1", "capacidade": 20}])

        resultado = ro.aplicar(veiculos)

        assert resultado["critico"] is False
        assert resultado["warnings"] == []

    def test_nao_mexe_quando_ja_estao_separadas(self):
        faculdades = [
            ("UNEX", {"ida": 10, "volta": 10, "total": 10}),
            ("UNEF", {"ida": 8, "volta": 8, "total": 8}),
        ]
        veiculos = distribuir(faculdades, veiculos_config=[
            {"nome": "Onibus 1", "capacidade": 50},
            {"nome": "Van 1", "capacidade": 20},
        ])
        # Nesse cenário elas já cabem em veículos diferentes pelo bin-packing normal
        resultado = ro.aplicar(veiculos)
        assert resultado["critico"] is False


class TestAgrupamentoUnifanQuadrivium:

    def test_junta_quando_bin_packing_separou(self):
        faculdades = [
            ("UNIFAN", {"ida": 5, "volta": 5, "total": 5}),
            ("QUADRIVIUM", {"ida": 5, "volta": 5, "total": 5}),
            ("UEFS", {"ida": 45, "volta": 45, "total": 45}),
        ]
        veiculos = distribuir(faculdades, veiculos_config=[
            {"nome": "Onibus 1", "capacidade": 50},
            {"nome": "Van 1", "capacidade": 10},
        ])

        resultado = ro.aplicar(veiculos)

        assert resultado["critico"] is False
        loc_unifan = [i for i, v in enumerate(resultado["veiculos"]) if any(f[0] == "UNIFAN" for f in v["faculdades"])][0]
        loc_quadrivium = [i for i, v in enumerate(resultado["veiculos"]) if any(f[0] == "QUADRIVIUM" for f in v["faculdades"])][0]
        assert loc_unifan == loc_quadrivium

    def test_critico_quando_juntas_excedem_qualquer_veiculo(self):
        faculdades = [
            ("UNIFAN", {"ida": 30, "volta": 30, "total": 30}),
            ("QUADRIVIUM", {"ida": 30, "volta": 30, "total": 30}),
        ]
        veiculos = distribuir(faculdades, veiculos_config=[
            {"nome": "Van 1", "capacidade": 35},
            {"nome": "Van 2", "capacidade": 35},
        ])

        resultado = ro.aplicar(veiculos)

        assert resultado["critico"] is True
        assert "UNIFAN" in resultado["motivo_critico"]
        assert "QUADRIVIUM" in resultado["motivo_critico"]

    def test_nao_mexe_quando_apenas_uma_das_duas_existe(self):
        faculdades = [("UNIFAN", {"ida": 5, "volta": 5, "total": 5})]
        veiculos = distribuir(faculdades, veiculos_config=[{"nome": "Van 1", "capacidade": 20}])

        resultado = ro.aplicar(veiculos)

        assert resultado["critico"] is False
        assert resultado["warnings"] == []
