# Discussão da Parte 1

## m01 — diferença entre passos e custo

No m01, o BFS encontra o caminho com menos movimentos: 10 passos e custo 30. Dijkstra e Bellman-Ford encontram um caminho de 14 passos e custo 20.

A diferença ocorre porque BFS minimiza a quantidade de movimentos, enquanto Dijkstra e Bellman-Ford minimizam a soma dos pesos. Assim, um caminho mais longo pode ser melhor quando evita água e lama.

## m06 — fonte reutilizável

A fonte `*` custa `-2` cada vez que é visitada. No modelo padrão, o estado não registra que a fonte foi usada. O jogador pode voltar a ela e repetir o desconto, formando um ciclo negativo de custo `-1`.

Por isso, Bellman-Ford informa que não existe menor custo bem definido: repetindo o ciclo, o custo continua diminuindo. A opção `--fonte-consumivel` altera o estado para registrar o uso da fonte e elimina essa repetição.

## m07 — ausência de solução

No m07, a porta `A` bloqueia o corredor até a saída. A chave `a` fica em uma região que não pode ser alcançada sem atravessar a própria porta. Nenhum estado alcançável possui a chave necessária, então BFS, Dijkstra e Bellman-Ford registram `SEM_SOLUCAO`.

## Mapa com chaves, esteiras e bônus

O arquivo `data/mapas_grupo/mapa_chaves.txt` contém as chaves `a`, `b` e `c`, três esteiras, a porta `A` e um bônus `+`.

O grafo possui 976 estados alcançáveis e 3.176 arcos. BFS encontra a saída em 12 passos e custo 12. Bellman-Ford encontra o mesmo resultado. Dijkstra recusa o grafo porque a primeira utilização do bônus gera um peso negativo.

## Mapa com estados-armadilha

O arquivo `data/mapas_grupo/mapa_armadilhas.txt` usa a esteira `v` para levar o jogador a uma região sem retorno à saída.

São 18 estados alcançáveis, dos quais 12 são estados-armadilha. Isso corresponde a 66,67%, acima do mínimo de 20% exigido. O caminho normal até a saída tem 5 passos e custo 5.

## Gabarito dos mapas do grupo

Para cada mapa, o gabarito pode ser conferido nos arquivos de saída:

- estados e graus: `out/parte1/graus_mapa_chaves.csv` e `out/parte1/graus_mapa_armadilhas.csv`;
- soluções dos algoritmos: `out/parte1/solucoes.csv`;
- métricas: `out/parte1/metricas_global.json`;
- camadas de chaves: `out/parte1/camadas.json`.
