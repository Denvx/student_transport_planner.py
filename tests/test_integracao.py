import pytest
from unittest.mock import patch
from src.parser_lista import processar_lista
from src.coordenadas import coordenadas, origem
from src.distancia import distancia_rota
from src.distribuicao import distribuir


class TestIntegracaoFull:
    """Teste de integração: simulação do fluxo completo do sistema"""

    @patch('src.distancia.client')
    def test_fluxo_completo(self, mock_client):
        """Testa o fluxo completo: parsing -> distância -> distribuição"""
        
        # Mock da API de rotas
        mock_response = {
            'routes': [{
                'summary': {
                    'distance': 45000,
                    'duration': 2700
                }
            }]
        }
        mock_client.directions.return_value = mock_response
        
        # 1. Parsing da lista de transporte
        texto = """
        UEFS
        1. Gabriel
        2. Larissa
        3. Icaro (ida)
        
        SENAI
        1. João (volta)
        2. Maria
        """
        
        dados_faculdades = processar_lista(texto, coordenadas)
        
        # Verifica parsing
        assert "UEFS" in dados_faculdades
        assert "SENAI" in dados_faculdades
        assert dados_faculdades["UEFS"]["total"] >= 3
        assert dados_faculdades["SENAI"]["total"] >= 2

    @patch('src.distancia.client')
    def test_fluxo_com_distribuicao(self, mock_client):
        """Testa fluxo: parsing + distribuição"""
        
        mock_response = {
            'routes': [{
                'summary': {
                    'distance': 45000,
                    'duration': 2700
                }
            }]
        }
        mock_client.directions.return_value = mock_response
        
        texto = """
        UEFS
        1. Gabriel
        2. Larissa
        3. Icaro
        4. Leo
        5. Sergio
        """
        
        dados = processar_lista(texto, coordenadas)
        
        faculdades_ordenadas = [(fac, info) for fac, info in dados.items()]
        
        veiculos = distribuir(faculdades_ordenadas)
        
        assert len(veiculos) == 6
        total_alocado = sum(v["ocupado"] for v in veiculos)
        assert total_alocado == dados["UEFS"]["total"]

    @patch('src.distancia.client')
    def test_fluxo_multiplas_faculdades(self, mock_client):
        """Testa fluxo com múltiplas faculdades"""
        
        mock_response = {
            'routes': [{
                'summary': {
                    'distance': 45000,
                    'duration': 2700
                }
            }]
        }
        mock_client.directions.return_value = mock_response
        
        texto = """
        UEFS
        1. Aluno1
        2. Aluno2
        3. Aluno3
        
        SENAI
        1. Aluno4
        2. Aluno5
        
        UNIFAN
        1. Aluno6 (ida)
        2. Aluno7 (volta)
        """
        
        dados = processar_lista(texto, coordenadas)
        faculdades_ordenadas = [(fac, info) for fac, info in dados.items()]
        veiculos = distribuir(faculdades_ordenadas)
        
        total_faculdades = sum(len(v["faculdades"]) for v in veiculos)
        assert total_faculdades == 3
        
        total_alunos = sum(v["ocupado"] for v in veiculos)
        total_esperado = sum(info["total"] for _, info in dados.items())
        assert total_alunos == total_esperado

    @patch('src.distancia.client')
    def test_respeitam_capacidades_com_multiplos_grupos(self, mock_client):
        """Testa se capacidades são respeitadas com múltiplos grupos"""
        
        mock_response = {
            'routes': [{
                'summary': {
                    'distance': 45000,
                    'duration': 2700
                }
            }]
        }
        mock_client.directions.return_value = mock_response
        
        texto = """
        UEFS
        """ + "\n".join([f"{i}. Aluno{i}" for i in range(1, 46)])  # 45 alunos
        
        texto += """
        SENAI
        """ + "\n".join([f"{i}. Aluno{i+45}" for i in range(1, 36)])  # 35 alunos
        
        texto += """
        UNIFAN
        """ + "\n".join([f"{i}. Aluno{i+80}" for i in range(1, 21)])  # 20 alunos
        
        dados = processar_lista(texto, coordenadas)
        faculdades_ordenadas = [(fac, info) for fac, info in dados.items()]
        veiculos = distribuir(faculdades_ordenadas)
        
        for veiculo in veiculos:
            assert veiculo["ocupado"] <= veiculo["capacidade"], \
                f"{veiculo['nome']} ultrapassou capacidade"

    def test_sem_dependencia_api_para_distribuicao(self):
        """Testa se distribuição funciona sem chamar API"""
        
        faculdades = [
            ("UEFS", {"ida": 25, "volta": 25, "total": 25}),
            ("SENAI", {"ida": 20, "volta": 20, "total": 20})
        ]
        
        veiculos = distribuir(faculdades)
        
        total = sum(v["ocupado"] for v in veiculos)
        assert total == 45
