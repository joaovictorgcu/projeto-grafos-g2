# P3 — Análises da Parte 1

Responsável: Guilherme Burle. Os artefatos numéricos são reproduzidos por `PYTHONPATH=. python -m src.analise`.

## Discussões para o relatório

### m01 — BFS e Dijkstra divergem

No m01, o BFS minimiza a quantidade de movimentos e encontra um caminho de 10 passos. O Dijkstra minimiza o custo acumulado das casas de destino e encontra um caminho de 14 passos com custo 20, enquanto o caminho do BFS custa 30. Isso ocorre porque a travessia de água (`~`) custa 5 e a travessia de lama (`,`) custa 3: menos passos não implica menor custo. A divergência é, portanto, uma consequência esperada de as duas buscas otimizarem funções objetivo diferentes.

### m06 — fonte reutilizável e ciclo negativo

A fonte `*` custa −2 cada vez que é visitada. Como o modelo padrão não registra fontes consumidas, é possível voltar à fonte e repetir o desconto indefinidamente. O Bellman-Ford registra o ciclo exibido em `out/parte1/ciclo_negativo_m06.json`, com custo negativo. Nesse caso não existe menor caminho bem definido: cada volta reduz ainda mais o custo. A opção `--fonte-consumivel` corrige o exploit ao incluir a fonte no conjunto de recursos consumidos do estado.

### m07 — sem solução

O m07 possui uma porta `A` que bloqueia o único corredor entre o início e a saída. A chave `a` está em uma região que só pode ser alcançada atravessando a própria barreira, portanto nenhum estado alcançável contém a chave necessária para abrir a passagem. Os três algoritmos de caminho registram `SEM_SOLUCAO` em `solucoes.csv`.

## Mapas do grupo e gabarito

### `guilherme_03_chaves.txt`

Mapa com as chaves `a`, `b` e `c`, uma porta `A`, três casas de esteira `>>>` e um bônus `+`. O estado inicial é `(1,1)|-|{}`. A saída é alcançada; o pipeline registra 1.000 estados alcançáveis, 12 passos no caminho BFS e custo 12 no caminho de Bellman-Ford. A presença de três chaves e de um bônus faz o espaço potencial ser maior que o conjunto explorado, evidenciando que o grafo de estados é construído por alcance.

### `guilherme_armadilhas.txt`

A esteira `v` conduz a uma ramificação inferior que não retorna à saída. O mapa possui 18 estados alcançáveis e 12 estados-armadilha, isto é, 66,7% dos estados, acima do mínimo de 20%. O estado `(2,5)|-|{}` é a entrada da ramificação e os estados seguintes permanecem sem caminho até `ALVO`.

## Prova do m05 — preencher pelo responsável

> Esta seção é intencionalmente deixada para a redação autoral de Guilherme, conforme o enunciado. Use como ponto de partida a invariável solicitada: ao longo de um caminho no grafo de estados, o conjunto de bônus consumidos só cresce; ele nunca volta a um estado anterior com um bônus ainda não consumido. Complete aqui a prova formal e a explicação do desaparecimento do ciclo negativo.
