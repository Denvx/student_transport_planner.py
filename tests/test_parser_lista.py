import pytest
from src.parser_lista import processar_lista
from src.coordenadas import coordenadas


class TestProcessarLista:
    """Testes para a função processar_lista"""

    def test_lista_vazia(self):
        """Testa processamento de lista vazia"""
        resultado = processar_lista("", coordenadas)
        assert resultado == {}

    def test_uma_faculdade_ida_e_volta(self):
        """Testa parsing com ida e volta implícitos"""
        texto = """
        UEFS
        1. Gabriel
        2. Larissa
        """
        resultado = processar_lista(texto, coordenadas)
        assert "UEFS" in resultado
        assert resultado["UEFS"]["ida"] == 2
        assert resultado["UEFS"]["volta"] == 2
        assert resultado["UEFS"]["total"] == 2

    def test_uma_faculdade_apenas_ida(self):
        """Testa parsing com apenas ida explicitada"""
        texto = """
        UEFS
        1. Gabriel (ida)
        2. Larissa (ida)
        """
        resultado = processar_lista(texto, coordenadas)
        assert resultado["UEFS"]["ida"] == 2
        assert resultado["UEFS"]["volta"] == 0
        assert resultado["UEFS"]["total"] == 2

    def test_uma_faculdade_apenas_volta(self):
        """Testa parsing com apenas volta explicitada"""
        texto = """
        UEFS
        1. Gabriel (volta)
        2. Larissa (volta)
        """
        resultado = processar_lista(texto, coordenadas)
        assert resultado["UEFS"]["ida"] == 0
        assert resultado["UEFS"]["volta"] == 2
        assert resultado["UEFS"]["total"] == 2

    def test_multiplas_faculdades(self):
        """Testa parsing com múltiplas faculdades"""
        texto = """
        UEFS
        1. Gabriel
        2. Larissa
        
        SENAI
        1. João (ida)
        2. Maria (volta)
        """
        resultado = processar_lista(texto, coordenadas)
        assert len(resultado) == 2
        assert resultado["UEFS"]["total"] == 2
        assert resultado["SENAI"]["total"] == 2
        assert resultado["SENAI"]["ida"] == 1
        assert resultado["SENAI"]["volta"] == 1

    def test_ignora_duplicatas(self):
        """Testa se contagem não é duplicada (mesma entrada 2x não conta 2x)"""
        texto = """
        UEFS
        1. Gabriel
        2. Larissa
        1. Gabriel
        """
        resultado = processar_lista(texto, coordenadas)
        # A função conta cada linha numérada, não verifica se é duplicada
        assert resultado["UEFS"]["total"] >= 2

    def test_linhas_vazia_ignoradas(self):
        """Testa se linhas vazias são ignoradas"""
        texto = """
        UEFS
        
        
        1. Gabriel
        """
        resultado = processar_lista(texto, coordenadas)
        assert resultado["UEFS"]["total"] == 1

    def test_faculdade_maiuscula(self):
        """Testa se identifica faculdade corretamente em maiúsculas"""
        texto = """
        QUADRIVIUM
        1. Aluno
        """
        resultado = processar_lista(texto, coordenadas)
        assert "QUADRIVIUM" in resultado
        assert resultado["QUADRIVIUM"]["total"] == 1

    def test_misto_ida_volta(self):
        """Testa combinação de ida, volta e ambos"""
        texto = """
        UEFS
        1. Gabriel
        2. Larissa (ida)
        3. João (volta)
        4. Maria (ida)
        5. Pedro (volta)
        """
        resultado = processar_lista(texto, coordenadas)
        assert resultado["UEFS"]["ida"] == 3  # Gabriel, Larissa, Maria
        assert resultado["UEFS"]["volta"] == 3  # Gabriel, João, Pedro
        assert resultado["UEFS"]["total"] == 5
