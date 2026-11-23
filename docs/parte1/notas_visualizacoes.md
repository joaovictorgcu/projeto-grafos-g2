# Parte 1: notas analíticas das visualizações
[IA] Claude (claude.ai) – revisão de clareza e ortografia; texto escrito por Caio

Rótulos de estado: `(linha,coluna)|chaves|{bônus}`  
Fontes: `src/viz.py`, `out/parte1/metricas_global.json`, `out/parte1/camadas.json`, `out/parte1/solucoes.csv` e `out/parte1/percurso_m03.json`.

---

## `percurso_m03.png` (mapa m03_tres_chaves)

**O que mostra**  
Percurso de menor custo do Dijkstra sobre a grade do mapa. A cor muda a cada chave coletada.  
Resultado: 91 passos e custo 99.

| Camada     | Passos | Termina em          |
|------------|--------|---------------------|
| sem chaves | 7      | pega a em (8,1)     |
| {a}        | 18     | pega b em (1,12)    |
| {a,b}      | 43     | pega c em (6,6)     |
| {a,b,c}    | 23     | chegada em G        |

Números de apoio:  
- BFS: 87 passos, custo 119  
- Bellman-Ford: iguais ao Dijkstra (91 passos, custo 99)  
- Grafo de estados: 213 estados e 466 arcos (35% do teto teórico de 608)

**Insight**  
O caminho evita água sempre que consegue. Na sala da chave c ele sobe pela linha 3 em vez de atravessar a água da linha 4. A única água que ele paga é a casa (8,9), porque não tem outro caminho.  

Quem manda no trajeto são as chaves, não a posição de G. O caminho passa mais de uma vez pelos mesmos corredores sem repetir estado, porque cada passagem é em uma camada diferente. O trecho mais longo é o de {a,b} (43 passos).

**Por que esse gráfico**  
Desenhar sobre a grade deixa o percurso junto das paredes, portas e terrenos. Isso se perde numa lista de estados ou num desenho abstrato do grafo. A cor por camada separa as idas e voltas pela mesma casa. Com uma cor só ficaria tudo misturado.

---

## `percurso_m08.png` (mapa m08_grande)

**O que mostra**  
Mesmo tipo de figura no mapa grande.  
Resultado: 396 passos e custo 482.

| Camada       | Passos | Termina em          |
|--------------|--------|---------------------|
| sem chaves   | 46     | pega a em (27,5)    |
| {a}          | 90     | pega b em (3,23)    |
| {a,b}        | 52     | pega c em (5,37)    |
| {a,b,c}      | 106    | pega d em (3,29)    |
| {a,b,c,d}    | 102    | chegada em G        |

Números de apoio:  
- BFS: 392 passos, custo 524  
- Bellman-Ford: iguais ao Dijkstra  
- Mapa: 1.169 casas livres, 4 chaves  
- Grafo de estados: 2.919 estados e 6.364 arcos (15,6% do teto teórico de 18.704)

**Insight**  
A distância na grade engana. As chaves b e d estão perto uma da outra na linha 3, mas no percurso ficam a 158 passos de distância porque a chave c fica no meio.  

No m03 o caminho repetia bastante os corredores. Aqui a repetição fica mais no miolo do mapa. A ocupação do grafo caiu de 35% para 15,6% porque as chaves só são pegadas na ordem a → b → c → d.

**Por que esse gráfico**  
Usar o mesmo formato do m03 facilita comparar os dois mapas. O percurso continua sendo uma linha só, então ainda dá pra acompanhar. Um desenho do grafo com quase 3.000 estados seria impossível de ler.

---

## `camadas_m02.png` (mapa m02_uma_chave)

**O que mostra**  
Grafo de estados em duas faixas (uma por camada), desenhadas sobre a grade do mapa.

- Sem chaves: 16 estados  
- Com {a}: 23 estados  

Total: 39 estados + ALVO.  
73 arcos dentro das camadas + 1 arco mudando de camada + 1 arco de custo 0 até o ALVO.

O arco que muda de camada está marcado em preto:  
`pega a: (3,10)|-|{} → (3,11)|a|{}`

Na camada sem chaves a linha 1 para em (1,5).  
Na camada {a} ela continua até (1,11).

**Insight**  
A diferença entre as duas faixas mostra que a porta faz parte da estrutura do grafo. Não precisa de regra extra. G só aparece na segunda faixa. As duas camadas só se conectam pelo arco “pega a” (não tem volta). Por isso dá pra passar várias vezes pela mesma casa sem repetir estado.

**Por que esse gráfico**  
Colocar as camadas uma em cima da outra na mesma grade deixa fácil comparar onde cada uma para. Num desenho normal de grafo os estados ficariam espalhados e a relação com o mapa se perderia. O arco entre camadas fica bem destacado no meio.

---

## `arvore_bfs_m02.png` (mapa m02_uma_chave)

**O que mostra**  
Árvore BFS do grafo de estados. Um nível por linha.

- 39 estados em 36 níveis  
- Menor caminho até G: 34 passos  
- 1 arco da árvore muda de camada  
- ALVO fica no nível 35

A raiz `(1,1)|-|{}` tem dois filhos.  
Um ramo termina rápido na folha `(1,5)|-|{}` (nível 4).  
O outro ramo vai até o ALVO. O “pega a” acontece entre os níveis 11 e 12.  
Cores separam estados sem chave dos estados com {a}.

Números de apoio:  
- BFS chega em 34 passos com custo 46  
- A comparação de modelagem registra 35 porque conta o arco até o ALVO

**Insight**  
A árvore quase não ramifica. Tem 39 estados em 36 níveis e a única bifurcação de verdade está na raiz. Isso mostra que o m02 é basicamente um corredor.  

O ramo curto para junto da porta. Depois o caminho vai buscar a chave e volta pelas mesmas casas já com {a}. Os 34 passos vêm desse vai-e-volta obrigatório.

**Por que esse gráfico**  
Na BFS o nível já é a distância em passos. Colocar o nível no eixo vertical faz a altura do nó mostrar direto quantos passos ele está do início. Sobre a grade isso não funcionaria bem, porque a mesma casa aparece em níveis diferentes.

---

## `multiplicidade_m08.png` (mapa m08_grande)

**O que mostra**  
Heatmap sobre a grade do m08. Cada casa mostra quantos estados alcançáveis caem nela.  
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
As cores formam regiões contínuas: mais escuras perto de S e mais claras perto de G. Cada região corresponde à parte do mapa que uma chave libera.  

As 165 casas com 5 estados são exatamente as casas da camada sem chaves.  
As 340 casas com só 1 estado só aparecem na última camada.  

A multiplicidade mostra em quantas camadas cada casa existe. O mapa de cores acaba revelando a ordem em que as portas abrem o labirinto.

**Por que esse gráfico**  
O heatmap sobre a grade mantém a informação de *onde* cada valor está. Um gráfico de barras só repetiria a tabela e perderia as regiões. A escala discreta (1 a 5) é melhor que uma contínua, porque a multiplicidade só assume valores inteiros.