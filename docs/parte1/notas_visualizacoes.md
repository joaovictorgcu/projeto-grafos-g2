# Parte 1 — Notas analíticas das visualizações

> [IA] Claude Code (Claude Opus 5.5) – "O que mostra" e rascunho de "Insight" e "Por que esse gráfico";
> revisado por Caio.

Mesmo formato da seção 6 de `docs/parte2/relatorio_parte2.md`. Rótulos de estado seguem o formato
`(linha,coluna)|chaves|{bônus}`. Fontes dos números: `src/viz.py`, `out/parte1/metricas_global.json`,
`out/parte1/camadas.json`, `out/parte1/solucoes.csv` e `out/parte1/percurso_m03.json`.

## `percurso_m03.png` (mapa m03_tres_chaves)

**O que mostra.** O percurso de menor custo do Dijkstra desenhado sobre a grade do mapa, com a cor
mudando a cada chave coletada. São 91 passos e custo 99, divididos em 4 trechos:

| Camada | Passos | Termina em |
|---|---|---|
| sem chaves | 7 | pega a em (8,1) |
| {a} | 18 | pega b em (1,12) |
| {a,b} | 43 | pega c em (6,6) |
| {a,b,c} | 23 | chegada em G |

A legenda identifica as camadas, início, chave coletada, chegada, parede, água (custo 5) e lama
(custo 3).

Números de apoio: a BFS chega em 87 passos com custo 119, e o Bellman-Ford dá os mesmos 91 passos e
custo 99 do Dijkstra. O grafo de estados tem 213 estados e 466 arcos, com 35,0% de ocupação do teto
teórico de 608 estados.

**Insight.** A figura mostra como o percurso evita o terreno caro: na sala de c, ele sobe pela linha
3 em vez de cruzar a água da linha 4, tanto na ida quanto na volta. A água que ele paga é a casa
(8,9), atravessada nos trechos {a,b} e {a,b,c}, porque ela fica no corredor da linha 8, sem desvio.
A figura também mostra que quem define o trajeto são as chaves, e não a posição de G: a linha passa
mais de uma vez pelos mesmos corredores sem repetir estado, porque cada passagem acontece em outra
camada, e o trecho mais longo é o de {a,b}, com 43 passos até c.

**Por que esse gráfico.** Desenhar sobre a grade deixa o percurso junto do que o explica (paredes,
portas e terreno), o que se perde numa lista de 91 estados ou num desenho abstrato do grafo de 213
estados. A cor por camada separa as passagens pela mesma casa: com uma cor só, as idas e voltas
virariam uma linha só e a ordem delas se perderia. A cor é categórica, um tom por conjunto de
chaves, e os passos de cada trecho ficam na legenda.

## `percurso_m08.png` (mapa m08_grande)

**O que mostra.** O mesmo tipo de figura no maior mapa fornecido: percurso de menor custo do
Dijkstra, com 396 passos e custo 482, divididos em 5 trechos:

| Camada | Passos | Termina em |
|---|---|---|
| sem chaves | 46 | pega a em (27,5) |
| {a} | 90 | pega b em (3,23) |
| {a,b} | 52 | pega c em (5,37) |
| {a,b,c} | 106 | pega d em (3,29) |
| {a,b,c,d} | 102 | chegada em G |

Números de apoio: a BFS chega em 392 passos com custo 524, e o Bellman-Ford dá os mesmos 396 passos
e custo 482. O mapa tem 1.169 casas livres, 4 chaves e nenhum bônus. O grafo de estados tem 2.919
estados e 6.364 arcos, com 15,6% de ocupação do teto teórico de 18.704 estados.

**Insight.** Com o mapa maior, a distância na grade diz pouco sobre a distância no percurso: b e d
estão na linha 3, nas colunas 23 e 29, mas ficam a 158 passos uma da outra (52 + 106), porque c vem
no meio. No m03 a linha repetia a maior parte dos corredores; aqui a repetição se concentra no
miolo do mapa, onde o trecho {a,b,c} chega até d e o trecho {a,b,c,d} volta pelo mesmo caminho. A
ocupação cai de 35,0% para 15,6% porque cada chave a mais dobra o teto, mas aqui acrescenta só uma
camada: as chaves só são coletadas na ordem a, b, c, d.

**Por que esse gráfico.** Repetir a forma do m03 permite comparar os dois mapas sem mudar a leitura:
a grade, a cor por camada e os passos na legenda são os mesmos, com uma cor a mais para a quarta
chave. A forma continua funcionando porque o percurso segue sendo uma linha só, enquanto um desenho
do grafo com 2.919 estados e 6.364 arcos ficaria ilegível. A desvantagem é a linha mais fina, que pede
mais atenção nos trechos sobrepostos; os rótulos das chaves ajudam a seguir a ordem.

## `camadas_m02.png` (mapa m02_uma_chave)

**O que mostra.** O grafo de estados do m02 em duas faixas, uma por camada, cada uma sobre a grade do
mapa: a camada sem chaves, com 16 estados, e a camada {a}, com 23 estados. O título informa 39
estados mais o ALVO, 73 arcos dentro das camadas (30 + 43), 1 arco que muda de camada e 1 arco de
custo 0 até o ALVO.

O arco que muda de camada aparece em preto e destacado, com o rótulo
`pega a: (3,10)|-|{} → (3,11)|a|{}`. Na camada sem chaves, os estados da linha 1 param em (1,5); na
camada {a}, eles seguem até (1,11).

**Insight.** A diferença entre as faixas mostra que a porta está na própria estrutura do grafo, sem
precisar de uma regra à parte. No mesmo mapa, a linha 1 para em (1,5) sem chaves e segue até (1,11)
com {a}, então G só existe na segunda faixa. As faixas só se ligam pelo arco `pega a`, sem arco de
volta, e por isso o jogador repassa pelas mesmas casas sem repetir estado: (3,10) sem chaves e
(3,10) com {a} são nós diferentes.

**Por que esse gráfico.** As faixas põem cada camada sobre a mesma grade, então uma casa fica na
mesma posição nas duas e dá para comparar direto onde os estados param. Num desenho de grafo comum,
o layout espalharia os 39 estados sem relação com o mapa, e (3,10) sem chaves e (3,10) com {a}
pareceriam nós sem nenhuma ligação. A separação também deixa o único arco entre camadas sozinho, em
preto, no espaço entre as faixas.

## `arvore_bfs_m02.png` (mapa m02_uma_chave)

**O que mostra.** A árvore BFS do grafo de estados, com um nível por linha e os filhos na ordem de
descoberta N, L, S, O. O título informa 39 estados em 36 níveis (0 a 35), menor número de passos até
G igual a 34 e 1 arco da árvore mudando de camada. O ALVO fica no nível 35, um arco depois de G.

A raiz `(1,1)|-|{}` tem dois filhos, `(1,2)|-|{}` e `(2,1)|-|{}`. O ramo por `(1,2)` termina na folha
`(1,5)|-|{}`, no nível 4. O outro ramo é o caminho até o ALVO, em destaque, e o arco "pega a" fica
entre os níveis 11 e 12. A cor dos nós separa os estados sem chaves dos estados com {a}.

Números de apoio: `solucoes.csv` registra 34 passos e custo 46 para a BFS. `comparacao_modelagem.csv`
registra 35 porque conta o arco até o ALVO.

**Insight.** A árvore quase não ramifica: 39 estados ocupam 36 níveis e a única bifurcação está na
raiz, o que mostra que o m02 é praticamente um corredor, sem escolha real de caminho. O ramo curto
termina em (1,5), junto à porta, e as mesmas casas voltam nos níveis 25 a 28, já com {a}: o jogador
precisa ir até a chave, no nível 12, e voltar. Os 34 passos vêm desse desvio obrigatório, visível
na troca de cor.

**Por que esse gráfico.** Na BFS, o nível é o número de passos desde o início, então com o nível no
eixo y a altura de cada nó já é a sua distância, e G aparece no nível 34 sem nenhuma conta. Sobre a
grade isso não funcionaria, porque muitas casas têm dois estados em níveis diferentes e a forma de
linha quase reta, que é o resultado aqui, ficaria escondida. A cor dos nós mantém a camada visível,
e assim dá para ler em que nível o arco "pega a" acontece.

## `multiplicidade_m08.png` (mapa m08_grande)

**O que mostra.** Um heatmap discreto sobre a grade do m08: cada casa recebe a cor do número de
estados alcançáveis naquela casa. O título informa multiplicidade máxima 5, em 165 casas.

| Estados na casa | Casas |
|---|---|
| 1 | 340 |
| 2 | 387 |
| 3 | 128 |
| 4 | 149 |
| 5 | 165 |

As 1.169 casas somam os 2.919 estados do grafo. Por camada, são 165 estados sem chaves, 314 em {a},
442 em {a,b}, 829 em {a,b,c} e 1.169 em {a,b,c,d}.

**Insight.** As cores não se espalham: formam regiões contínuas, escuras perto de S e claras no lado
direito, onde está G. Cada região é a parte do mapa liberada por uma chave, e os números confirmam:
as 165 casas com 5 estados são os 165 estados sem chaves, e as 340 casas com 1 estado são o que só
aparece na camada {a,b,c,d} (1.169 − 829). A multiplicidade mede, então, em quantas camadas a casa
existe, e o mapa de cores vira a ordem em que as portas abrem o labirinto.

**Por que esse gráfico.** O heatmap sobre a grade mantém o que importa aqui, que é onde cada valor
está: barras das cinco classes repetiriam a tabela e perderiam as regiões. A escala é discreta
porque a multiplicidade só assume os inteiros de 1 a 5; uma escala contínua sugeriria valores
intermediários e deixaria as fronteiras entre regiões menos nítidas. Os tons vão do claro ao escuro
de uma só cor porque as classes têm ordem, e a legenda traz quantas casas há em cada uma.
