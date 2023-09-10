import random, numpy as np, seaborn as sns, matplotlib.pyplot as plt
from typing import List, Tuple

# Gera uma população inicial de indivíduos
def pop_inicial(n_pop: int, n_genes: int) -> np.ndarray:
    pop = np.zeros((n_pop, n_genes), dtype=int)
    for i in range(n_pop):
        pop[i] = np.random.permutation(n_genes)
    return pop

# Avalia a adaptabilidade de um indivíduo
def avaliar_individuo(individuo: np.ndarray, distancias: np.ndarray) -> float:
    distancia_total = 0
    for i in range(len(individuo) - 1):
        cidade_atual = individuo[i]
        proxima_cidade = individuo[i + 1]
        distancia_total += distancias[cidade_atual][proxima_cidade]
    cidade_final = individuo[-1]
    cidade_inicial = individuo[0]
    distancia_total += distancias[cidade_final][cidade_inicial]
    return distancia_total

# Avalia a adaptabilidade de uma população
def avaliar_pop(pop: np.ndarray, distancias: np.ndarray) -> np.ndarray:
    n_pop = pop.shape[0]
    fitness = np.zeros(n_pop)
    for i in range(n_pop):
        fitness[i] = avaliar_individuo(pop[i], distancias)
    return fitness

# Seleciona pais para o crossover por meio de torneio
def selecao_pais(pop: np.ndarray, fitness: np.ndarray, n_pop: int) -> np.ndarray:
    pais = np.zeros_like(pop)
    for i in range(n_pop):
        idx_1 = random.randint(0, n_pop - 1)
        idx_2 = random.randint(0, n_pop - 1)
        if fitness[idx_1] < fitness[idx_2]:
            pais[i] = pop[idx_1]
        else:
            pais[i] = pop[idx_2]
    return pais

# Promove Partially Mapped Crossover (PMX) entre dois pais
def crossover_pmx(pai_1: np.ndarray, pai_2: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
    n_genes = len(pai_1)
    filho_1 = -np.ones(n_genes, dtype=int)
    filho_2 = -np.ones(n_genes, dtype=int)

    ponto_corte_1 = random.randint(0, n_genes - 2)
    ponto_corte_2 = random.randint(ponto_corte_1 + 1, n_genes - 1)

    filho_1[ponto_corte_1:ponto_corte_2+1] = pai_2[ponto_corte_1:ponto_corte_2+1]
    filho_2[ponto_corte_1:ponto_corte_2+1] = pai_1[ponto_corte_1:ponto_corte_2+1]

    def preencher_filho(filho, pai):
        for i in range(n_genes):
            if filho[i] == -1:
                gene_pai = pai[i]
                while gene_pai in filho:
                    idx_gene_pai_filho = np.where(filho == gene_pai)[0][0]
                    gene_pai_filho_pai = pai[idx_gene_pai_filho]
                    gene_pai = gene_pai_filho_pai
                filho[i] = gene_pai

    preencher_filho(filho_1, pai_1)
    preencher_filho(filho_2, pai_2)

    return filho_1, filho_2

# Promove crossover em toda a população
def crossover_pop(pais: np.ndarray) -> np.ndarray:
    n_pop, n_genes = pais.shape
    filhos = np.zeros_like(pais)
    for i in range(0, n_pop, 2):
        pai_1 = pais[i]
        pai_2 = pais[i + 1]
        filho_1, filho_2 = crossover_pmx(pai_1, pai_2)
        filhos[i] = filho_1
        filhos[i + 1] = filho_2
    return filhos

# Promove a mutação em apenas um indivíduo
def mutacao_individuo(individuo: np.ndarray) -> None:
    n_genes = len(individuo)
    ponto_troca_1 = random.randint(0, n_genes - 2)
    ponto_troca_2 = random.randint(ponto_troca_1 + 1, n_genes - 1)
    individuo[ponto_troca_1], individuo[ponto_troca_2] = individuo[ponto_troca_2], individuo[ponto_troca_1]

# Promove mutação em toda a população
def mutacao_pop(filhos: np.ndarray, taxa_mutacao: float) -> None:
    n_pop = filhos.shape[0]
    for i in range(n_pop):
        if random.random() < taxa_mutacao:
            mutacao_individuo(filhos[i])

# Seleciona sobreviventes para a próxima geração
def selecao_sobreviventes(pop: np.ndarray, filhos: np.ndarray, fitness: np.ndarray, fitness_filhos: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
    n_pop = pop.shape[0]
    nova_pop = np.zeros_like(pop)
    nova_fitness = np.zeros_like(fitness)
    i_pop = 0
    i_filhos = 0
    for i in range(n_pop):
        if fitness[i_pop] < fitness_filhos[i_filhos]:
            nova_pop[i] = pop[i_pop]
            nova_fitness[i] = fitness[i_pop]
            i_pop += 1
        else:
            nova_pop[i] = filhos[i_filhos]
            nova_fitness[i] = fitness_filhos[i_filhos]
            i_filhos += 1
    return nova_pop, nova_fitness

# Calcular distância entre cidades
def calcular_distancias(coordenadas: List[Tuple[int, int]]) -> np.ndarray:
    n_cidades = len(coordenadas)
    distancias = np.zeros((n_cidades, n_cidades))
    for i in range(n_cidades):
        for j in range(i + 1, n_cidades):
            x1, y1 = coordenadas[i]
            x2, y2 = coordenadas[j]
            distancia = np.sqrt((x1 - x2)**2 + (y1 - y2)**2)
            distancias[i][j] = distancia
            distancias[j][i] = distancia
    return distancias

# Função principal de evolução
def evolucao(coordenadas: List[Tuple[int, int]], taxa_mutacao: float, n_pop: int, n_geracoes: int):
    n_genes = len(coordenadas)
    distancias = calcular_distancias(coordenadas)

    pop = pop_inicial(n_pop, n_genes)
    fitness = avaliar_pop(pop, distancias)

    fitness_ao_longo_geracoes = []

    for geracao in range(n_geracoes):
        pais = selecao_pais(pop, fitness, n_pop)
        filhos = crossover_pop(pais)
        mutacao_pop(filhos, taxa_mutacao)
        fitness_filhos = avaliar_pop(filhos, distancias)
        pop, fitness = selecao_sobreviventes(pop, filhos, fitness, fitness_filhos)

        fitness_ao_longo_geracoes.append(np.min(fitness)) #Armazena o fitness do melhor indivíduo da geração

    return pop[np.argmin(fitness)], fitness_ao_longo_geracoes

# Função para calcular a distância total de uma rota
def calcular_distancia_total(rota: List[int], distancias: np.ndarray) -> float:
    distancia_total = 0
    for i in range(len(rota) - 1):
        cidade_atual = rota[i]
        proxima_cidade = rota[i + 1]
        distancia_total += distancias[cidade_atual][proxima_cidade]
    cidade_final = rota[-1]
    cidade_inicial = rota[0]
    distancia_total += distancias[cidade_final][cidade_inicial]
    return distancia_total

# Função principal
def principal():
    coordenadas = []
    file = 'berlin52.tsp'

    with open(file) as obj_file:
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

    taxa_mutacao = 0.001
    n_pop = 100
    n_geracoes = 400

    melhor_rota, fitness_ao_longo_geracoes = evolucao(coordenadas, taxa_mutacao, n_pop, n_geracoes)

    # Calcula a distância total da melhor rota encontrada
    distancias = calcular_distancias(coordenadas)
    distancia_melhor_rota = calcular_distancia_total(melhor_rota, distancias)

    print(f"Distância da melhor rota: {distancia_melhor_rota}")

    plt.figure(figsize=(10, 6))
    sns.boxplot(data=fitness_ao_longo_geracoes, whis=1.5)
    plt.xlabel('Geração')
    plt.ylabel('Fitness (Menor distância)')
    plt.title('Evolução do fitness ao longo das gerações')
    plt.show()

if __name__ == "__main__":
    principal()