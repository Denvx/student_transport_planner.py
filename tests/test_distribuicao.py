import pytest
from src.distribuicao import distribuir


class TestDistribuicao:
    """Testes para lógica de distribuição de alunos nos veículos"""

    def test_distribuicao_vazia(self):
        """Testa distribuição com lista vazia"""
        resultado = distribuir([])
        
        assert len(resultado) == 6  # 2 ônibus + 4 vans
        for veiculo in resultado:
            assert veiculo["ocupado"] == 0
            assert veiculo["faculdades"] == []

    def test_cargas_iniciais_zeradas(self):
        """Testa se todos os veículos começam vazios"""
        resultado = distribuir([])
        
        for veiculo in resultado:
            assert veiculo["ocupado"] == 0
            assert "capacidade" in veiculo
            assert "nome" in veiculo

    def test_distribucao_um_grupo_pequeno(self):
        """Testa distribuição de um grupo que cabe em qualquer veículo"""
        faculdades = [
            ("UEFS", {"ida": 5, "volta": 5, "total": 5})
        ]
        
        resultado = distribuir(faculdades)
        
        total_distribuido = sum(v["ocupado"] for v in resultado)
        assert total_distribuido == 5

    def test_preferencia_onibus(self):
        """Testa se prioriza ônibus antes de vans"""
        faculdades = [
            ("UEFS", {"ida": 25, "volta": 25, "total": 25})
        ]
        
        resultado = distribuir(faculdades)
        
        onibus_1 = resultado[0]
        assert onibus_1["nome"] == "Ônibus 1"
        assert onibus_1["ocupado"] == 25

    def test_transbordamento(self):
        """Testa distribuição com múltiplos grupos que precisam de vários veículos"""
        faculdades = [
            ("UEFS", {"ida": 30, "volta": 30, "total": 30}),
            ("SENAI", {"ida": 30, "volta": 30, "total": 30}),
            ("UNIFAN", {"ida": 20, "volta": 20, "total": 20})
        ]
        
        resultado = distribuir(faculdades)
        
        total_distribuido = sum(v["ocupado"] for v in resultado)
        assert total_distribuido == 80

    def test_respeitam_capacidades(self):
        """Testa se nenhum veículo ultrapassa sua capacidade"""
        faculdades = [
            ("UEFS", {"ida": 40, "volta": 40, "total": 40}),
            ("SENAI", {"ida": 35, "volta": 35, "total": 35}),
            ("UNIFAN", {"ida": 20, "volta": 20, "total": 20})
        ]
        
        resultado = distribuir(faculdades)
        
        for veiculo in resultado:
            assert veiculo["ocupado"] <= veiculo["capacidade"]

    def test_primeira_veiculo_com_espaco(self):
        """Testa se aloca no primeiro veículo que tem espaço"""
        faculdades = [
            ("UEFS", {"ida": 10, "volta": 10, "total": 10})
        ]
        
        resultado = distribuir(faculdades)
        
        onibus_1 = resultado[0]
        assert len(onibus_1["faculdades"]) == 1
        assert onibus_1["faculdades"][0][0] == "UEFS"

    def test_nenhum_grupo_deixado_para_tras(self):
        """Testa se todos os grupos são distribuídos"""
        faculdades = [
            ("UEFS", {"ida": 45, "volta": 45, "total": 45}),
            ("SENAI", {"ida": 40, "volta": 40, "total": 40}),
            ("UNIFAN", {"ida": 15, "volta": 15, "total": 15})
        ]
        
        resultado = distribuir(faculdades)
        
        total_faculdades_distribuidas = sum(
            len(v["faculdades"]) for v in resultado
        )
        assert total_faculdades_distribuidas == 3

    def test_ordem_alocacao(self):
        """Testa se é respeitada a ordem de entrada das faculdades"""
        faculdades = [
            ("UEFS", {"ida": 10, "volta": 10, "total": 10}),
            ("SENAI", {"ida": 15, "volta": 15, "total": 15}),
        ]
        
        resultado = distribuir(faculdades)
        
        # Primeiro grupo deve estar no Ônibus 1
        assert ("UEFS", {"ida": 10, "volta": 10, "total": 10}) in resultado[0]["faculdades"]

    def test_vans_sao_usadas_apos_onibus(self):
        """Testa se vans são usadas somente após ônibus ficarem cheios"""
        faculdades = [
            ("UEFS", {"ida": 50, "volta": 50, "total": 50}),
            ("SENAI", {"ida": 45, "volta": 45, "total": 45}),
            ("UNIFAN", {"ida": 15, "volta": 15, "total": 15})
        ]
        
        resultado = distribuir(faculdades)
        
        onibus_1 = resultado[0]
        onibus_2 = resultado[1]
        
        assert onibus_1["ocupado"] == 50
        
        assert onibus_2["ocupado"] == 45
        
        total_van = sum(v["ocupado"] for v in resultado[2:])
        assert total_van == 15

    def test_capacidades_veiculos(self):
        """Testa se as capacidades dos veículos estão corretas"""
        resultado = distribuir([])
        
        nomes_capacidades = {v["nome"]: v["capacidade"] for v in resultado}
        
        assert nomes_capacidades["Ônibus 1"] == 50
        assert nomes_capacidades["Ônibus 2"] == 50
        assert nomes_capacidades["Van 1"] == 20
        assert nomes_capacidades["Van 2"] == 15
