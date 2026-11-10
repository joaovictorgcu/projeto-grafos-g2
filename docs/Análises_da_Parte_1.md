# Análises da Parte 1

Este documento resume as análises dos mapas, os resultados dos algoritmos e os arquivos gerados pelo projeto. Os resultados podem ser reproduzidos com:

```bash
PYTHONPATH=. python -m src.analise
```

## Modelo usado

O grafo de estados representa cada estado por:

```text
(posição, chaves coletadas, bônus consumidos)
```

Isso é necessário porque a mesma casa pode permitir movimentos diferentes dependendo das chaves e dos bônus já usados. `ALVO` é o nó virtual ligado à casa `G`.

## Mapas do grupo

### `data/mapas_grupo/mapa_chaves.txt`

O mapa tem as chaves `a`, `b` e `c`, a porta `A`, três casas de esteira `>>>` e um bônus `+`.

| Item | Resultado |
|---|---:|
| Estados alcançáveis | 976 |
| Arcos | 3.176 |
| Teto teórico | 1.024 |
| Ocupação do teto | 95,31% |
| BFS | 12 passos, custo 12 |
| Bellman-Ford | 12 passos, custo 12 |

O teto teórico é calculado por:

```text
casas livres × 2^(número de chaves) × 2^(número de bônus)
```

Dijkstra recusa esse grafo porque a primeira utilização do bônus gera um arco de peso negativo. Bellman-Ford é o algoritmo adequado para tratar essa situação.

### `data/mapas_grupo/mapa_armadilhas.txt`

A esteira `v` conduz a uma região inferior que pode ser alcançada a partir de `S`, mas não consegue voltar à saída.

| Item | Resultado |
|---|---:|
| Estados alcançáveis | 18 |
| Estados-armadilha | 12 |
| Proporção de armadilhas | 66,67% |
| Mínimo exigido | 20% |
| BFS até a saída | 5 passos, custo 5 |

Um estado-armadilha é alcançável a partir do início, mas não possui caminho até `ALVO`. Para encontrá-los, o algoritmo faz uma busca reversa a partir de `ALVO` e separa os estados que não aparecem nessa busca.

## Métricas dos grafos de estados

| Mapa | Estados | Arcos | Densidade | Teto | Ocupação |
|---|---:|---:|---:|---:|---:|
| m01 | 24 | 46 | 0,083333 | 24 | 100,00% |
| m02 | 39 | 74 | 0,049933 | 46 | 84,78% |
| m03 | 213 | 466 | 0,010320 | 608 | 35,03% |
| m04 | 37 | 66 | 0,049550 | 48 | 77,08% |
| m05 | 215 | 438 | 0,009520 | 352 | 61,08% |
| m06 | 24 | 46 | 0,083333 | 24 | 100,00% |
| m07 | 16 | 38 | 0,158333 | 62 | 25,81% |
| m08 | 2.919 | 6.364 | 0,000747 | 18.704 | 15,61% |

A densidade dirigida é calculada por:

```text
|E| / (|V| × (|V| − 1))
```

## Camadas, graus e modelagens

`out/parte1/camadas.json` agrupa os estados pelo conjunto de chaves coletadas. A mudança de camada acontece quando o jogador coleta uma chave.

Os arquivos `out/parte1/graus_*.csv` registram, para cada estado, o grau de entrada e o grau de saída.

`out/parte1/comparacao_modelagem.csv` compara três modelos nos mapas m02, m03 e m04:

1. portas tratadas como chão;
2. portas tratadas como parede;
3. grafo de estados.

Os dois primeiros modelos são simplificações: o primeiro pode liberar uma porta sem chave e o segundo pode impedir a passagem mesmo depois da coleta. O grafo de estados representa corretamente a dependência entre posição, chaves e bônus.

## Resultados dos algoritmos

Os resultados completos estão em `out/parte1/solucoes.csv`.

| Mapa | BFS | Dijkstra | Bellman-Ford |
|---|---|---|---|
| m01 | 10 passos, custo 30 | 14 passos, custo 20 | 14 passos, custo 20 |
| m02 | 34 passos, custo 46 | 34 passos, custo 46 | 34 passos, custo 46 |
| m03 | 87 passos, custo 119 | 91 passos, custo 99 | 91 passos, custo 99 |
| m04 | 20 passos, custo 36 | 20 passos, custo 36 | 20 passos, custo 36 |
| m05 | 12 passos, custo 18 | recusa peso negativo | 20 passos, custo 5 |
| m06 | 10 passos, custo 10 | recusa peso negativo | ciclo negativo de custo -1 |
| m07 | sem solução | sem solução | sem solução |
| m08 | 392 passos, custo 524 | 396 passos, custo 482 | 396 passos, custo 482 |

BFS minimiza a quantidade de passos. Dijkstra e Bellman-Ford minimizam o custo, por isso podem escolher caminhos mais longos e mais baratos.

## DFS, percurso e ciclo negativo

`out/parte1/dfs_classificacao.csv` classifica os arcos da DFS como árvore, retorno, avanço ou cruzamento. A classificação segue a ordem de vizinhança definida no projeto.

`out/parte1/percurso_m03.json` registra o percurso de menor custo do m03: 91 passos e custo 99.

`out/parte1/ciclo_negativo_m06.json` registra o ciclo de custo `-1` causado pela fonte reutilizável. Como a fonte pode ser visitada novamente, o desconto negativo pode ser repetido indefinidamente.

Os estados-armadilha dos mapas oficiais estão em:

```text
out/parte1/armadilhas_m04.csv
out/parte1/armadilhas_m07.csv
```

## Prova sobre o bônus do m05

No grafo de estados, o conjunto `B` de bônus consumidos nunca diminui. Ao entrar pela primeira vez em um bônus de índice `i`, o estado muda de:

```text
(posição, chaves, B)
```

para:

```text
(nova posição, novas chaves, B ∪ {i})
```

A primeira entrada pode ter custo negativo. Depois que `i` pertence a `B`, novas entradas no mesmo bônus têm custo normal. Portanto, para formar um ciclo no grafo de estados, o caminho precisaria retornar ao mesmo conjunto `B`; nesse retorno o bônus já estaria consumido e o desconto não poderia ser obtido novamente. O ciclo negativo criado pela reutilização do bônus no grafo de posições desaparece no grafo de estados.

Isso não vale para a fonte do m06, que é reutilizável no modelo padrão e continua produzindo custo negativo a cada visita.

## Arquivos gerados

Os principais arquivos da Parte 1 estão em `out/parte1/`:

- `metricas_global.json`;
- `camadas.json`;
- `graus_*.csv`;
- `comparacao_modelagem.csv`;
- `solucoes.csv`;
- `dfs_classificacao.csv`;
- `percurso_m03.json`;
- `ciclo_negativo_m06.json`;
- `armadilhas_m04.csv`;
- `armadilhas_m07.csv`.
