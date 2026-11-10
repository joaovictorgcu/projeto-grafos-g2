# P3 — Análises da Parte 1: entrega final de Guilherme Burle

## 1. Escopo

Este documento reúne a parte textual final do pacote P3. Os dados numéricos citados aqui são os que estão nos arquivos de `out/parte1/` gerados pelo comando:

```bash
PYTHONPATH=. python -m src.analise
```

O P3 analisa os oito mapas oficiais e os dois mapas próprios do grupo. O grafo usado pelos algoritmos é o grafo de estados, cujo vértice registra:

```text
(posição, conjunto de chaves, conjunto de bônus consumidos)
```

O nó virtual `ALVO` representa o término da partida depois da entrada em `G`.

---

## 2. Mapas próprios do grupo

### 2.1 Mapa com três chaves, esteiras e bônus

Arquivo: `data/mapas_grupo/mapa_chaves.txt`.

O mapa contém as chaves `a`, `b` e `c`, a porta `A`, três casas de esteira `>>>` e um bônus `+`. O caminho até a saída é possível. Como a posição pode ser visitada com diferentes conjuntos de chaves e de bônus consumidos, uma mesma casa física pode originar vários estados distintos.

O resultado calculado foi:

| Propriedade | Resultado |
|---|---:|
| Chaves | 3 (`a`, `b`, `c`) |
| Esteiras | 3 |
| Bônus | 1 |
| Estados alcançáveis | 976 |
| Arcos do grafo de estados | 3.176 |
| Teto teórico | 1.024 |
| Ocupação do teto | 95,31% |
| Caminho BFS | 12 passos, custo 12 |
| Bellman-Ford | 12 passos, custo 12 |

O teto teórico é uma referência combinatória. A fórmula usada é:

```text
casas_livres × 2^(número de chaves) × 2^(número de bônus)
```

A exploração é feita a partir do início; portanto, somente estados realmente alcançáveis são registrados.

Dijkstra recusa esse mapa porque o bônus produz um arco de peso negativo. Isso é comportamento correto do algoritmo, não falha da modelagem.

### 2.2 Mapa com estados-armadilha

Arquivo: `data/mapas_grupo/mapa_armadilhas.txt`.

Nesse mapa, a esteira `v` leva o jogador a uma região inferior sem caminho de retorno até a saída. A região é alcançável a partir de `S`, mas seus estados não conseguem chegar a `ALVO`.

O resultado foi:

| Propriedade | Resultado |
|---|---:|
| Estados alcançáveis | 18 |
| Estados-armadilha | 12 |
| Proporção de armadilhas | 66,67% |
| Mínimo exigido | 20% |
| Caminho BFS até a saída | 5 passos |
| Custo do caminho | 5 |

O mapa cumpre o requisito porque 12 dos 18 estados alcançáveis são armadilhas.

A identificação é feita no grafo transposto: uma BFS parte de `ALVO` e descobre quais estados conseguem chegar à saída no grafo original. Os estados alcançáveis que não aparecem nessa busca reversa são classificados como armadilhas.

---

## 3. Métricas globais

O arquivo `out/parte1/metricas_global.json` contém a ordem, o tamanho, a densidade, o teto teórico e a ocupação de `G_pos` e `G_est`.

A densidade dirigida é calculada como:

```text
|E| / (|V| × (|V| − 1))
```

No `G_pos`, um nó representa somente uma casa livre. No `G_est`, um nó representa a casa e o histórico relevante de chaves e bônus.

Os números do grafo de estados foram:

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

O m08 demonstra o efeito do tamanho do mapa: mesmo com quatro chaves, somente 2.919 estados foram alcançados, enquanto o teto combinatório seria 18.704.

---

## 4. Camadas de chaves

O arquivo `out/parte1/camadas.json` agrupa os estados de acordo com o conjunto de chaves já coletadas.

A camada `-` representa nenhum conjunto de chaves. As camadas `a`, `ab` e `abc`, por exemplo, representam estados que possuem exatamente esses conjuntos de chaves.

A mudança de camada acontece quando um arco chega a uma chave ainda não coletada. O estado de destino fica em uma camada nova porque a chave passa a fazer parte do histórico do jogador.

As métricas por camada registram:

- número de estados;
- número de arcos internos;
- grau de saída médio;
- quantidade de arcos entre camadas.

Essa organização é importante porque portas e caminhos podem ficar disponíveis somente depois da mudança de camada.

---

## 5. Graus de entrada e saída

Os arquivos `out/parte1/graus_*.csv` registram, para cada estado:

- `grau_entrada`: número de arcos que chegam ao estado;
- `grau_saida`: número de arcos que partem do estado.

Um estado com grau de saída zero pode ser um beco ou uma posição em que as regras de esteira impedem qualquer continuação. Um estado com grau de entrada alto pode ser alcançado por diferentes trajetórias.

Foram gerados arquivos para os oito mapas oficiais e para os dois mapas do grupo.

---

## 6. Comparação entre modelagens

O arquivo `out/parte1/comparacao_modelagem.csv` compara, nos mapas m02, m03 e m04:

1. portas tratadas como chão;
2. portas tratadas como parede;
3. grafo de estados.

A modelagem “portas como chão” é permissiva demais: ela pode permitir que um caminho atravesse uma porta sem ter a chave. A modelagem “portas como parede” é restritiva demais: ela remove a casa da porta mesmo depois que a chave poderia ser coletada.

O grafo de estados é o modelo correto porque a possibilidade de atravessar a porta depende do conjunto de chaves do estado atual.

A mesma ideia vale para bônus: o custo da casa depende de o bônus já ter sido consumido, algo que não pode ser representado por uma casa isolada.

---

## 7. Resultados dos algoritmos

O arquivo `out/parte1/solucoes.csv` registra BFS, Dijkstra e Bellman-Ford.

### 7.1 m01

- BFS: 10 passos, custo 30.
- Dijkstra: 14 passos, custo 20.
- Bellman-Ford: 14 passos, custo 20.

A diferença ocorre porque BFS minimiza passos, enquanto Dijkstra e Bellman-Ford minimizam custo. O caminho mais curto em quantidade de movimentos atravessa terrenos mais caros.

### 7.2 m02

Os três algoritmos encontram caminho com 34 passos e custo 46. Como os pesos são positivos e não há alternativa de menor custo, os resultados coincidem.

### 7.3 m03

- BFS: 87 passos, custo 119.
- Dijkstra: 91 passos, custo 99.
- Bellman-Ford: 91 passos, custo 99.

BFS encontra menos movimentos, mas o caminho de menor custo precisa aceitar mais passos para evitar terrenos caros.

### 7.4 m04

Os três algoritmos encontram caminho com 20 passos e custo 36. As esteiras restringem os movimentos, mas não introduzem pesos negativos.

### 7.5 m05

- BFS: 12 passos, custo 18.
- Dijkstra: recusa o grafo por encontrar arco de peso `-4`.
- Bellman-Ford: 20 passos, custo 5.

O bônus é negativo na primeira utilização, mas o estado registra que ele já foi consumido. Por isso, o grafo de estados não possui o ciclo negativo causado por tratar o bônus como desconto permanente.

### 7.6 m06

- BFS: 10 passos, custo 10.
- Dijkstra: recusa o grafo por encontrar arco de peso `-2`.
- Bellman-Ford: detecta ciclo negativo de custo `-1`.

O BFS ainda pode responder a pergunta de quantidade de passos. O menor custo, entretanto, não é bem definido no modelo com fonte reutilizável.

### 7.7 m07

BFS, Dijkstra e Bellman-Ford registram `SEM_SOLUCAO`. A chave necessária não pode ser obtida de maneira que abra a passagem até a saída.

### 7.8 m08

- BFS: 392 passos, custo 524.
- Dijkstra: 396 passos, custo 482.
- Bellman-Ford: 396 passos, custo 482.

A diferença entre BFS e os algoritmos de custo mostra novamente que menos movimentos não significa menor soma de pesos.

---

## 8. Classificação da DFS

O arquivo `out/parte1/dfs_classificacao.csv` classifica os arcos encontrados pela DFS como:

- **árvore**: arco que descobre um estado branco;
- **retorno**: arco que aponta para um estado cinza, ainda ativo na pilha;
- **avanço**: arco para um descendente já descoberto;
- **cruzamento**: arco que liga ramos diferentes ou estados já finalizados.

A classificação depende da ordem N, L, S, O exigida pelo enunciado. Alterar essa ordem pode alterar a árvore de DFS e a classificação de alguns arcos.

---

## 9. Percurso do m03

O arquivo `out/parte1/percurso_m03.json` registra o percurso de menor custo encontrado por Bellman-Ford.

O resultado é:

- status: `OK`;
- passos: 91;
- custo: 99.

O caminho passa por diferentes conjuntos de chaves. Ele começa sem chaves, coleta as chaves obrigatórias e termina em uma posição próxima da saída, respeitando as portas e as regras do mapa.

---

## 10. Ciclo negativo do m06

O arquivo `out/parte1/ciclo_negativo_m06.json` registra o ciclo:

```text
(3,5)|-|{}
(3,6)|-|{}
(3,5)|-|{}
```

O custo total é `-1`.

A interpretação é que o jogador entra e sai da fonte reutilizável, recebe novamente o custo negativo e volta ao mesmo estado. Repetindo o ciclo, o custo continua diminuindo.

---

## 11. Estados-armadilha dos mapas oficiais

Foram gerados:

- `out/parte1/armadilhas_m04.csv`;
- `out/parte1/armadilhas_m07.csv`.

O m04 possui 4 estados-armadilha. O m07 possui 16 estados-armadilha.

Um estado-armadilha não é necessariamente um estado inacessível. Ele é alcançável a partir do início, mas não possui caminho até `ALVO`.

---

## 12. Prova do m05: o ciclo negativo desaparece no grafo de estados

No grafo de posições, a casa de bônus `+` pode ser tratada como se tivesse custo `-4` em todas as entradas. Se houver um caminho que chega ao bônus e retorna à mesma região, a modelagem de posições permite repetir esse desconto. Uma ida e volta pelo bônus pode então produzir uma soma negativa repetida indefinidamente.

No grafo de estados, entretanto, o estado não é apenas a posição. Ele também contém o conjunto `B` de bônus já consumidos.

Considere uma transição que entra em um bônus ainda não consumido. Se o bônus tiver índice `i`, a transição altera o estado de:

```text
(p, K, B)
```

para:

```text
(p', K', B ∪ {i})
```

O custo dessa primeira entrada pode ser `-4`. Em qualquer entrada posterior no mesmo bônus, como `i` já pertence a `B`, o custo passa a ser `1`.

A propriedade fundamental é:

```text
B nunca diminui ao longo de um caminho.
```

A cada consumo, `B` permanece igual ou recebe um novo índice. Nunca existe transição que remova um bônus de `B`.

Suponha, por contradição, que exista no grafo de estados um ciclo negativo que reutilize o bônus. Para ser um ciclo, o caminho deve retornar ao mesmo estado completo, incluindo a posição, as chaves e o conjunto `B`. Se o caminho consumir o bônus durante a primeira volta, o estado que aparece depois do consumo terá `i ∈ B`. Como `B` não diminui, nenhuma volta posterior pode retornar ao mesmo estado anterior com `i ∉ B`. Logo, o desconto `-4` não pode ser obtido repetidamente no mesmo ciclo de estados.

Se o ciclo não consumir o bônus, então ele não recebe o custo `-4` associado à primeira utilização. Nesse caso, os arcos desse ciclo têm os custos normais e não formam o ciclo negativo do grafo de posições.

Portanto, o ciclo negativo criado pela modelagem de posições não existe no grafo de estados do m05. O histórico do consumo faz com que o bônus seja uma fonte finita de desconto. O grafo de estados representa corretamente essa regra porque distingue, por exemplo:

```text
(posição, chaves, {})
```

de:

```text
(posição, chaves, {0})
```

Embora os dois estados estejam na mesma casa física, eles não têm o mesmo futuro de custos. Depois que o bônus foi usado, o desconto não pode ser repetido.

Essa prova não se aplica ao m06 no modelo padrão porque a fonte `*` foi definida como reutilizável. No m06, a visita repetida à fonte continua custando `-2`, o que permite um ciclo negativo real. A opção `--fonte-consumivel` modifica o estado para registrar a fonte consumida e elimina esse exploit.

---

## 13. Conclusão do P3

O P3 entrega os mapas próprios, as métricas dos grafos, as métricas por camadas, os graus dos estados, a comparação das modelagens, os resultados dos algoritmos, a classificação da DFS, o percurso do m03, o ciclo negativo do m06, os estados-armadilha dos mapas oficiais e os gabaritos dos mapas próprios.

Os artefatos numéricos estão em `out/parte1/`. Este documento fornece a explicação textual completa para integração no PDF técnico final do grupo.

A suíte de testes do projeto foi executada com sucesso:

```text
1079 passed
```
