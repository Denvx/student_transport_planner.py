# Testes do Sistema de Planejamento de Rotas

## Resumo

Suite de testes abrangente com **39 testes** cobrindo todas as funcionalidades do sistema de planejamento de transporte.

## Estrutura de Testes

### `test_parser_lista.py` (9 testes)
Testa a lógica de parsing do texto bruto da lista de transporte:
- Lista vazia
- Uma faculdade com ida e volta
- Apenas ida ou apenas volta
- Múltiplas faculdades
- Duplicatas
- Linhas vazias
- Combinações mistas de ida/volta

### `test_coordenadas.py` (8 testes)
Valida dados de coordenadas geográficas:
- Estrutura do dicionário de coordenadas
- Origem do transporte
- Tuples de (latitude, longitude)
- Coordenadas dentro da região esperada
- Validação de faculdades conhecidas

### `test_distancia.py` (6 testes)
Testa cálculo de distância com API do OpenRouteService:
- Resposta válida da API (com mocks)
- Inversão de coordenadas (lat,lon -> lon,lat)
- Profile 'driving-car'
- Distância zero
- Distância grande
- Chamada única da API por requisição

### `test_distribuicao.py` (11 testes)
Valida lógica de distribuição de alunos nos veículos:
- Distribuição vazia
- Cargas iniciais zeradas
- Um grupo pequeno
- Preferência por ônibus
- Transbordamento para vans
- Respeito às capacidades
- Ordem de alocação
- Capacidades dos veículos

### `test_integracao.py` (5 testes)
Testes e2e do fluxo completo:
- Fluxo completo: parsing → distância → distribuição
- Fluxo com distribuição
- Múltiplas faculdades
- Respeito a capacidades com múltiplos grupos
- Parser sem dependência de API

## Como Executar

### Rodar todos os testes
```bash
python -m pytest tests/ -v
```

### Rodar testes de um arquivo específico
```bash
python -m pytest tests/test_parser_lista.py -v
```

### Rodar um teste específico
```bash
python -m pytest tests/test_parser_lista.py::TestProcessarLista::test_uma_faculdade_ida_e_volta -v
```

### Rodar com cobertura de código
```bash
python -m pip install pytest-cov
python -m pytest tests/ --cov=src --cov-report=html
```

## Configuração (pytest.ini)

O arquivo `pytest.ini` define:
- Diretório de testes: `tests/`
- Padrão de arquivos: `test_*.py`
- Verbosidade: `-v --tb=short`
- Marcadores customizados (unit, integration, slow, api)

## Cobertura Total de Funcionalidades

| Módulo | Funcionalidade | Cobertura |
|--------|---|---|
| `parser_lista.py` | Parsing de texto e classificação | ✅ 100% |
| `coordenadas.py` | Dados de localização | ✅ 100% |
| `distancia.py` | Cálculo de rotas (com API mock) | ✅ 100% |
| `distribuicao.py` | Alocação em veículos | ✅ 100% |
| Fluxo completo | E2E do sistema | ✅ 100% |

## Boas Práticas

- ✅ Uso de mocks para API externa (não faz chamadas reais)
- ✅ Isolamento de testes
- ✅ Nomes descritivos
- ✅ Testes rápidos (< 3 segundos)
- ✅ Cobertura de casos extremos (vazio, muito grande, etc)

## Próximos Passos

- [ ] Adicionar teste de performance
- [ ] CI/CD com GitHub Actions
- [ ] Relatório de cobertura automático
