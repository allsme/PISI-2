from operator import attrgetter
import random, sys, time, copy
import matplotlib.pyplot as plt


# Classe que representa um grafo
class Grafo:

    def __init__(self, quantidade_vertices):
        self.arestas = {}  # dicionário de arestas
        self.vertices = set()  # conjunto de vértices
        self.quantidade_vertices = quantidade_vertices  # quantidade de vértices

    # Adiciona uma aresta ligando "src" a "dest" com um "custo"
    def adicionarAresta(self, src, dest, custo=0):
        # Verifica se a aresta já existe
        if not self.existeAresta(src, dest):
            self.arestas[(src, dest)] = custo
            self.vertices.add(src)
            self.vertices.add(dest)

    # Verifica se existe uma aresta ligando "src" a "dest"
    def existeAresta(self, src, dest):
        return (True if (src, dest) in self.arestas else False)

    # Mostra todas as ligações do grafo
    def mostrarGrafo(self):
        print('Mostrando o grafo:\n')
        for aresta in self.arestas:
            print('%d ligado em %d com custo %d' % (aresta[0], aresta[1], self.arestas[aresta]))

    # Retorna o custo total do caminho
    def getCustoCaminho(self, caminho):

        custo_total = 0
        for i in range(self.quantidade_vertices - 1):
            custo_total += self.arestas[(caminho[i], caminho[i + 1])]

        # Adiciona o custo da última aresta
        custo_total += self.arestas[(caminho[self.quantidade_vertices - 1], caminho[0])]
        return custo_total

    # Obtém caminhos únicos aleatórios - retorna uma lista de listas de caminhos
    def getCaminhosAleatorios(self, tamanho_maximo):

        caminhos_aleatorios, lista_vertices = [], list(self.vertices)

        vertice_inicial = random.choice(lista_vertices)
        if vertice_inicial not in lista_vertices:
            print('Erro: vértice inicial %d não existe!' % vertice_inicial)
            sys.exit(1)

        lista_vertices.remove(vertice_inicial)
        lista_vertices.insert(0, vertice_inicial)

        for i in range(tamanho_maximo):
            lista_temporaria = lista_vertices[1:]
            random.shuffle(lista_temporaria)
            lista_temporaria.insert(0, vertice_inicial)

            if lista_temporaria not in caminhos_aleatorios:
                caminhos_aleatorios.append(lista_temporaria)

        return caminhos_aleatorios

# Classe que representa um grafo completo
class GrafoCompleto(Grafo):

    # Gera um grafo completo
    def gerar(self):
        for i in range(self.quantidade_vertices):
            for j in range(self.quantidade_vertices):
                if i != j:
                    peso = random.randint(1, 10)
                    self.adicionarAresta(i, j, peso)

# Classe que representa uma partícula
class Particula:

    def __init__(self, solucao, custo):

        # Solução atual
        self.solucao = solucao

        # Melhor solução (aptidão) que alcançou até agora
        self.pbest = solucao

        # Define os custos
        self.custo_solucao_atual = custo
        self.custo_pbest_solucao = custo

        # A velocidade de uma partícula é uma sequência de 4-tuplas
        # (1, 2, 1, 'beta') significa SO(1,2), probabilidade 1 e compara com "beta"
        self.velocidade = []

    # Define o pbest
    def setPBest(self, novo_pbest):
        self.pbest = novo_pbest

    # Retorna o pbest
    def getPBest(self):
        return self.pbest

    # Define a nova velocidade (sequência de operadores de troca)
    def setVelocidade(self, nova_velocidade):
        self.velocidade = nova_velocidade

    # Retorna a velocidade (sequência de operadores de troca)
    def getVelocidade(self):
        return self.velocidade

    # Define a solução
    def setSolucaoAtual(self, solucao):
        self.solucao = solucao

    # Obtém a solução
    def getSolucaoAtual(self):
        return self.solucao

    # Define o custo da melhor solução pbest
    def setCustoPBest(self, custo):
        self.custo_pbest_solucao = custo

    # Obtém o custo da melhor solução pbest
    def getCustoPBest(self):
        return self.custo_pbest_solucao

    # Define o custo da solução atual
    def setCustoSolucaoAtual(self, custo):
        self.custo_solucao_atual = custo

    # Obtém o custo da solução atual
    def getCustoSolucaoAtual(self):
        return self.custo_solucao_atual

    # Remove todos os elementos da lista de velocidade
    def limparVelocidade(self):
        del self.velocidade[:]

# Algoritmo PSO
class PSO:

    def __init__(self, grafo, iteracoes, tamanho_populacao, beta=1, alfa=1):
        self.grafo = grafo  # o grafo
        self.iteracoes = iteracoes  # máximo de iterações
        self.tamanho_populacao = tamanho_populacao  # tamanho da população
        self.particulas = []  # lista de partículas
        self.beta = beta  # a probabilidade de todos os operadores de troca na sequência de troca (gbest - x(t-1))
        self.alfa = alfa  # a probabilidade de todos os operadores de troca na sequência de troca (pbest - x(t-1))

        # Inicializado com um grupo de partículas (soluções) aleatórias
        solucoes = self.grafo.getCaminhosAleatorios(self.tamanho_populacao)

        # Verifica se existem soluções
        if not solucoes:
            print('População inicial vazia! Tente executar o algoritmo novamente...')
            sys.exit(1)

        # Cria as partículas e inicialização das sequências de troca em todas as partículas
        for solucao in solucoes:
            # Cria uma nova partícula
            particula = Particula(solucao=solucao, custo=grafo.getCustoCaminho(solucao))
            # Adiciona a partícula
            self.particulas.append(particula)

        # Atualiza o "tamanho_populacao"
        self.tamanho_populacao = len(self.particulas)

    # Define o gbest (melhor partícula da população)
    def setGBest(self, novo_gbest):
        self.gbest = novo_gbest

    # Retorna o gbest (melhor partícula da população)
    def getGBest(self):
        return self.gbest

    # Mostra as informações das partículas
    def mostrarParticulas(self):

        print('Mostrando partículas...\n')
        for particula in self.particulas:
            print('pbest: %s\t|\tcusto pbest: %d\t|\tsolução atual: %s\t|\tcusto solução atual: %d' \
                % (str(particula.getPBest()), particula.getCustoPBest(), str(particula.getSolucaoAtual()),
                            particula.getCustoSolucaoAtual()))
        print('')

    def executar(self):

        # Para cada passo de tempo (iteração)
        for t in range(self.iteracoes):

            # Atualiza o gbest (melhor partícula da população)
            self.gbest = min(self.particulas, key=attrgetter('custo_pbest_solucao'))

            # Para cada partícula no enxame
            for particula in self.particulas:

                particula.limparVelocidade()  # Limpa a velocidade da partícula
                velocidade_temporaria = []
                solucao_gbest = copy.copy(self.gbest.getPBest())  # Obtém a solução do gbest
                solucao_pbest = particula.getPBest()[:]  # Cópia da solução pbest
                solucao_particula = particula.getSolucaoAtual()[:]  # Obtém cópia da solução atual da partícula

                # Gera todos os operadores de troca para calcular (pbest - x(t-1))
                for i in range(self.grafo.quantidade_vertices):
                    if solucao_particula[i] != solucao_pbest[i]:
                        # Gera operador de troca
                        operador_troca = (i, solucao_pbest.index(solucao_particula[i]), self.alfa)

                        # Adiciona operador de troca na lista de velocidade
                        velocidade_temporaria.append(operador_troca)

                        # Realiza a troca
                        aux = solucao_pbest[operador_troca[0]]
                        solucao_pbest[operador_troca[0]] = solucao_pbest[operador_troca[1]]
                        solucao_pbest[operador_troca[1]] = aux

                # Gera todos os operadores de troca para calcular (gbest - x(t-1))
                for i in range(self.grafo.quantidade_vertices):
                    if solucao_particula[i] != solucao_gbest[i]:
                        # Gera operador de troca
                        operador_troca = (i, solucao_gbest.index(solucao_particula[i]), self.beta)

                        # Adiciona operador de troca na lista de velocidade
                        velocidade_temporaria.append(operador_troca)

                        # Realiza a troca
                        aux = solucao_gbest[operador_troca[0]]
                        solucao_gbest[operador_troca[0]] = solucao_gbest[operador_troca[1]]
                        solucao_gbest[operador_troca[1]] = aux

                # Atualiza a velocidade
                particula.setVelocidade(velocidade_temporaria)

                # Gera nova solução para a partícula
                for operador_troca in velocidade_temporaria:
                    if random.random() <= operador_troca[2]:
                        # Realiza a troca
                        aux = solucao_particula[operador_troca[0]]
                        solucao_particula[operador_troca[0]] = solucao_particula[operador_troca[1]]
                        solucao_particula[operador_troca[1]] = aux

                # Atualiza a solução atual
                particula.setSolucaoAtual(solucao_particula)
                # Obtém o custo da solução atual
                custo_solucao_atual = self.grafo.getCustoCaminho(solucao_particula)
                # Atualiza o custo da solução atual
                particula.setCustoSolucaoAtual(custo_solucao_atual)

                # Verifica se a solução atual é a solução pbest
                if custo_solucao_atual < particula.getCustoPBest():
                    particula.setPBest(solucao_particula)
                    particula.setCustoPBest(custo_solucao_atual)

# Leitura dos dados do "berlim52" (supondo que você tem um arquivo chamado "berlim52.tsp")
def lerDadosBerlim52():
    coordenadas = {}
    with open("berlim52.tsp", "r") as file:
        lines = file.readlines()
        for line in lines:
            if line.startswith("NODE_COORD_SECTION"):
                break
        for line in lines:
            if line.startswith("EOF"):
                break
            parts = line.strip().split()
            if len(parts) == 3:
                node, x, y = map(int, parts)
                coordenadas[node] = (x, y)
    return coordenadas

# Função principal
def main():
    coordenadas = []

    # Lê as coordenadas do arquivo "berlin52.tsp"
    a = 'berlin52.tsp'
    with open(a) as obj_file:
        lines = obj_file.readlines()
        read_coordinates = False
        for line in lines:
            if line.strip() == "NODE_COORD_SECTION":
                read_coordinates = True
                continue
            elif read_coordinates and line.strip() != "EOF":
                parts = line.strip().split()
                if len(parts) == 3:
                    _, x, y = parts
                    coordenadas.append((float(x), float(y)))

    # Cria uma instância de Grafo com base nas coordenadas lidas
    grafo_berlim52 = Grafo(quantidade_vertices=len(coordenadas))
    
    # Adicione as arestas ao grafo com as distâncias calculadas a partir das coordenadas
    for i in range(len(coordenadas)):
        for j in range(i + 1, len(coordenadas)):
            x1, y1 = coordenadas[i]
            x2, y2 = coordenadas[j]
            distancia = round(((x1 - x2) ** 2 + (y1 - y2) ** 2) ** 0.5)
            grafo_berlim52.adicionarAresta(i, j, distancia)
            grafo_berlim52.adicionarAresta(j, i, distancia)

    pso_berlim52 = PSO(grafo_berlim52, iteracoes=300, tamanho_populacao=300,  beta=0.3, alfa=0.5)
    pso_berlim52.executar()  # Executa o algoritmo PSO
    pso_berlim52.mostrarParticulas()  # Mostra as partículas

    # Mostra o melhor caminho encontrado
    print('Melhor caminho encontrado:', pso_berlim52.getGBest().getPBest())
    print('Custo do melhor caminho:', pso_berlim52.getGBest().getCustoPBest())

if __name__ == "__main__":
    main()