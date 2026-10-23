# Parte 2 — Rede de transferências entre clubes

Números reproduzíveis com os comandos do README; todos saem de `out/parte2/parte2_report.json`,
`out/parte2/eda_resumo.json` e `out/parte2/ficha_dataset.json`.

## 1. Dataset e modelagem

**Fonte.** Transfermarkt Datasets (dcaribou), tabela `transfers`, snapshot publicado em 05/09/2026
com dados até 06/07/2026, licença CC0-1.0. O script `scripts/ficha_transfermarkt.py --baixar` baixa
os três arquivos e confere o SHA-256; os CSVs não entram no repositório.

**Grafo de clubes** `G = (V, E, w)`, dirigido e ponderado:

- `V`: clubes do recorte, |V| = 4.739;
- `(u, v) ∈ E` se ao menos um jogador foi de `u` para `v` (direção nativa da fonte), |E| = 31.626;
- `w(u, v) = Σ (valor pago − valor de mercado)` das transferências de `u` para `v`, em EUR.
  36.442 transferências viram 31.626 arcos: as 4.816 de pares repetidos são somadas ao arco do par.

Densidade 0,0014 e grau médio 6,67. 79,14% dos arcos têm peso negativo; o peso vai de −180 mi
(Mbappé, PSG → Real Madrid, saída sem compensação) a +115 mi, com mediana −250 mil.

**Grafo temporal**, nó = (clube, temporada): transferência `(A, s) → (B, s+1)` com o mesmo peso, e
espera `(X, s) → (X, próxima temporada de X)` com peso 0. Todo arco avança no tempo, então não há
ciclo. 21.703 nós e 52.290 arcos (35.326 de transferência, 16.964 de espera).

**Caminho mínimo e ciclo negativo no domínio.** O custo de um caminho é a soma das diferenças entre
o que foi pago e o que o jogador valia. Um caminho de custo muito negativo é uma sequência de clubes
ligada por saídas abaixo do valor de mercado (ou sem pagamento). Um ciclo negativo é um grupo de
clubes que, somando as idas e voltas, cede jogadores uns aos outros por menos do que eles valem; no
grafo estático ele torna o caminho mínimo indefinido (−∞) para quem o alcança.

### Recorte

| Etapa | Linhas |
|---|---:|
| transferências no arquivo bruto | 175.165 |
| até 06/07/2026 | 174.645 |
| com valor pago e valor de mercado | 86.667 |
| sem pseudo-clubes | 86.574 |
| sem self-loops | 86.574 |
| sem empréstimos | 36.442 |

O empréstimo é uma heurística: valor pago 0 num vai-e-volta consecutivo do mesmo jogador. A
marcação é feita sobre o histórico completo do jogador, antes dos outros filtros, com ordenação
estável. Feita depois, a perna de ida cuja volta caiu no filtro de faltantes escapava e o grafo
saía com 5.207 nós e 33.688 arcos, diferente da proposta aprovada
(`tests/test_dataset.py::test_emprestimo_sai_mesmo_quando_a_volta_nao_tem_valor_de_mercado`).

## 2. Exploração dos dados (AVD)

### Estrutural

`transfers` tem 175.165 linhas e 10 colunas: ids e nomes dos clubes, `player_id`, data, temporada
(texto `"24/25"`), `transfer_fee` e `market_value_in_eur` (numéricos, EUR). Atributos do jogador vêm
de `players` (idade derivada de `date_of_birth`, posição, pé, altura, nacionalidade, empresário) e a
liga do destino vem de `clubs`.

Inconsistências verificadas: nenhum valor pago negativo, nenhum valor de mercado ≤ 0, nenhuma linha
duplicada, nenhuma data inválida. Há 520 transferências com data depois do snapshot (até 2030):
são retornos de empréstimo já agendados, não transferências que aconteceram, e saem pelo corte de
data. Os 8 self-loops saem do grafo. A posição desconhecida vem gravada como o texto `"Missing"`, e
é convertida em ausente antes de qualquer contagem.

### Faltantes e mecanismo de ausência

| Atributo | % faltante (brutas) |
|---|---:|
| valor de mercado | 38,91% |
| valor pago | 35,12% |
| os dois ao mesmo tempo | 23,78% |

- **Valor de mercado — MAR em relação à temporada.** A ausência depende de uma variável observada:
  é 100% até 2003, cai de 97% (2004) para 16% (2025) (`e3_faltantes.png`). O Transfermarkt só
  passou a registrar valor de mercado de forma sistemática a partir de meados dos anos 2000.
- **Valor pago — parte MAR, parte MNAR.** Fica em torno de 1/3 em todas as épocas, e o valor de
  mercado mediano das transferências sem valor pago (250 mil) é metade do das com valor pago
  (500 mil): falta mais em transferências de jogadores baratos, o que é observável (MAR). Mas uma
  parte é "valor não divulgado", que depende do próprio valor ausente (MNAR).
- **Liga do destino — ausência estrutural.** 26,85% das transferências usadas vão para clubes fora
  das ligas que o dataset acompanha. Não é erro: virou a categoria "fora das ligas cobertas".
- Empresário (32,79%) é tratado como categoria ("sem empresário"); idade, posição, pé e altura
  faltam em ≤ 2,3% e ficam fora só dos painéis daquele atributo.

**Tratamento.** Sem os dois valores não existe peso, e imputar o valor pago ou o de mercado seria
inventar pesos negativos, o que o enunciado proíbe. Por isso essas transferências ficam fora do
grafo, mas não são apagadas da análise: entram nas contagens de faltantes, no funil e no gráfico
por temporada. A consequência documentada é que o grafo representa sobretudo o mercado a partir de
2010, com transferências de valor divulgado.

### Distribucional

- 54,9% das transferências usadas são saídas gratuitas (valor pago 0, peso = −valor de mercado);
  entre as pagas, 51,41% saem abaixo do valor de mercado (`e2_pesos.png`).
- As gratuitas respondem por 53,4% da soma dos pesos negativos.
- Graus muito assimétricos: mediana de saída 2 e de entrada 1, p99 de 50 e 58, máximo 87 (Benfica,
  saída) e 84 (Fenerbahçe, entrada) (`e1_graus.png`). Poucos clubes concentram as conexões.

### Relacional (atributo-alvo: peso)

Correlação de Spearman (monotônica, robusta aos outliers) do peso com os numéricos: idade −0,40
(moderada, inversa), valor de mercado −0,30 (fraca a moderada, inversa), temporada −0,14 (fraca),
altura 0,08 (desprezível). Entre as categóricas (`e4_relacoes.png`):

- **idade:** a % de transferências com peso negativo sobe de forma monotônica, de 62% (até 21 anos)
  a 96% (34+), junto com a % de gratuitas (45% → 90%). É a relação mais forte, direta e não linear
  (satura acima dos 30);
- **posição:** goleiros 87% negativos, atacantes 73%;
- **empresário:** sem empresário 82%, com 76% — fraca, e confundida com o valor de mercado (os com
  empresário valem mais);
- **pé:** praticamente sem efeito (77%–83%);
- **liga do destino:** é a maior diferença entre grupos. A Premier League é a única com menos da
  metade das transferências negativas (37%, mediana do peso +950 mil); as demais ficam entre 54%
  (Serie A) e 98% (`x2_explanatoria_ligas.png`).

### Outliers

- **Peso por transferência:** a regra do IQR marca 22% das transferências (limites −1,55 mi e
  +0,85 mi). Com uma distribuição de cauda tão pesada, o IQR no valor bruto não separa erro de dado
  real: Mbappé (−180 mi), Neymar (+122 mi), Dembélé (+115 mi), Haaland (−90 mi) e Messi (−80 mi) são
  todos transferências conhecidas e corretas.
- **Razão valor pago / valor de mercado (log10), nas vendas pagas:** 713 outliers (4,34%), fora de
  [−0,96; 0,86], ou seja, pagas por menos de 1/9 ou mais de 7 vezes o valor de mercado
  (`e5_outliers.png`). Nas faixas baixas há valores de mercado redondos (25 mil, 50 mil) com valor
  pago de milhões, onde o valor de mercado provavelmente está desatualizado.
- **Tratamento:** os outliers ficam no grafo. Eles são o fenômeno que a pergunta de pesquisa estuda
  (os maiores ciclos e caminhos negativos passam por eles), e removê-los mudaria a resposta. Nos
  gráficos, a escala log/symlog e as estatísticas por mediana evitam que eles achatem o resto.

## 3. Algoritmos

### BFS e DFS a partir de 3 fontes

| Fonte | Alcançados | Excentricidade | Clubes por nível (0, 1, 2, …) |
|---|---:|---:|---|
| Benfica | 3.203 | 11 | 1, 87, 742, 1.183, 743, 281, 106, 34, 17, 6, 2, 1 |
| Real Madrid | 3.203 | 11 | 1, 38, 421, 1.095, 959, 460, 145, 53, 22, 6, 2, 1 |
| Santos | 3.203 | 10 | 1, 50, 572, 1.184, 856, 364, 114, 40, 15, 6, 1 |

As três fontes alcançam exatamente os mesmos 3.203 clubes (67,6% do grafo): os outros 1.536 não
são alcançáveis a partir de clubes grandes. A maior parte está a 2–4 transferências de distância
(`a3_camadas_bfs.png`).

| Fonte | Árvore | Retorno | Avanço | Cruzamento | Ciclo? |
|---|---:|---:|---:|---:|---|
| Benfica | 3.202 | 13.875 | 10.951 | 1.349 | sim |
| Real Madrid | 3.202 | 13.931 | 10.953 | 1.291 | sim |
| Santos | 3.202 | 13.914 | 10.907 | 1.354 | sim |

Os arcos de retorno mostram que o grafo de clubes é cheio de ciclos (exemplo a partir do Real
Madrid: AC Milan → Roma → AC Milan). Arcos de árvore = alcançados − 1, como esperado.

### Dijkstra (6 pares) e a transformação dos pesos

O Dijkstra recusa pesos negativos (79% dos arcos). A transformação usada no grafo de clubes é o
**deslocamento** `w' = w − mín(w) = w + 180 mi`, que deixa todo peso ≥ 0.

| Origem → destino | Caminho | Custo original |
|---|---|---:|
| Santos → PSG | Santos → Inter → PSG | −42,5 mi |
| Flamengo → Barcelona | Flamengo → Arsenal → Barcelona | −33,8 mi |
| River Plate → Bayern | River Plate → Leipzig → Bayern Munich | −65,0 mi |
| Boca Juniors → Real Madrid | Boca Juniors → Chelsea → Real Madrid | −56,5 mi |
| Ajax → Benfica | Ajax → Inter → Benfica | −34,0 mi |
| Flamengo → Man Utd | Flamengo → Arsenal → Man Utd | −34,8 mi |

**Limite do deslocamento:** cada arco ganha +180 mi, então um caminho de k arcos ganha k · 180 mi.
Como nenhum peso negativo passa de 180 mi, um arco a mais nunca compensa: o Dijkstra deslocado
sempre escolhe um caminho com o menor número de arcos (o mesmo número de passos da BFS nos 6
pares) e, entre esses, o de menor custo original. Ele não encontra o caminho de menor custo real.

Por isso usamos também a **repesagem de Johnson** `w'(u, v) = w(u, v) + h(u) − h(v)`, com `h` vindo
de um Bellman-Ford a partir de um nó virtual. Ela preserva os caminhos mínimos, mas só vale sem
ciclo negativo, então foi aplicada ao grafo temporal: o Dijkstra repesado deu exatamente as mesmas
distâncias do Bellman-Ford nos 7.027 nós alcançados (0 divergências).

### Bellman-Ford

**Com peso negativo e sem ciclo negativo** — grafo temporal, a partir de Benfica (15/16): 7.027
estados alcançados, 6.391 com distância negativa. O destino de menor custo é Bournemouth (27/28),
com custo −335,46 mi em 12 arcos:

Benfica (15/16 … 19/20) → Frankfurt (20/21, Jović −37,7 mi) → AC Milan (21/22, Rebić −25,3 mi)
→ Inter (22/23, Çalhanoğlu −35 mi) → PSG (24/25, Škriniar −50 mi) → Real Madrid (25/26, Mbappé
−180 mi) → AC Milan (26/27, Modrić −4 mi) → Bournemouth (27/28, Jiménez −3,5 mi).

**Com ciclo negativo** — grafo de clubes completo, a partir do Real Madrid: ciclo detectado e
exibido, Abdysh-Ata Kant → Alga Bishkek → Abdysh-Ata Kant, custo −100 mil. No recorte dos 40 clubes
de maior grau: Lyon → Lille → Lyon, custo −1 mi. O Bellman-Ford devolve o primeiro ciclo que ainda
relaxa na |V|-ésima passada, não o mais negativo. Por contagem direta dos pares recíprocos há 1.780
ciclos negativos de comprimento 2; o mais negativo é Real Madrid ⇄ PSG (−30 mi na ida, −180 mi na
volta, −210 mi no total).

## 4. Desempenho e escalabilidade

Média e desvio padrão de 5 execuções (`time.perf_counter`, coletor de lixo desligado durante a
medição), em subgrafos induzidos por amostras encaixadas de nós (10% ⊂ 25% ⊂ … ⊂ 100%, semente 42).
Fonte de BFS, Dijkstra e Bellman-Ford: o clube de maior grau de saída da amostra; a DFS percorre a
floresta completa. Dijkstra com pesos deslocados; Bellman-Ford com os pesos originais (há ciclo
negativo em todos os tamanhos).

| Tamanho | \|V\| | \|E\| | BFS (ms) | DFS (ms) | Dijkstra (ms) | Bellman-Ford (ms) |
|---:|---:|---:|---:|---:|---:|---:|
| 10% | 214 | 314 | 0,03 ± 0,01 | 0,14 ± 0,02 | 0,08 ± 0,01 | 5,64 ± 0,11 |
| 25% | 743 | 1.965 | 0,17 ± 0,02 | 0,73 ± 0,17 | 0,47 ± 0,05 | 186 ± 9,22 |
| 50% | 1.900 | 7.695 | 0,61 ± 0,03 | 2,44 ± 0,07 | 1,61 ± 0,18 | 2.165 ± 63,06 |
| 75% | 3.276 | 17.966 | 1,30 ± 0,16 | 5,01 ± 0,30 | 3,62 ± 0,24 | 8.502 ± 269 |
| 100% | 4.739 | 31.626 | 2,42 ± 0,59 | 8,14 ± 0,31 | 5,63 ± 0,57 | 22.010 ± 366 |

Memória (pico do `tracemalloc`, grafo completo): BFS 371 KB, DFS 3.662 KB, Dijkstra
606 KB. O `tracemalloc` deixa o Bellman-Ford cerca de 6 vezes mais lento, então a memória
dele só foi medida até 50% (549 KB). A DFS gasta mais memória por guardar a classificação de
todos os arcos.

**Escalabilidade** (`a2_escalabilidade.png`): tempo no tamanho / tempo no grafo completo, contra a
mesma razão da complexidade teórica.

| Algoritmo | Complexidade | 10% (medido / teoria) | 50% (medido / teoria) |
|---|---|---|---|
| BFS | O(V + E) | 0,011 / 0,015 | 0,252 / 0,264 |
| DFS | O(V + E) | 0,017 / 0,015 | 0,299 / 0,264 |
| Dijkstra | O((V + E) log V) | 0,014 / 0,009 | 0,286 / 0,235 |
| Bellman-Ford | O(V · E) | 0,0003 / 0,0004 | 0,098 / 0,098 |

As quatro curvas medidas acompanham a teórica. O Bellman-Ford é o caso mais claro: do 50% para o
100% o |V| · |E| cresce 10,2 vezes e o tempo cresceu 10,2 vezes, e o custo por relaxação fica em
~145 ns a partir de 50%. Nos tamanhos pequenos, a parte fixa (montar listas, dicionários) pesa
mais, e o tempo relativo fica um pouco acima ou abaixo da teoria. No grafo completo, o Bellman-Ford
foi cerca de 9 mil vezes mais lento que a BFS.

## 5. Discussão crítica

**Quando usar cada algoritmo.**

- **BFS** responde "a quantas transferências um clube está do outro" e quem é alcançável. É o mais
  rápido e não depende dos pesos, então é o certo para a estrutura da rede (camadas, mundo pequeno).
- **DFS** classifica arcos e detecta ciclo em O(V + E). Aqui ela mostrou que o grafo de clubes é
  cíclico, o que já avisa que um caminho mínimo com pesos negativos pode não existir.
- **Dijkstra** é o mais rápido para custo, mas só com pesos ≥ 0. Com o deslocamento ele vira, na
  prática, uma BFS com desempate por custo. Com Johnson ele é exato, mas Johnson exige um
  Bellman-Ford antes e um grafo sem ciclo negativo.
- **Bellman-Ford** é o único que trata pesos negativos e detecta ciclo negativo, e foi três ordens
  de grandeza mais lento. No grafo temporal (sem ciclo), a parada antecipada o deixa rápido; no
  grafo de clubes, o ciclo negativo força todas as |V| − 1 passadas.

**Limites do design de pesos.**

- Somar os pesos do par esconde a época: Navas (2019) e Mbappé (2024) entram no mesmo arco. O grafo
  temporal resolve isso, ao custo de mais nós.
- O valor de mercado é uma estimativa do Transfermarkt, não um preço. Saída gratuita vira −valor de
  mercado inteiro, então fim de contrato de um jogador caro domina o peso (53,4% da massa negativa).
- O recorte só mantém transferências com os dois valores, o que puxa o grafo para depois de 2010 e
  para transferências de valor divulgado.
- Os ciclos negativos do grafo estático não são "exploráveis" como no jogo da Parte 1: não dá para
  voltar no tempo e repetir a transferência. Eles indicam clubes que trocam jogadores abaixo do
  valor nos dois sentidos, não uma arbitragem real.

**Resposta à pergunta de pesquisa.** Os valores pagos abaixo do valor de mercado dominam a rede:
78% das transferências e 79% dos arcos são negativos. Por isso o grafo de clubes é cheio de ciclos
negativos (1.780 só de comprimento 2), e o caminho de menor custo nele não existe para os 3.203
clubes alcançáveis a partir dos grandes. No grafo temporal, onde o custo é finito, o caminho mais
barato é guiado por poucas saídas muito abaixo do valor de mercado: só a saída gratuita do Mbappé é
54% do custo do melhor caminho a partir do Benfica 15/16. As relações que os algoritmos e a
exploração revelam são: idade (quanto mais velho, mais gratuita e mais negativa a saída), a Premier
League como único destino que paga acima do mercado, e pares de grandes clubes (Real Madrid ⇄ PSG,
Dortmund ⇄ Bayern) que formam os ciclos mais negativos.

## 6. Notas analíticas das visualizações

**E1 — `e1_graus.png` (exploratória).** Mostra, em log-log, a fração de clubes com grau de saída e
de entrada ≥ k. Insight: a curva cai devagar, poucos clubes têm dezenas de parceiros e a maioria tem
1 ou 2 — há hubs. Por que esse gráfico: a distribuição complementar acumulada em log-log mostra a
cauda inteira sem depender da escolha de bins, o que um histograma linear esconderia.

**E2 — `e2_pesos.png` (exploratória).** Histograma do peso por transferência, separado em saídas
gratuitas e vendas pagas. Insight: as gratuitas são 100% negativas e concentradas entre −100 mil e
−5 mi; as pagas se dividem quase ao meio, com a massa negativa um pouco maior. Por que esse
gráfico: histograma para distribuição; escala symlog porque os pesos vão de −180 mi a +122 mi e têm
sinal; dois painéis com o mesmo eixo x em vez de barras sobrepostas.

**E3 — `e3_faltantes.png` (exploratória).** % de transferências sem valor de mercado e sem valor
pago por temporada. Insight: o valor de mercado falta por causa da época (MAR); o valor pago falta
num patamar constante. Por que esse gráfico: linha para evolução no tempo; as duas séries têm a
mesma unidade (%), então dividem o mesmo eixo sem distorção.

**E4 — `e4_relacoes.png` (exploratória, multivariada).** % de transferências com peso negativo por
faixa etária, posição, pé e empresário, com a média geral tracejada. Insight: a idade separa muito
mais que os outros atributos e a relação é monotônica. Por que esse gráfico: gráfico de pontos
(dot plot) com o mesmo eixo nos quatro painéis permite comparar os efeitos entre atributos; o n de
cada grupo fica escrito para não supervalorizar grupos pequenos.

**E5 — `e5_outliers.png` (exploratória).** Valor pago contra valor de mercado nas vendas pagas, em
log-log, com a diagonal de peso 0 e os outliers do IQR (sobre o log da razão) em laranja. Insight:
os outliers são as vendas muito acima ou muito abaixo do valor, concentradas nos valores de mercado
baixos; os maiores pesos absolutos (Neymar, Dembélé, Haaland) estão perto da diagonal em termos
relativos. Por que esse gráfico: dispersão para relação entre duas variáveis contínuas; log porque
os valores cobrem 5 ordens de grandeza.

**X1 — `x1_explanatoria_caminho.png` (explanatória, responde à pergunta).** Custo acumulado ao
longo do caminho de menor custo do Bellman-Ford no grafo temporal, com a saída do Mbappé em
destaque. De onde nasceu: na E2 vimos que as saídas gratuitas são mais da metade da massa negativa,
e no Bellman-Ford o melhor caminho passava por elas. Mensagem: um único jogador saindo de graça
responde por 54% do custo do caminho inteiro. Por que esse gráfico: o degrau acumulado mostra a
contribuição de cada transferência na ordem do caminho; o destaque é por cor (laranja contra cinza)
e tamanho, e o texto em negrito diz a mensagem sem precisar de legenda.

**X2 — `x2_explanatoria_ligas.png` (explanatória).** % de transferências com peso negativo por liga
do clube de destino. De onde nasceu: na E4 a idade e a posição mudavam a proporção de negativos;
olhando a liga do destino apareceu a maior diferença entre grupos. Mensagem: só a Premier League
compra, em geral, acima do valor de mercado. Por que esse gráfico: barras horizontais ordenadas
para comparar muitas categorias com nomes longos; uma só cor de destaque e as demais em cinza; a
linha de 50% dá a referência.

**A1 — `a1_tempos.png` (algoritmos).** Tempo médio de cada algoritmo no grafo completo, em escala
log, com o desvio padrão. Insight: BFS, Dijkstra e DFS ficam em milissegundos; o Bellman-Ford leva
segundos. Por que esse gráfico: barras para comparar magnitudes; escala log porque os tempos
diferem em quatro ordens de grandeza.

**A2 — `a2_escalabilidade.png` (algoritmos).** Tempo medido e curva teórica, ambos relativos ao
grafo completo, um painel por algoritmo. Insight: as duas curvas andam juntas, então o crescimento
medido segue a complexidade. Por que esse gráfico: linhas para crescimento em função do tamanho;
normalizar pelo maior grafo deixa medida e teoria na mesma escala sem eixo duplo.

**A3 — `a3_camadas_bfs.png` (algoritmos).** Clubes descobertos por nível da BFS a partir das três
fontes. Insight: o pico fica no nível 3 e quase tudo está a até 4 transferências — mundo pequeno.
Por que esse gráfico: linha porque o nível é ordenado; três séries no mesmo eixo para comparar as
fontes.
