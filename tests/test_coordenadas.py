import pytest
from src.coordenadas import coordenadas, origem


class TestCoordenadas:
    """Testes para dados de coordenadas"""

    def test_coordenadas_existe(self):
        """Testa se dicionário de coordenadas existe"""
        assert coordenadas is not None
        assert isinstance(coordenadas, dict)

    def test_coordenadas_nao_vazio(self):
        """Testa se há faculdades cadastradas"""
        assert len(coordenadas) > 0

    def test_todas_faculdades_tem_coordenadas(self):
        """Testa se cada faculdade tem tupla de (latitude, longitude)"""
        for faculdade, coords in coordenadas.items():
            assert isinstance(coords, tuple)
            assert len(coords) == 2
            lat, lon = coords
            assert isinstance(lat, (int, float))
            assert isinstance(lon, (int, float))

    def test_origem_existe(self):
        """Testa se ponto de origem é definido"""
        assert origem is not None
        assert isinstance(origem, tuple)
        assert len(origem) == 2

    def test_origem_coordenadas_validas(self):
        """Testa se origem tem coordenadas válidas"""
        lat, lon = origem
        assert isinstance(lat, (int, float))
        assert isinstance(lon, (int, float))
        # Origem deve estar em Riachão do Jacuípe, Bahia (~-12, ~-39)
        assert -15 < lat < -10
        assert -41 < lon < -37

    def test_faculdade_conhecida(self):
        """Testa se faculdades conhecidas estão no cadastro"""
        faculdades_esperadas = ["UEFS", "SENAI", "UNIFAN", "UNEF", "IFBA", "UNIRB"]
        for fac in faculdades_esperadas:
            assert fac in coordenadas, f"Faculdade {fac} não encontrada"

    def test_coordenadas_razoaveis(self):
        """Testa se todas as coordenadas estão na região de Feira de Santana/Riachão"""
        for faculdade, (lat, lon) in coordenadas.items():
            # Região geral (Bahia)
            assert -14 < lat < -11, f"{faculdade} tem latitude fora da região"
            assert -40 < lon < -38, f"{faculdade} tem longitude fora da região"

    def test_coordenadas_diferente_origem(self):
        """Testa se nenhuma faculdade está na mesma localização da origem"""
        for faculdade, coords in coordenadas.items():
            assert coords != origem, f"{faculdade} tem mesma coordenada que origem"
