import pytest
from unittest.mock import Mock, patch
from src.distancia import distancia_rota


class TestDistancia:
    """Testes para cálculo de distância com API OpenRouteService"""

    @patch('src.distancia.client')
    def test_distancia_rota_valida(self, mock_client):
        """Testa cálculo de distância com resposta válida da API"""
        # Simula resposta da API OpenRouteService
        mock_response = {
            'routes': [{
                'summary': {
                    'distance': 45000,  # metros
                    'duration': 2700    # segundos
                }
            }]
        }
        mock_client.directions.return_value = mock_response
        
        p1 = (-11.810503167138526, -39.382493942430905)  # Origem
        p2 = (-12.200186611506028, -38.97186855898357)   # UEFS
        
        distancia, tempo = distancia_rota(p1, p2)
        
        assert distancia == 45000
        assert tempo == 2700
        mock_client.directions.assert_called_once()

    @patch('src.distancia.client')
    def test_coordenadas_sao_revertidas(self, mock_client):
        """Testa se as coordenadas são invertidas (lat,lon -> lon,lat)"""
        mock_response = {
            'routes': [{
                'summary': {
                    'distance': 50000,
                    'duration': 3000
                }
            }]
        }
        mock_client.directions.return_value = mock_response
        
        p1 = (-11.8, -39.4)
        p2 = (-12.2, -38.9)
        
        distancia_rota(p1, p2)
        
        # Verifica se foi chamado com coordenadas invertidas (lon, lat)
        call_args = mock_client.directions.call_args
        coords = call_args.kwargs['coordinates']
        
        assert coords[0] == (-39.4, -11.8)  # (lon, lat)
        assert coords[1] == (-38.9, -12.2)

    @patch('src.distancia.client')
    def test_profile_driving_car(self, mock_client):
        """Testa se usa projeto de rota 'driving-car'"""
        mock_response = {
            'routes': [{
                'summary': {
                    'distance': 30000,
                    'duration': 1800
                }
            }]
        }
        mock_client.directions.return_value = mock_response
        
        p1 = (-11.8, -39.4)
        p2 = (-12.2, -38.9)
        
        distancia_rota(p1, p2)
        
        call_args = mock_client.directions.call_args
        assert call_args.kwargs['profile'] == 'driving-car'

    @patch('src.distancia.client')
    def test_distancia_zero(self, mock_client):
        """Testa caso de distância zero (mesma localização)"""
        mock_response = {
            'routes': [{
                'summary': {
                    'distance': 0,
                    'duration': 0
                }
            }]
        }
        mock_client.directions.return_value = mock_response
        
        p1 = (-12.0, -39.0)
        p2 = (-12.0, -39.0)
        
        distancia, tempo = distancia_rota(p1, p2)
        
        assert distancia == 0
        assert tempo == 0

    @patch('src.distancia.client')
    def test_distancia_grande(self, mock_client):
        """Testa caso de distância longa"""
        mock_response = {
            'routes': [{
                'summary': {
                    'distance': 150000,  # 150 km
                    'duration': 7200     # 2 horas
                }
            }]
        }
        mock_client.directions.return_value = mock_response
        
        p1 = (-11.8, -39.4)
        p2 = (-13.5, -37.0)
        
        distancia, tempo = distancia_rota(p1, p2)
        
        assert distancia == 150000
        assert tempo == 7200

    @patch('src.distancia.client')
    def test_api_chamada_uma_unica_vez(self, mock_client):
        """Testa se API é chamada apenas uma vez por requisição"""
        mock_response = {
            'routes': [{
                'summary': {
                    'distance': 40000,
                    'duration': 2400
                }
            }]
        }
        mock_client.directions.return_value = mock_response
        
        p1 = (-11.8, -39.4)
        p2 = (-12.2, -38.9)
        
        distancia_rota(p1, p2)
        
        assert mock_client.directions.call_count == 1
