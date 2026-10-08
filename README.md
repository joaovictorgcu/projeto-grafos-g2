# Projeto Final de Grafos + AVD — Grupo 2 (turma 5A)

Labirinto com chaves (grafo de estados) + comparação de BFS, DFS, Dijkstra e Bellman-Ford num dataset maior.
Teoria dos Grafos + Análise e Visualização de Dados, CESAR School, 2026.2.

## Integrantes e pacotes de trabalho

Cada pacote tem um dono e um revisor. A revisão é em anel: cada um revisa o pacote do seguinte,
e revisar significa commitar alguma coisa lá — um teste, uma correção, uma documentação.

| Integrante | Pacote | Revisa |
|---|---|---|
| Gabriel França | **P1** — modelagem e grafo de estados | P2 |
| Luís Eduardo Bérard | **P2** — algoritmos e testes | P3 |
| Guilherme Burle | **P3** — análises da Parte 1 | P4 |
| João Victor Uchôa | **P4** — Parte 2: dados e experimentos | P5 |
| Caio Leimig | **P5** — visualização e comunicação | P1 |

## Andamento

- [x] Checkpoint de 12/10: proposta do dataset da Parte 2 e apresentação (`docs/checkpoint_12-10/`)
- [x] Mapas fornecidos (m01 a m08) em `data/mapas/`
- [ ] Parte 1: labirintos com chaves e portas (grafo de estados)
- [ ] Parte 2: rede de transferências entre clubes
- [ ] Declaração de Uso de IA assinada (`docs/DECLARACAO_IA.pdf`)
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
├─ docs/
│  ├─ DECLARACAO_IA.pdf  # declaração de uso de IA assinada por todos
│  └─ checkpoint_12-10/  # material do checkpoint
├─ data/
│  ├─ mapas/             # m01 a m08
│  ├─ mapas_grupo/       # os 2 mapas do grupo
│  └─ dataset_parte2/    # dataset maior (Parte 2)
├─ out/
│  ├─ parte1/
│  └─ parte2/
├─ scripts/              # download e ficha do dataset da Parte 2
├─ src/
│  ├─ cli.py
│  ├─ solve.py
│  ├─ graphs/
│  │  ├─ io.py           # ler/validar os mapas e o dataset
│  │  ├─ estados.py      # grafo de posições e grafo de estados
│  │  ├─ graph.py        # lista de adjacência DIRIGIDA
│  │  └─ algorithms.py   # BFS, DFS, Dijkstra, Bellman-Ford (próprios)
│  └─ viz.py             # visualizações/UX
└─ tests/
   ├─ test_bfs.py
   ├─ test_dfs.py
   ├─ test_dijkstra.py
   ├─ test_bellman_ford.py
   ├─ test_estados.py
   └─ test_io.py
```

Hoje existem o README, `docs/checkpoint_12-10/` e `data/mapas/`. O resto entra conforme o projeto andar.

## Instalação

Precisa de Python 3.11+.

```
python -m venv .venv
.venv\Scripts\activate        # Windows
source .venv/bin/activate     # Linux e macOS
pip install -r requirements.txt
```

Os algoritmos (BFS, DFS, Dijkstra e Bellman-Ford) são implementação própria: nenhuma
biblioteca de grafos é usada fora de `tests/`, onde `networkx` entra só como oráculo
para conferir os resultados.

## Como executar

Os comandos seguem o enunciado e passam a funcionar quando o `src/` estiver pronto:

```
python -m src.cli --mapa ./data/mapas/m03_tres_chaves.txt --alg BFS --out ./out/parte1/
python -m src.cli --mapa ./data/mapas/m03_tres_chaves.txt --alg DIJKSTRA --out ./out/parte1/
python -m src.cli --mapa ./data/mapas/m05_bonus.txt --alg BELLMAN_FORD --out ./out/parte1/
python -m src.cli --mapa ./data/mapas/m06_fonte.txt --alg BELLMAN_FORD --fonte-consumivel --out ./out/parte1/
python -m src.cli --mapa ./data/mapas/m04_esteiras.txt --armadilhas --out ./out/parte1/
python -m src.cli --mapa ./data/mapas/m03_tres_chaves.txt --interactive --out ./out/parte1/

python -m src.cli --dataset ./data/dataset_parte2/ --alg DIJKSTRA --source A --target Z --out ./out/parte2/
python -m src.cli --dataset ./data/dataset_parte2/ --benchmark --out ./out/parte2/
```

## Testes

```
pytest
```
