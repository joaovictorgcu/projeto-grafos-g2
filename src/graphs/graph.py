# [IA] Claude Code (Claude Opus 5.5) – lista de adjacência dirigida, unindo as classes provisórias dos testes do P2
class Grafo:
    def __init__(self):
        self.adj = {}
        self._entrada = {}
        self._tamanho = 0

    def adicionar_no(self, u):
        if u not in self.adj:
            self.adj[u] = []
            self._entrada[u] = 0

    def adicionar_arco(self, u, v, peso=1):
        self.adicionar_no(u)
        self.adicionar_no(v)
        self.adj[u].append((v, peso))
        self._entrada[v] += 1
        self._tamanho += 1

    def nos(self):
        return list(self.adj)

    def vizinhos(self, u):
        return [v for v, _ in self.adj.get(u, ())]

    def arcos(self, u):
        return list(self.adj.get(u, ()))

    def ordem(self):
        return len(self.adj)

    def tamanho(self):
        return self._tamanho

    def grau_saida(self, u):
        return len(self.adj.get(u, ()))

    def grau_entrada(self, u):
        return self._entrada.get(u, 0)

    def transposto(self):
        t = Grafo()
        for u in self.adj:
            t.adicionar_no(u)
        for u, lista in self.adj.items():
            for v, peso in lista:
                t.adicionar_arco(v, u, peso)
        return t
