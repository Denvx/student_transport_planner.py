import pytest
from unittest.mock import patch
from src.distancia import distancia_rota


class TestRotaRiachaoUefs:
    """
    Antes deste teste era um script solto (sem assert, sem função test_*)
    que fazia uma chamada REAL e não mockada ao OpenRouteService no momento
    da coleta do pytest — travava a suíte inteira sem ORS_API_KEY configurada
    e consumia cota real da API quando configurada. Substituído por um teste
    de verdade, seguindo o mesmo padrão de mock de test_distancia.py.
    """

    @patch('src.distancia.client')
    def test_distancia_riachao_ate_uefs(self, mock_client):
        mock_response = {
            'routes': [{
                'summary': {
                    'distance': 52340,
                    'duration': 3120,
                }
            }]
        }
        mock_client.directions.return_value = mock_response

        origem = (-11.810503167138526, -39.382493942430905)  # Riachão
        destino = (-12.200186611506028, -38.97186855898357)  # UEFS

        distancia, tempo = distancia_rota(origem, destino)

        assert distancia == 52340
        assert tempo == 3120
        mock_client.directions.assert_called_once()
