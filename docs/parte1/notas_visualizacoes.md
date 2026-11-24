# Parte 1: notas analíticas das visualizações
[IA] Claude (claude.ai) – revisão de clareza e ortografia; texto escrito por Caio

Rótulos de estado: `(linha,coluna)|chaves|{bônus}`  
Fontes: `src/viz.py`, `out/parte1/metricas_global.json`, `out/parte1/camadas.json`, `out/parte1/solucoes.csv` e `out/parte1/percurso_m03.json`.

---

## `percurso_m03.png` (mapa m03_tres_chaves)

**O que mostra**  
O caminho mais barato encontrado pelo Dijkstra. A cor muda cada vez que o personagem pega uma chave.  
Resultado: 91 passos e custo 99.

| Camada     | Passos | Termina em          |
|------------|--------|---------------------|
| sem chaves | 7      | pega a em (8,1)     |
| {a}        | 18     | pega b em (1,12)    |
| {a,b}      | 43     | pega c em (6,6)     |
| {a,b,c}    | 23     | chega em G          |

Números extras:  
- BFS: 87 passos, custo 119  
- Bellman-Ford: igual ao Dijkstra (91 passos, custo 99)  
- Grafo de estados: 213 estados e 466 arcos (35% do máximo possível de 608)

**Insight**  
O custo total fica baixo porque o algoritmo aceita dar voltas longas para não pisar em água. O trecho de 43 passos com as chaves a e b é o mais caro em distância, mas ainda sai mais barato do que atravessar água cedo.  
O fato de o Bellman-Ford dar o mesmo resultado mostra que não há ciclos negativos e que o grafo de estados está bem montado.

**Por que esse gráfico**  
Ele deixa claro o preço de cada decisão. Dá para ver com os olhos onde o caminho paga água e onde ele prefere alongar o percurso. Uma tabela de estados não mostraria esse trade-off de forma tão direta.

---

## `percurso_m08.png` (mapa m08_grande)

**O que mostra**  
O mesmo tipo de figura, agora no mapa grande.  
Resultado: 396 passos e custo 482.

| Camada       | Passos | Termina em          |
|--------------|--------|---------------------|
| sem chaves   | 46     | pega a em (27,5)    |
| {a}          | 90     | pega b em (3,23)    |
| {a,b}        | 52     | pega c em (5,37)    |
| {a,b,c}      | 106    | pega d em (3,29)    |
| {a,b,c,d}    | 102    | chega em G          |

Números extras:  
- BFS: 392 passos, custo 524  
- Bellman-Ford: igual ao Dijkstra  
- Mapa: 1.169 casas livres, 4 chaves  
- Grafo de estados: 2.919 estados e 6.364 arcos (15,6% do máximo possível de 18.704)

**Insight**  
Mesmo com quatro chaves, o caminho quase não sobe o custo em relação ao BFS (482 contra 524). A diferença de 42 unidades vem só de alguns trechos de água evitados.  
O grafo usa só 15,6% dos estados possíveis. Isso indica que a ordem fixa das chaves corta muita exploração inútil.

**Por que esse gráfico**  
No mapa grande uma lista de 396 posições seria ilegível. A linha colorida por camada transforma o caminho longo em algo que ainda dá para seguir com o olhar e comparar com o m03.

---

## `camadas_m02.png` (mapa m02_uma_chave)

**O que mostra**  
O grafo de estados desenhado em duas faixas, uma por camada, em cima da grade do mapa.

- Sem chaves: 16 estados  
- Com {a}: 23 estados  

Total: 39 estados + ALVO.  
73 arcos dentro das camadas + 1 arco que muda de camada + 1 arco de custo 0 até o ALVO.

O arco que muda de camada está marcado em preto:  
`pega a: (3,10)|-|{} → (3,11)|a|{}`

Na camada sem chaves a linha 1 para em (1,5).  
Na camada {a} ela continua até (1,11).

**Insight**  
A faixa de cima é um caminho incompleto: ela sobe, anda um pouco e para no meio do corredor superior. A faixa de baixo preenche os dois corredores inteiros.  
O desenho mostra que a chave não só “abre a porta”, ela completa o mapa. O que era um beco sem saída na primeira faixa vira um caminho contínuo na segunda.

**Por que esse gráfico**  
Colocar as duas camadas na mesma grade permite comparar o formato de cada uma sem precisar ficar alternando entre figuras. O arco preto no meio serve de âncora visual: a gente enxerga exatamente o ponto em que o grafo muda de tamanho.

---

## `arvore_bfs_m02.png` (mapa m02_uma_chave)

**O que mostra**  
A árvore BFS do grafo de estados. Cada nível ocupa uma linha.

- 39 estados em 36 níveis  
- Menor caminho até G: 34 passos  
- 1 arco da árvore muda de camada  
- ALVO fica no nível 35

A raiz `(1,1)|-|{}` tem dois filhos.  
Um ramo termina rápido na folha `(1,5)|-|{}` (nível 4).  
O outro ramo vai até o ALVO. O “pega a” acontece entre os níveis 11 e 12.  
Cores separam estados sem chave dos estados com {a}.

Números extras:  
- BFS chega em 34 passos com custo 46  

**Insight**  
Depois da raiz a árvore quase não se divide. O único ramo que morre cedo é o da esquerda, que para no nível 4.  
A partir do “pega a” (nível 12) o desenho vira uma linha única laranja até o final. Isso mostra que, uma vez com a chave, o personagem não tem mais escolhas: só existe um caminho possível até o ALVO.

**Por que esse gráfico**  
A altura de cada nó já é a distância em passos. Não precisa de legenda extra. Dá para ver de imediato que o caminho até G é longo e que a maior parte dele acontece depois da chave.

---

## `multiplicidade_m08.png` (mapa m08_grande)

**O que mostra**  
Um heatmap em cima da grade do m08. Cada casa mostra quantos estados alcançáveis caem nela.  
Máximo: 5 estados (em 165 casas).

| Estados na casa | Casas |
|-----------------|-------|
| 1               | 340   |
| 2               | 387   |
| 3               | 128   |
| 4               | 149   |
| 5               | 165   |

As 1.169 casas livres somam os 2.919 estados do grafo.  
Por camada: 165 (sem chaves) → 314 ({a}) → 442 ({a,b}) → 829 ({a,b,c}) → 1.169 ({a,b,c,d}).

**Insight**  
O lado esquerdo do mapa é escuro (muitos estados por casa). O lado direito é quase todo claro (só 1 estado).  
A mudança de cor não é gradual: existe uma divisão bem marcada no meio do labirinto. As casas perto de G só existem na última camada. Isso aparece no desenho como uma grande região clara que só é alcançada depois da última chave.

**Por que esse gráfico**  
Ele transforma um número abstrato (quantos estados por casa) em uma imagem que segue a forma do mapa. Dá para enxergar a progressão das chaves sem precisar ler a tabela de camadas.