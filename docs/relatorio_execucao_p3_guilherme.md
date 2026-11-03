# Relatório da execução do P3 — Guilherme Burle

## 1. Objetivo deste relatório

Este relatório explica, de forma didática e individualizada, tudo o que foi feito no pacote **P3 — Análises da Parte 1** do projeto de Teoria dos Grafos + AVD. O pacote ficou responsável por:

- criar os dois mapas próprios do grupo;
- calcular métricas globais dos grafos;
- calcular métricas por camadas de chaves;
- calcular graus de entrada e saída;
- comparar diferentes modelagens;
- registrar as soluções dos algoritmos;
- registrar a classificação dos arcos da DFS;
- salvar o percurso do m03;
- salvar o ciclo negativo do m06;
- encontrar os estados-armadilha dos mapas exigidos;
- documentar as discussões da Parte 1;
- deixar os resultados reproduzíveis por código e protegidos por testes.

A implementação foi feita no repositório clonado em:

`/home/ubuntu/projeto-grafos-g2`

O repositório original utilizado foi:

`https://github.com/joaovictorgcu/projeto-grafos-g2`

O trabalho ficou restrito ao P3. Não foram alterados os módulos que pertencem ao P1, ao P2, ao P4 ou ao P5.

---

## 2. Leitura dos materiais recebidos

### 2.1 Leitura do arquivo TXT

O arquivo TXT foi lido para descobrir a divisão de responsabilidades do grupo. Ele informa que Guilherme é o dono do pacote P3, chamado **Análises da Parte 1**.

O TXT também lista os arquivos esperados e explica que o P3 deve entregar, entre outros itens:

- `metricas_global.json`;
- `camadas.json`;
- arquivos `graus_*.csv`;
- `comparacao_modelagem.csv`;
- `solucoes.csv`;
- `dfs_classificacao.csv`;
- `percurso_m03.json`;
- `ciclo_negativo_m06.json`;
- `armadilhas_m04.csv`;
- `armadilhas_m07.csv`.

O TXT também informa que Guilherme deve criar dois mapas próprios e escrever, no relatório técnico, as discussões do m01, do m06 e do m07, além do gabarito dos mapas do grupo.

### 2.2 Leitura do PDF de critérios

O PDF foi consultado para verificar o formato exato das entregas. A seção de arquivos obrigatórios confirmou que:

- as métricas globais devem conter informações de `G_pos` e `G_est`;
- as camadas devem ser agrupadas pelo conjunto de chaves;
- a comparação deve incluir portas como chão, portas como parede e grafo de estados;
- as soluções devem incluir BFS, Dijkstra e Bellman-Ford;
- a classificação da DFS deve separar arcos de árvore, retorno, avanço e cruzamento;
- o ciclo negativo do m06 precisa ser exibido;
- os estados-armadilha do m04 e do m07 precisam ser exportados.

O PDF também determina que a prova do m05 seja autoral. Por isso, essa prova não foi escrita automaticamente.

### 2.3 Confirmação antes da execução

Foi solicitada confirmação antes de clonar o repositório e modificar os arquivos. A confirmação foi fornecida. Depois disso, o repositório foi clonado e o trabalho começou.

---

## 3. Clonagem e inspeção do repositório

### 3.1 Clonagem

O repositório foi clonado com o comando equivalente a:

```bash
git clone https://github.com/joaovictorgcu/projeto-grafos-g2.git projeto-grafos-g2
```

O clone foi bem-sucedido e começou no commit:

`b35535f — Adiciona solve.py (CLI da Parte 1), estados_armadilha e testes`

### 3.2 Inspeção da estrutura

A estrutura existente foi examinada para evitar duplicação e para respeitar a divisão de pacotes. Foram encontrados:

- `data/mapas/` com os oito mapas oficiais;
- `data/mapas_grupo/` inicialmente vazio, contendo apenas `.gitkeep`;
- `src/graphs/io.py` para leitura e validação dos mapas;
- `src/graphs/graph.py` para a estrutura de grafo;
- `src/graphs/estados.py` para construir os grafos de estados e de posições;
- `src/graphs/algorithms.py` com BFS, DFS, Dijkstra, Bellman-Ford e busca de armadilhas;
- `src/solve.py` com a CLI já existente;
- `tests/` com uma suíte ampla de testes dos pacotes anteriores.

Essa inspeção foi importante porque o P3 deveria consumir as interfaces existentes, e não reimplementar os algoritmos dos outros integrantes.

---

## 4. Entendimento da interface existente

### 4.1 Leitura dos mapas

Foi reutilizada a função `ler_mapa`, de `src/graphs/io.py`. Ela valida:

- se o mapa não está vazio;
- se todas as linhas têm o mesmo tamanho;
- se os símbolos são válidos;
- se existe exatamente um início `S`;
- se existe pelo menos uma saída `G`.

Essa reutilização garante que os mapas novos obedecem às mesmas regras dos mapas oficiais.

### 4.2 Construção do grafo de estados

Foi reutilizada `construir_estados`, de `src/graphs/estados.py`.

Esse construtor começa no estado inicial e explora somente estados alcançáveis. Cada estado registra:

```text
(posição, chaves coletadas, bônus consumidos)
```

A exploração respeita:

- a ordem de direções N, L, S, O;
- portas que exigem a chave correspondente;
- esteiras que permitem somente a direção da seta;
- bônus que só têm valor negativo na primeira utilização;
- fontes `*` reutilizáveis no modelo padrão;
- a regra de que, ao entrar em `G`, o jogo termina;
- o nó virtual `ALVO`.

### 4.3 Construção do grafo de posições

Foi reutilizada `construir_posicoes` em duas versões:

- portas tratadas como chão;
- portas tratadas como parede.

Essas duas versões são usadas na comparação de modelagens exigida pelo enunciado.

### 4.4 Reutilização dos algoritmos

O módulo novo não reimplementa BFS, DFS, Dijkstra ou Bellman-Ford. Ele chama as implementações já existentes em `src/graphs/algorithms.py`.

Isso evita que o P3 altere a responsabilidade do P2 e mantém todos os resultados compatíveis com os testes existentes.

---

## 5. Criação do primeiro mapa próprio

Foi criado o arquivo:

[data/mapas_grupo/guilherme_03_chaves.txt](../data/mapas_grupo/guilherme_03_chaves.txt)

O mapa contém:

- as chaves `a`, `b` e `c`;
- uma porta `A`;
- três casas de esteira `>>>`;
- um bônus `+`;
- um início `S`;
- uma saída `G`.

O conteúdo foi escolhido para cumprir o requisito do PDF de ter pelo menos três chaves, esteiras e bônus.

A porta `A` também permite que o mapa exercite a relação entre chave coletada e passagem posterior pela porta.

O resultado da validação foi:

- chaves: 3;
- esteiras: 3;
- bônus: 1;
- estados alcançáveis: 1.000;
- caminho BFS: 12 passos;
- caminho de Bellman-Ford: custo 12.

O número alto de estados acontece porque as combinações de chaves e o bônus são descobertas à medida que o grafo é explorado. Isso ilustra a diferença entre casas físicas e estados do jogo.

---

## 6. Criação do segundo mapa próprio

Foi criado o arquivo:

[data/mapas_grupo/guilherme_armadilhas.txt](../data/mapas_grupo/guilherme_armadilhas.txt)

Nesse mapa, uma esteira `v` direciona o jogador para uma região inferior que não consegue retornar à saída.

A ideia é criar estados que são alcançáveis a partir do início, mas que não conseguem chegar ao `ALVO`. Esses estados são os estados-armadilha.

A validação encontrou:

- 18 estados alcançáveis;
- 12 estados-armadilha;
- proporção de armadilhas: 66,7%.

O requisito mínimo era 20%. Portanto, o mapa supera o requisito com margem.

A primeira versão do mapa não atendia ao requisito porque a ramificação inferior ainda conseguia retornar à saída. Ela foi corrigida usando uma esteira unidirecional. Depois da correção, a proporção de armadilhas foi recalculada.

---

## 7. Implementação do módulo `src/analise.py`

Foi criado o arquivo:

[src/analise.py](../src/analise.py)

Esse módulo é o centro da implementação do P3. Ele pode ser executado com:

```bash
PYTHONPATH=. python -m src.analise
```

O módulo cria a pasta de saída, lê os mapas oficiais e os mapas do grupo e gera os artefatos numéricos.

### 7.1 Função de escrita JSON

Foi criada uma função auxiliar para escrever JSON com indentação e acentuação preservada. Isso deixa os arquivos legíveis para inspeção manual e para inclusão no relatório.

### 7.2 Função de escrita CSV

Foi criada uma função auxiliar para escrever arquivos CSV com cabeçalho, codificação UTF-8 e separação padronizada.

Isso evita repetir código e mantém todos os CSVs consistentes.

### 7.3 Descoberta dos mapas

O módulo procura automaticamente:

- todos os `.txt` de `data/mapas/`;
- todos os `.txt` de `data/mapas_grupo/`.

Os mapas oficiais recebem nomes curtos como `m01`, `m02` e `m08`. Os mapas do grupo mantêm nomes mais específicos para evitar que dois arquivos tenham o mesmo nome de saída.

Essa correção foi necessária porque os dois mapas inicialmente começavam com `guilherme`, o que poderia fazer um resultado sobrescrever o outro.

---

## 8. Implementação das métricas globais

A função `metricas_globais` gera:

[out/parte1/metricas_global.json](../out/parte1/metricas_global.json)

Para cada mapa, ela calcula:

- número de casas livres;
- lista de chaves;
- número de bônus;
- ordem de `G_pos` com portas como chão;
- tamanho de `G_pos` com portas como chão;
- densidade de `G_pos` com portas como chão;
- ordem de `G_pos` com portas como parede;
- tamanho de `G_pos` com portas como parede;
- densidade de `G_pos` com portas como parede;
- ordem de `G_est`;
- tamanho de `G_est`;
- densidade de `G_est`;
- teto teórico;
- ocupação do teto teórico.

O teto teórico foi calculado como:

```text
casas_livres × 2^(quantidade_de_chaves) × 2^(quantidade_de_bonus)
```

Essa fórmula representa o limite máximo de combinações de posição, chaves e bônus. O grafo real, entretanto, contém apenas os estados alcançáveis.

A ocupação foi calculada como:

```text
estados_alcançáveis / teto_teórico
```

---

## 9. Implementação das camadas

A função `camadas` gera:

[out/parte1/camadas.json](../out/parte1/camadas.json)

Cada camada corresponde a um conjunto de chaves. Por exemplo:

- `-`: nenhuma chave;
- `a`: somente a chave `a`;
- `ab`: chaves `a` e `b`;
- `abc`: as três chaves.

Para cada camada, foram calculados:

- quantidade de estados;
- quantidade de arcos internos;
- grau de saída médio.

Também foram contados os arcos que atravessam de uma camada para outra, como `-->a` ou `a-->ab`.

Essa análise mostra em que momentos a coleta de uma chave muda o estado do jogador e cria uma camada diferente do grafo.

---

## 10. Implementação dos graus de entrada e saída

A função `graus` gera um CSV por mapa:

- `graus_m01.csv` até `graus_m08.csv`;
- `graus_guilherme_03_chaves.csv`;
- `graus_guilherme_armadilhas.csv`.

Cada linha contém:

- o rótulo do estado;
- o grau de entrada;
- o grau de saída.

O grau de entrada informa quantos arcos chegam ao estado. O grau de saída informa quantos movimentos partem do estado.

Estados em becos ou armadilhas tendem a ter grau de saída baixo. Estados que podem ser alcançados por vários caminhos podem ter grau de entrada alto.

---

## 11. Implementação da comparação de modelagens

A função `comparacao_modelagem` gera:

[out/parte1/comparacao_modelagem.csv](../out/parte1/comparacao_modelagem.csv)

A comparação foi executada nos mapas:

- m02;
- m03;
- m04.

Para cada mapa, foram comparados:

1. portas como chão;
2. portas como parede;
3. grafo de estados.

Para cada modelo foram registrados:

- ordem;
- tamanho;
- status da busca BFS;
- quantidade de passos até a saída, quando possível.

Essa comparação foi implementada para evidenciar que o grafo de posições não representa corretamente informações que dependem do histórico, como chaves coletadas, portas abertas e bônus consumidos.

---

## 12. Implementação das soluções dos algoritmos

A função `solucoes` gera:

[out/parte1/solucoes.csv](../out/parte1/solucoes.csv)

Foram executados, em cada mapa:

- BFS;
- Dijkstra;
- Bellman-Ford.

O arquivo registra:

- mapa;
- algoritmo;
- status;
- número de passos;
- custo ou motivo.

Os status possíveis incluem:

- `OK`;
- `SEM_SOLUCAO`;
- `CICLO_NEGATIVO`;
- `ERRO`.

Dijkstra aparece como recusado nos mapas com pesos negativos, especialmente m05 e m06. Isso está correto: Dijkstra não pode ser usado com segurança quando existem arcos negativos.

O m07 aparece como `SEM_SOLUCAO` nos três algoritmos porque nenhum caminho até a saída é alcançável.

O m06 aparece com `CICLO_NEGATIVO` no Bellman-Ford porque a fonte reutilizável permite reduzir o custo indefinidamente.

---

## 13. Implementação da classificação da DFS

A função `dfs_classificacao` gera:

[out/parte1/dfs_classificacao.csv](../out/parte1/dfs_classificacao.csv)

Foram registrados os arcos visitados pela DFS e sua classificação:

- `arvore`: arco que descobre um novo estado;
- `retorno`: arco para um estado ainda ativo na pilha de DFS;
- `avanco`: arco para um descendente já descoberto;
- `cruzamento`: arco entre ramos diferentes ou para outro estado já finalizado.

O arquivo contém também o mapa de origem, porque a mesma classificação pode aparecer em mais de um mapa.

---

## 14. Implementação do percurso do m03

A função `percurso_m03` gera:

[out/parte1/percurso_m03.json](../out/parte1/percurso_m03.json)

O caminho foi obtido com Bellman-Ford, pois ele calcula custo mesmo quando o módulo também precisa lidar com pesos negativos em outros mapas.

O arquivo contém:

- mapa;
- algoritmo usado;
- status;
- quantidade de passos;
- custo;
- sequência dos estados do caminho.

No m03, o resultado encontrado foi um caminho válido até a saída.

---

## 15. Implementação do ciclo negativo do m06

A função `ciclo_m06` gera:

[out/parte1/ciclo_negativo_m06.json](../out/parte1/ciclo_negativo_m06.json)

O arquivo registra:

- o mapa m06;
- o status `CICLO_NEGATIVO`;
- os estados que formam o ciclo;
- o custo total do ciclo.

O ciclo encontrado tem custo `-1`. Isso demonstra que, com a fonte reutilizável, uma volta pode diminuir o custo acumulado. Por esse motivo, não existe um menor caminho finito bem definido no modelo padrão.

---

## 16. Implementação dos estados-armadilha

A função `armadilhas` usa a busca no grafo transposto já existente no projeto.

O procedimento é:

1. transpor todos os arcos do grafo;
2. começar uma BFS no nó virtual `ALVO`;
3. encontrar quais estados conseguem chegar ao `ALVO`;
4. selecionar os estados alcançáveis a partir do início que não aparecem nessa busca reversa.

A função gera:

- [out/parte1/armadilhas_m04.csv](../out/parte1/armadilhas_m04.csv);
- [out/parte1/armadilhas_m07.csv](../out/parte1/armadilhas_m07.csv).

Cada linha contém o estado, a posição, as chaves e os bônus consumidos.

---

## 17. Criação dos testes do P3

Foi criado:

[tests/test_analise.py](../tests/test_analise.py)

Esse arquivo testa separadamente:

### 17.1 Teste do mapa com chaves

Confirma que o mapa próprio possui pelo menos três chaves, esteiras e bônus.

### 17.2 Teste do mapa com armadilhas

Calcula a proporção de estados-armadilha e confirma que ela é pelo menos 20%.

### 17.3 Teste dos artefatos

Confirma que os principais arquivos obrigatórios foram gerados e que o JSON de métricas pode ser lido.

---

## 18. Documentação criada

Foi criado:

[docs/parte1_p3_guilherme.md](../docs/parte1_p3_guilherme.md)

Esse documento contém:

- discussão do m01;
- discussão do m06;
- discussão do m07;
- descrição e gabarito dos mapas próprios;
- espaço reservado para a prova autoral do m05.

A discussão do m01 explica por que BFS e Dijkstra podem produzir caminhos diferentes: BFS minimiza passos, enquanto Dijkstra minimiza custo.

A discussão do m06 explica o problema da fonte reutilizável e a correção `--fonte-consumivel`.

A discussão do m07 explica por que a porta e a posição da chave impedem uma solução.

---

## 19. O que não foi feito de propósito

A prova formal do m05 não foi escrita. O enunciado exige que essa prova seja autoral e que seja feita pelo responsável. Foi deixado somente um roteiro com a ideia central: o conjunto de bônus consumidos só cresce ao longo de um caminho e não volta para um estado anterior com o bônus disponível.

Também não foram implementadas as entregas dos outros pacotes, como:

- novos algoritmos do P2;
- dataset e benchmark da Parte 2;
- visualizações do P5;
- PDF final completo do grupo;
- revisão cruzada do João Victor;
- declaração de uso de IA assinada por todos.

Alguns arquivos de visualização já existentes no repositório foram preservados, mas eles não foram criados nesta execução do P3.

---

## 20. Instalação das dependências

A execução inicial indicou que `pytest` não estava instalado no ambiente. As dependências de `requirements.txt` foram instaladas.

Entre as dependências instaladas ou confirmadas estão:

- `pytest`;
- `networkx`;
- `streamlit`;
- `pandas`;
- `matplotlib`.

A variável `PYTHONPATH=.` foi usada nos comandos de teste porque o projeto não possui um pacote instalado globalmente. Isso permite que os testes encontrem o pacote local `src`.

---

## 21. Resultado dos testes

A suíte completa foi executada com:

```bash
PYTHONPATH=. pytest -q
```

Resultado final:

```text
1079 passed
```

Os testes anteriores do repositório continuaram passando. Isso mostra que a implementação do P3 não quebrou as funcionalidades já existentes.

---

## 22. Commits realizados

Foram feitos três commits locais, separados por tipo de trabalho.

### 22.1 Commit dos mapas

```text
339f62b P3: adiciona mapas do grupo
```

Esse commit contém os dois mapas de `data/mapas_grupo/`.

### 22.2 Commit do código, testes e documentação

```text
2d53389 P3: implementa analises da parte 1
```

Esse commit contém:

- `src/analise.py`;
- `tests/test_analise.py`;
- `docs/parte1_p3_guilherme.md`.

### 22.3 Commit dos artefatos

```text
12be737 P3: adiciona artefatos das analises
```

Esse commit contém os JSONs e CSVs gerados em `out/parte1/`.

### 22.4 Situação do repositório

O branch local ficou três commits à frente de `origin/main`.

Nenhum push foi feito para o GitHub.

A identidade local usada nos commits foi:

```text
Manus Agent <dev-agent@manus.ai>
```

Isso foi necessário porque o repositório não tinha nome e e-mail Git configurados. Para cumprir a exigência acadêmica de que Guilherme tenha commits associados à própria conta, os commits podem precisar ser refeitos ou ter a autoria ajustada antes do push, conforme a política do grupo e da disciplina.

---

# O que ainda precisa ser feito por Guilherme

## 1. Escrever a prova autoral do m05

Esta é a pendência mais importante e não deve ser simplesmente copiada da documentação criada. Guilherme deve escrever a própria prova, usando a ideia da invariância do conjunto de bônus:

- um bônus pode ser consumido somente uma vez;
- o conjunto de bônus consumidos só cresce;
- depois que o bônus é consumido, voltar à mesma posição não recria o desconto;
- portanto, o ciclo negativo existente no grafo de posições não permanece como ciclo negativo no grafo de estados.

A prova precisa ser revisada para ficar formal, clara e compatível com o modelo usado no projeto.

## 2. Conferir pessoalmente todos os números

Guilherme deve abrir e conferir:

- `metricas_global.json`;
- `camadas.json`;
- `solucoes.csv`;
- `percurso_m03.json`;
- `ciclo_negativo_m06.json`;
- os CSVs de graus;
- os CSVs de armadilhas.

A conferência é necessária para que ele consiga explicar os resultados durante a apresentação e responder perguntas das professoras.

## 3. Executar novamente o gerador

Guilherme deve saber explicar e executar:

```bash
cd /home/ubuntu/projeto-grafos-g2
PYTHONPATH=. python -m src.analise
```

Ele deve verificar que os arquivos de `out/parte1/` são reproduzidos sem erro.

## 4. Estudar as discussões dos mapas oficiais

Guilherme precisa dominar especialmente:

- por que BFS e Dijkstra divergem no m01;
- por que Dijkstra recusa pesos negativos;
- por que o m06 possui ciclo negativo;
- como `--fonte-consumivel` muda o modelo;
- por que o m07 não possui solução;
- como a busca no grafo transposto encontra estados-armadilha;
- como as camadas de chaves são calculadas.

## 5. Integrar o texto ao PDF técnico do grupo

O arquivo `docs/parte1_p3_guilherme.md` é uma documentação auxiliar. Guilherme ainda precisa transferir e adaptar as seções pertinentes para o PDF técnico final do grupo.

A prova do m05 deve ser inserida somente depois de ser escrita e revisada por ele.

## 6. Inserir o gabarito dos mapas do grupo no PDF

O PDF deve apresentar, de modo legível:

- estados principais;
- arcos relevantes;
- passos;
- custos;
- quantidade de armadilhas;
- proporção de armadilhas no mapa próprio de armadilhas.

Os CSVs e JSONs servem como evidência detalhada, mas o relatório deve resumir os resultados para leitura humana.

## 7. Garantir a autoria dos commits

Como os commits locais foram criados com `Manus Agent`, Guilherme deve verificar com o grupo como associá-los corretamente à conta exigida pela disciplina.

Ele pode precisar:

- configurar `user.name` e `user.email` locais;
- refazer os commits com a própria identidade;
- ou seguir o procedimento do grupo para preservar os commits e registrar a autoria corretamente.

Isso é importante porque a rubrica exige commits de cada integrante em pelo menos dois pacotes.

## 8. Fazer o push, se o grupo desejar

Nenhum push foi feito. Guilherme ou João Victor precisa decidir se deve enviar os três commits para o repositório remoto, depois de revisar a autoria e o conteúdo.

## 9. Fazer a revisão cruzada do P4

Segundo a divisão do grupo, Guilherme revisa o pacote P4 de João Victor. Essa revisão deve gerar uma contribuição concreta, como:

- um teste;
- uma correção;
- uma melhoria de documentação;
- ou outro commit pequeno e verificável.

Apenas ler o P4 não cumpre a regra de revisão por commit.

## 10. Preparar-se para a apresentação

Mesmo sendo responsável pelo P3, Guilherme deve estudar também P1, P2, P4 e P5. O PDF informa que qualquer integrante pode ser chamado para explicar qualquer parte do projeto.

Ele deve conseguir explicar:

- como um mapa vira um grafo de estados;
- por que o grafo é dirigido;
- como os algoritmos funcionam;
- como os dados da Parte 2 foram tratados;
- quais decisões visuais foram tomadas pelo P5.

## 11. Atualizar a declaração de uso de IA

O TXT informa que a declaração de uso de IA ainda não existia no repositório. O grupo precisa providenciar essa declaração conforme a regra da disciplina e obter a participação ou assinatura dos cinco integrantes, se isso for exigido.

## 12. Fazer a integração final

Antes da entrega, o grupo ainda precisa:

- integrar o relatório do P3 ao PDF técnico;
- integrar as visualizações do P5;
- conferir os arquivos de P1 e P2;
- verificar o mapa surpresa da demonstração ao vivo;
- verificar o README;
- verificar a matriz de contribuição;
- verificar a declaração de uso de IA;
- executar todos os testes;
- executar novamente os scripts de geração;
- conferir se o repositório remoto contém todos os commits e arquivos.

Em resumo, a parte técnica principal do P3 foi implementada e validada. A pendência autoral central é a prova do m05. As demais pendências de Guilherme são estudar os resultados, integrar o conteúdo ao PDF, garantir a autoria dos commits, revisar o P4 e participar da preparação final do grupo.
