
class Grafo:
    def __init__(self):
        self.adj = {}

    def adicionar_no(self, u):
        if u not in self.adj:
            self.adj[u] = []

    def adicionar_arco(self, u, v, peso=1):
        self.adicionar_no(u)
        self.adicionar_no(v)
        self.adj[u].append((v, peso))

    def nos(self):
        return list(self.adj.keys())

    def vizinhos(self, u):
        return [v for v, peso in self.adj.get(u, [])]

    def arcos(self, u):
        return list(self.adj.get(u, []))

    def ordem(self):
        return len(self.adj)

    def tamanho(self):
        total = 0
        for lista in self.adj.values():
            total += len(lista)
        return total

    def grau_saida(self, u):
        return len(self.adj.get(u, []))

    def grau_entrada(self, u):
        total = 0
        for lista in self.adj.values():
            for v, peso in lista:
                if v == u:
                    total += 1
        return total

    def transposto(self):
        novo_grafo = Grafo()

        for u in self.nos():
            novo_grafo.adicionar_no(u)

        for u in self.nos():
            for v, peso in self.arcos(u):
                novo_grafo.adicionar_arco(v, u, peso)

        return novo_grafo
