# Projeto Final de Grafos + AVD — Grupo 2 (turma 5A)

Labirinto com chaves (grafo de estados) + comparação de BFS, DFS, Dijkstra e Bellman-Ford num dataset maior.
Teoria dos Grafos + Análise e Visualização de Dados, CESAR School, 2026.2.

## Integrantes

- João Victor Uchôa
- Luís Eduardo Bérard
- Caio Leimig
- Guilherme Burle
- Gabriel França

## Andamento

- [x] Checkpoint de 12/10: proposta do dataset da Parte 2 e apresentação (`docs/checkpoint_12-10/`)
- [ ] Parte 1: labirintos com chaves e portas (grafo de estados)
- [ ] Parte 2: rede de transferências entre clubes
- [ ] Entrega final (26/11/2026)

## Dataset da Parte 2

[Transfermarkt Datasets](https://github.com/dcaribou/transfermarkt-datasets), tabela `transfers`.

- Nó = clube; arco = clube de origem → clube de destino do jogador; peso = valor pago − valor de mercado (EUR).
- 4.739 nós e 31.626 arcos; 79,14% dos arcos têm peso negativo.
- Os CSVs brutos não vão para o repositório, por causa dos termos de uso do Transfermarkt. Vai só o script de download.

## Apresentação do checkpoint

Abra `docs/checkpoint_12-10/apresentacao/index.html` no navegador. As setas ← → passam os slides.

## Estrutura (a pedida no enunciado)

```
projeto-grafos-g2/
├─ README.md
├─ requirements.txt
├─ docs/                 # declaração e material do checkpoint
├─ data/
│  ├─ mapas/             # m01 a m08
│  ├─ mapas_grupo/       # os 2 mapas do grupo
│  └─ dataset_parte2/
├─ out/
│  ├─ parte1/
│  └─ parte2/
├─ src/
│  ├─ cli.py
│  ├─ solve.py
│  ├─ graphs/            # io.py, estados.py, graph.py, algorithms.py
│  └─ viz.py
└─ tests/
```

Por enquanto só existem este README e `docs/checkpoint_12-10/`. O resto entra conforme o projeto andar.

## Como executar

Precisa de Python 3.11+. Os comandos seguem o enunciado e passam a funcionar quando o `src/` estiver pronto:

```
python -m src.cli --mapa ./data/mapas/m03_tres_chaves.txt --alg BFS --out ./out/parte1/
python -m src.cli --mapa ./data/mapas/m06_fonte.txt --alg BELLMAN_FORD --fonte-consumivel --out ./out/parte1/
python -m src.cli --dataset ./data/dataset_parte2/ --benchmark --out ./out/parte2/
```
