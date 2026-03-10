# Sistema de Planejamento de Rotas — AERJ

**Automacao do transporte universitario de Riacho do Jacuipe, Bahia.**

[![Status](https://img.shields.io/badge/status-em%20desenvolvimento-yellow?style=flat-square)](https://github.com)
[![Python](https://img.shields.io/badge/Python-3.x-blue?style=flat-square&logo=python)](https://www.python.org/)

---

## Sobre o Projeto

Este projeto foi desenvolvido para automatizar o planejamento do transporte universitario da **AERJ — Associacao de Transporte de Riacho do Jacuipe**.

O sistema le uma lista de estudantes organizada por faculdade (gerada no WhatsApp, por exemplo), processa os dados, remove duplicatas, identifica quem vai na ida e quem volta, ordena as faculdades por distancia geografica da origem e distribui os alunos nos veiculos disponiveis de forma eficiente.

O processo que antes era feito manualmente passa a ser resolvido em segundos.

---

## Problema que o sistema resolve

As listas de transporte chegam em formato livre, com repeticoes, numeracoes fora de ordem e alunos sem especificar se vao na ida, na volta ou nos dois sentidos. Processar isso manualmente e lento e sujeito a erro.

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
| Onibus 1 | 50 lugares |
| Onibus 2 | 50 lugares |
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

Cada faculdade tem coordenadas geograficas cadastradas. O sistema calcula a distancia entre a origem do transporte e cada faculdade e define a ordem da rota:

```python
coordenadas = {
    "UNEF": (-12.27415110131773, -38.933359218509345),
    "UNIFAN": (-12.248416984981803, -38.954434249711596),
    "UEFS": (-12.200186611506028, -38.97186855898357),
    "SENAI": (-12.23050281951723, -38.96934641511576),
    "QUADRIVIUM": (-12.251282176815081, -38.95890350671682),
    "INSTITUTO MIX": (-12.255552595513555, -38.96096778967345),
    "UNIRB": (-12.272706100429666, -38.93353845266053),
    "IFBA": (-12.289096911618342, -38.91357269338105)
}
```

### 4. Distribuicao nos veiculos

Com os grupos ordenados, o algoritmo percorre a lista e aloca cada faculdade no primeiro veiculo que ainda tenha capacidade suficiente:

```
Onibus 1 (48/50)
 - UEFS      | Ida: 13 | Volta: 11 | Total: 13
 - SENAI     | Ida:  4 | Volta:  3 | Total:  4
 - QUADRIVIUM| Ida:  8 | Volta:  7 | Total:  8

Van 1 (18/20)
 - UNIFAN    | Ida: 18 | Volta: 15 | Total: 18

Van 2 (1/15)
 - IFBA      | Ida:  1 | Volta:  1 | Total:  1
```

---

## Exemplo de Saida

```
===== DISTRIBUICAO DOS VEICULOS =====

Onibus 1 (48/50)
 - UEFS      | Ida: 13 | Volta: 11 | Total: 13
 - SENAI     | Ida:  4 | Volta:  3 | Total:  4

Van 1 (20/20)
 - UNIFAN    | Ida: 18 | Volta: 15 | Total: 20

Van 2 (1/15)
 - IFBA      | Ida:  1 | Volta:  1 | Total:  1
```

---

## Tecnologias Utilizadas

- **Python 3.x**
- `re` — expressoes regulares para parsing do texto
- `collections.defaultdict` — agrupamento dos dados por faculdade
- `math` — calculo de distancia entre coordenadas geograficas

Sem dependencias externas. Basta ter o Python instalado.

---

## Como Executar

```bash
# Clone o repositorio
https://github.com/Denvx/student_transport_planner.py.git

# Entre na pasta
cd aerj-rotas

# Execute o script
python rotas.py
```

Para usar com uma nova lista, substitua o conteudo da variavel `texto` no arquivo pelo texto atualizado da lista de transporte.

---

## Proximas Etapas

- Leitura automatica do texto via arquivo `.txt` ou entrada no terminal
- Calculo de rota otimizada com API de mapas
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
