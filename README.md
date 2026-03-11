# Sistema de Planejamento de Rotas — AERJ

**Automacao do transporte universitario de Riacho do Jacuipe, Bahia.**

[![Status](https://img.shields.io/badge/status-em%20desenvolvimento-yellow?style=flat-square)](https://github.com)
[![Python](https://img.shields.io/badge/Python-3.x-blue?style=flat-square&logo=python)](https://www.python.org/)

---

## Sobre o Projeto

Este projeto foi desenvolvido para automatizar o planejamento do transporte universitario da **AERJ — Associacao de Transporte de Riacho do Jacuipe**.

O sistema le uma lista de estudantes organizada por faculdade (gerada no WhatsApp, por exemplo), processa os dados, remove duplicatas, identifica quem vai na ida e quem volta, ordena as faculdades por distancia geografica da origem usando a API do OpenRouteService para calculos precisos de rota de carro, e distribui os alunos nos veiculos disponiveis de forma eficiente.

O processo que antes era feito manualmente passa a ser resolvido em segundos.

---

## Problema que o sistema resolve

As listas de transporte chegam em formato livre e alunos sem especificar se vao na ida, na volta ou nos dois sentidos. Processar isso manualmente e lento e sujeito a erro.

Este script:

- Le o texto bruto da lista e identifica cada faculdade automaticamente
- Remove entradas duplicadas
- Classifica cada passageiro como ida, volta ou ambos
- Ordena as faculdades pela distancia em relacao a origem do transporte
- Distribui os grupos de alunos nos veiculos disponiveis respeitando a capacidade de cada um

---

## Frota Disponivel

| Veiculo  | Capacidade |
|----------|:----------:|
| Ônibus 1 | 50 lugares |
| Ônibus 2 | 50 lugares |
| Van 1    | 20 lugares |
| Van 2    | 15 lugares |

O algoritmo encaixa cada grupo de alunos no primeiro veiculo que ainda tenha espaco disponivel, respeitando a ordem de distancia da rota.

---

## Como Funciona

### 1. Leitura do texto

O sistema recebe o texto bruto da lista de transporte, que normalmente vem de grupos de WhatsApp com formatacao inconsistente:

```
UEFS
1. Gabriel
2. Larissa
3. Icaro (ida)
12. Leo (volta)
13. Sergio

SENAI
1. Tindade
2. Hasmin
```

### 2. Processamento e limpeza

O script percorre o texto linha a linha e:

- Identifica o nome da faculdade quando a linha esta em maiusculas
- Detecta entradas numeradas e extrai o nome do passageiro
- Verifica se ha indicacao de "ida" ou "volta" na linha
- Quando nao ha indicacao, assume que o aluno vai nos dois sentidos
- Ignora entradas duplicadas (mesmo numero de linha repetido dentro da mesma faculdade)

### 3. Ordenacao por distancia

Cada faculdade tem coordenadas geograficas cadastradas. O sistema calcula a distancia real de rota de carro entre a origem do transporte e cada faculdade usando a API do OpenRouteService, definindo a ordem otimizada da rota baseada em distancia e tempo de viagem.

### 4. Distribuicao nos veiculos

Com os grupos ordenados, o algoritmo percorre a lista e aloca cada faculdade no primeiro veiculo que ainda tenha capacidade suficiente:

```
Ônibus 1 (48/50)
 - UEFS      | Ida: 13 | Volta: 11 | Total: 13
 - SENAI     | Ida:  4 | Volta:  3 | Total:  4
 - QUADRIVIUM| Ida:  8 | Volta:  7 | Total:  8

Van 1 (19/20)
 - UNIFAN    | Ida: 18 | Volta: 15 | Total: 18
 - IFBA      | Ida:  1 | Volta:  1 | Total:  1
```

---
## Tecnologias Utilizadas

- **Python 3.x**
- `re` — expressoes regulares para parsing do texto
- `collections.defaultdict` — agrupamento dos dados por faculdade
- `openrouteservice` — API para calculo de rotas e distancias reais
- `python-dotenv` — carregamento de variaveis de ambiente do arquivo .env

---

## Estrutura do Projeto

O código está organizado em módulos para facilitar manutenção e testes:

- `main.py`: Arquivo principal que importa os módulos, processa a lista de texto, ordena as faculdades por distância e distribui nos veículos, imprimindo o resultado.
- `coordenadas.py`: Define as coordenadas geográficas (latitude, longitude) de cada faculdade e o ponto de origem do transporte.
- `distancia.py`: Contém a função para calcular a distância euclidiana entre dois pontos geográficos.
- `parser_lista.py`: Processa o texto bruto da lista, identificando faculdades e alunos, classificando-os como ida, volta ou ambos.
- `distribuicao.py`: Implementa a lógica de distribuição das faculdades nos veículos disponíveis, priorizando o primeiro com capacidade suficiente.

---

## Como Executar

### 1. Pré-requisitos

- Python 3.x instalado (https://www.python.org/downloads/)
- Conta no OpenRouteService para obter chave da API (gratuita para uso limitado: https://openrouteservice.org/)

### 2. Instalação das dependências

```bash
# Clone o repositorio
git clone https://github.com/Denvx/student_transport_planner.py.git
cd student_transport_planner.py

# Instale as dependências principais
pip install openrouteservice python-dotenv

# Instale também pytest para rodar os testes
pip install pytest pytest-mock
```

### 3. Configuração da API

- Copie o arquivo de exemplo para o arquivo real:
  ```bash
  cp .env.example .env
  ```

- Edite o arquivo `.env` e adicione sua chave da API do OpenRouteService:
  ```
  API_KEY_HEIGIT=sua_chave_aqui
  ```
  (Obtenha a chave em https://openrouteservice.org/dev/#/signup)

### 4. Execução

```bash
python main.py
```

Para usar com uma nova lista, substitua o conteudo da variavel `texto` no arquivo `main.py` pelo texto atualizado da lista de transporte.

---

## Testes

O projeto possui uma suite de **39 testes** cobrindo todas as funcionalidades. Os testes utilizam mocks para a API externa (não fazem chamadas reais).

### Estrutura de Testes

- `test_parser_lista.py` — 9 testes para parsing de texto
- `test_coordenadas.py` — 8 testes para validação de dados geográficos  
- `test_distancia.py` — 6 testes para cálculo de rotas
- `test_distribuicao.py` — 11 testes para alocação em veículos
- `test_integracao.py` — 5 testes do fluxo completo (end-to-end)

### Rodar Todos os Testes

```bash
python -m pytest tests/ -v
```

### Rodar Teste Específico

Rodar um arquivo de testes:
```bash
python -m pytest tests/test_parser_lista.py -v
```

Rodar um único teste:
```bash
python -m pytest tests/test_parser_lista.py::TestProcessarLista::test_uma_faculdade_ida_e_volta -v
```

### Visualizar Cobertura de Código

```bash
# Instale ferramenta de cobertura
pip install pytest-cov

# Gere relatório
python -m pytest tests/ --cov=src --cov-report=html

# Abra em navegador (será criado em htmlcov/index.html)
```

### Resultado Esperado

```
============================= 39 passed in ~3s =============================
```

Todos os testes devem passar sem erros.

---

## Proximas Etapas

- ✅ Calculo de rota otimizada com API de mapas (implementado)
- Leitura automatica do texto via arquivo `.txt` ou entrada no terminal
- Relatorio exportado em PDF ou planilha
- Interface web para gestao das listas
- Cadastro de alunos e faculdades em banco de dados

---

## Contexto

O projeto faz parte de um sistema maior em desenvolvimento para a **AERJ**, associacao responsavel pelo transporte de estudantes universitarios de Riachão do Jacuipe para Feira de Santana e outras cidades.

O objetivo e digitalizar e automatizar processos que hoje dependem de controle manual, reduzindo erros e otimizando o uso da frota.

---

## Autor

**Denver Oliveira**  
Estudante de Desenvolvimento de Sistemas  
Riachão do Jacuipe, Bahia
