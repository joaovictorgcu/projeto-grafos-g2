# Projeto Final de Grafos + AVD — Grupo 2 (turma 5A)

Teoria dos Grafos + Análise e Visualização de Dados, CESAR School, 2026.2.

- **Parte 1:** labirinto com chaves e portas modelado como grafo de estados.
- **Parte 2:** rede de transferências entre clubes de futebol (Transfermarkt), com BFS, DFS, Dijkstra e
  Bellman-Ford comparados em corretude e desempenho, mais a análise exploratória e explanatória dos dados.

BFS, DFS, Dijkstra e Bellman-Ford são implementação própria (`src/graphs/algorithms.py`). Nenhuma
biblioteca de grafos é usada fora de `tests/`, onde o `networkx` entra só como oráculo.

## Sumário

- [Integrantes e pacotes](#integrantes-e-pacotes-de-trabalho)
- [Andamento](#andamento)
- [Instalação](#instalação)
- [Parte 1 — labirintos](#parte-1--labirintos)
- [Parte 2 — rede de transferências](#parte-2--rede-de-transferências)
- [Testes](#testes)
- [Estrutura do repositório](#estrutura-do-repositório)

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
  - [x] leitura e validação dos mapas, `G_pos` e `G_est`, `arestas_<mapa>.csv`
  - [x] figuras da Seção 8 e labirinto interativo (Streamlit)
  - [ ] `src/solve.py` (o `src/cli.py` já despacha `--mapa` para ele)
  - [ ] `metricas_global.json`, `camadas.json`, `graus_<mapa>.csv`, `comparacao_modelagem.csv`,
        `solucoes.csv`, `dfs_classificacao.csv`, `percurso_m03.json`, `ciclo_negativo_m06.json`,
        `armadilhas_m04.csv`, `armadilhas_m07.csv`
  - [ ] os 2 mapas do grupo em `data/mapas_grupo/`
- [x] Parte 2: rede de transferências entre clubes (`out/parte2/` e `docs/parte2/`)
- [ ] Declaração de Uso de IA assinada (`docs/DECLARACAO_IA.pdf`)
- [ ] PDF final (manual + técnica, com a matriz de contribuição)
- [ ] Entrega final (26/11/2026)

## Instalação

Precisa de Python 3.11+.

```
python -m venv .venv
.venv\Scripts\activate        # Windows
source .venv/bin/activate     # Linux e macOS
pip install -r requirements.txt
```

Todos os comandos abaixo rodam a partir da raiz do repositório.

## Parte 1 — labirintos

Os mapas ficam em `data/mapas/` (fornecidos) e `data/mapas_grupo/` (do grupo).

### O que já funciona

```
# arestas_<mapa>.csv de todos os mapas
python -m src.graphs.estados --out ./out/parte1/

# figuras da Seção 8
python -m src.viz --mapa ./data/mapas/m03_tres_chaves.txt --png ./out/parte1/percurso_m03.png
python -m src.viz --mapa ./data/mapas/m08_grande.txt --png ./out/parte1/percurso_m08.png
python -m src.viz --mapa ./data/mapas/m02_uma_chave.txt --camadas ./out/parte1/camadas_m02.png
python -m src.viz --mapa ./data/mapas/m02_uma_chave.txt --arvore-bfs ./out/parte1/arvore_bfs_m02.png
python -m src.viz --mapa ./data/mapas/m08_grande.txt --multiplicidade ./out/parte1/multiplicidade_m08.png
```

### Labirinto interativo

Feito em Streamlit; abre no navegador:

```
streamlit run src/interativo.py
streamlit run src/interativo.py -- --mapa ./data/mapas/m03_tres_chaves.txt
```

Na barra lateral escolhe-se o mapa (ou envia-se um `.txt`, como o mapa surpresa), o algoritmo
(BFS, Dijkstra ou Bellman-Ford), a camada em destaque e a velocidade. A animação mostra posição,
chaves, bônus consumidos e custo acumulado a cada passo; os estados-armadilha ficam marcados e,
embaixo, há a comparação dos três algoritmos no mesmo mapa.

### Comandos do enunciado (dependem do `src/solve.py`)

```
python -m src.cli --mapa ./data/mapas/m03_tres_chaves.txt --alg BFS --out ./out/parte1/
python -m src.cli --mapa ./data/mapas/m03_tres_chaves.txt --alg DIJKSTRA --out ./out/parte1/
python -m src.cli --mapa ./data/mapas/m05_bonus.txt --alg BELLMAN_FORD --out ./out/parte1/
python -m src.cli --mapa ./data/mapas/m06_fonte.txt --alg BELLMAN_FORD --fonte-consumivel --out ./out/parte1/
python -m src.cli --mapa ./data/mapas/m04_esteiras.txt --armadilhas --out ./out/parte1/
python -m src.cli --mapa ./data/mapas/m03_tres_chaves.txt --interactive --out ./out/parte1/
```

O `src/cli.py` repassa os argumentos para `solve.executar(args)`. Enquanto o `solve.py` não existe,
esses comandos param com a mensagem "a Parte 1 ainda não está ligada ao cli".

## Parte 2 — rede de transferências

### O dataset

[Transfermarkt Datasets](https://github.com/dcaribou/transfermarkt-datasets) (mantido por dcaribou,
licença CC0-1.0), tabela `transfers`, snapshot de 05/09/2026 com dados até 06/07/2026.

| | |
|---|---|
| Nó | clube (`club_id`), sem os 6 pseudo-clubes (Without Club, Unknown, Retired, Career break, Ban, Own Youth) |
| Arco | clube de origem → clube de destino do jogador |
| Peso | soma, em EUR, de valor pago − valor de mercado das transferências do par |
| Tamanho | 4.739 nós e 31.626 arcos; 79,14% dos arcos têm peso negativo |
| Grafo temporal | nó = (clube, temporada): 21.703 nós e 52.290 arcos, sem ciclos (usado no Bellman-Ford sem ciclo negativo e no Dijkstra com repesagem de Johnson) |

**Recorte** (`src/graphs/dataset.py`): datas até 06/07/2026; valor pago e valor de mercado
conhecidos; sem pseudo-clubes; sem self-loops; sem empréstimos (fee = 0 num vai-e-volta consecutivo
do mesmo jogador, marcado sobre o histórico completo). 175.165 transferências brutas viram 36.442
usadas.

**Pergunta de pesquisa:** em uma rede de transferências entre clubes, como os valores pagos em
relação ao valor de mercado dos jogadores influenciam os caminhos do grafo e quais relações podem
ser identificadas pelos algoritmos de caminhos mínimos e ciclos negativos?

### 1. Baixar o snapshot

Os CSVs brutos não vão para o repositório, por causa dos termos de uso do Transfermarkt. O script
baixa os 3 arquivos (`transfers`, `players` e `clubs`, 10,3 MB em `.csv.gz`) para
`data/dataset_parte2/`, confere o SHA-256 de cada um e imprime a ficha do grafo:

```
python scripts/ficha_transfermarkt.py --baixar
```

No Windows, `scripts/rodar_fichas.bat` faz o mesmo com duplo clique. A ficha vai para
`out/parte2/ficha_dataset.json`.

### 2. Rodar os experimentos

```
# um algoritmo, entre dois clubes (nome como no Transfermarkt, ou o club_id)
python -m src.cli --dataset ./data/dataset_parte2/ --alg DIJKSTRA --source Santos --target PSG --out ./out/parte2/
python -m src.cli --dataset ./data/dataset_parte2/ --alg BFS --source Benfica --out ./out/parte2/
python -m src.cli --dataset ./data/dataset_parte2/ --alg DFS --source "Real Madrid" --out ./out/parte2/
python -m src.cli --dataset ./data/dataset_parte2/ --alg BELLMAN_FORD --source "Real Madrid" --out ./out/parte2/

# tudo: BFS/DFS de 3 fontes, Dijkstra em 6 pares, Bellman-Ford com e sem ciclo negativo,
# desempenho (5 execuções) e escalabilidade (10%, 25%, 50%, 75% e 100% dos nós)
python -m src.cli --dataset ./data/dataset_parte2/ --benchmark --out ./out/parte2/
```

O `--benchmark` leva cerca de 4 minutos: o Bellman-Ford no grafo completo faz as |V| − 1 passadas
(o ciclo negativo impede a parada antecipada), uns 20 s por execução. `--repeticoes` e `--tamanhos`
mudam os parâmetros.

### 3. Análise exploratória e gráficos

```
python -m src.avd_parte2 --dataset ./data/dataset_parte2/ --out ./out/parte2/
python -m src.viz_parte2 --dataset ./data/dataset_parte2/ --out ./out/parte2/
```

O `viz_parte2` lê o `parte2_report.json`, então rode o `--benchmark` antes.

### Saídas em `out/parte2/`

| Arquivo | Conteúdo |
|---|---|
| `parte2_report.json` | resultados de todos os algoritmos, desempenho e escalabilidade |
| `desempenho.csv` | a tabela de desempenho em CSV |
| `eda_resumo.json` | estrutura, faltantes, distribuições, relações e outliers do dataset |
| `ficha_dataset.json` | funil do recorte e números do grafo |
| `e1_graus.png` … `e5_outliers.png` | visualizações exploratórias |
| `x1_explanatoria_caminho.png`, `x2_explanatoria_ligas.png` | visualizações explanatórias |
| `a1_tempos.png`, `a2_escalabilidade.png`, `a3_camadas_bfs.png`, `a4_caminhos.png` | comparação dos algoritmos: tempo, comportamento e caminhos |

A interpretação dos resultados e as notas analíticas de cada gráfico estão em
`docs/parte2/relatorio_parte2.md`.

## Testes

```
pytest
```

Os testes da Parte 2 (`test_dataset.py`, `test_parte2.py`) usam dados sintéticos e não precisam do
snapshot baixado.

## Estrutura do repositório

```
projeto-grafos-g2/
├─ README.md
├─ requirements.txt
├─ docs/
│  ├─ checkpoint_12-10/   # proposta do dataset e apresentação do checkpoint
│  └─ parte2/             # relatório e notas analíticas da Parte 2
├─ data/
│  ├─ mapas/              # m01 a m08
│  ├─ mapas_grupo/        # os 2 mapas do grupo
│  └─ dataset_parte2/     # snapshot do Transfermarkt (baixado pelo script, fora do git)
├─ out/
│  ├─ parte1/
│  └─ parte2/
├─ scripts/
│  ├─ ficha_transfermarkt.py   # download + ficha do dataset
│  └─ rodar_fichas.bat
├─ src/
│  ├─ cli.py              # linha de comando das duas partes
│  ├─ interativo.py       # labirinto interativo (Streamlit)
│  ├─ viz.py              # figuras da Parte 1
│  ├─ parte2.py           # experimentos da Parte 2
│  ├─ avd_parte2.py       # análise exploratória da Parte 2
│  ├─ viz_parte2.py       # gráficos da Parte 2
│  └─ graphs/
│     ├─ io.py            # leitura/validação dos mapas e do dataset
│     ├─ dataset.py       # recorte do Transfermarkt e grafos da Parte 2
│     ├─ estados.py       # grafo de posições e grafo de estados
│     ├─ graph.py         # lista de adjacência dirigida
│     └─ algorithms.py    # BFS, DFS, Dijkstra, Bellman-Ford
└─ tests/
```

## Apresentação do checkpoint

Abra `docs/checkpoint_12-10/apresentacao/index.html` no navegador. As setas ← → passam os slides.
