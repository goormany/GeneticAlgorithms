import random
from typing import List, Tuple

class GeneticOperators:
    def __init__(self, num_vertices: int, mutation_rate: float = 0.1,
                 crossover_rate: float = 0.8):
        """
        Args:
            num_vertices: количество вершин в графе
            mutation_rate: вероятность мутации
            crossover_rate: вероятность скрещивания
        """
        self.num_vertices = num_vertices
        self.mutation_rate = mutation_rate
        self.crossover_rate = crossover_rate

    def create_random_individual(self) -> List[int]:
        """
        Создает случайную особь (код Прюфера)
        """
        code_length = self.num_vertices - 2
        if code_length <= 0:
            return []

        return [random.randint(1, self.num_vertices) for _ in range(code_length)]

    def tournament_selection(self, population: List[Tuple[List[int], float]],
                             tournament_size: int = 3) -> List[int]:
        """
        Турнирная селекция

        Args:
            population: популяция [(особь, fitness), ...]
            tournament_size: размер турнира

        Returns:
            Выбранная особь
        """
        tournament = random.sample(population, min(tournament_size, len(population)))
        # Выбираем особь с лучшим (минимальным) fitness
        winner = min(tournament, key=lambda x: x[1])
        return winner[0].copy()

    def roulette_selection(self, population: List[Tuple[List[int], float]]) -> List[int]:
        """
        Рулеточная селекция (с инверсией для минимизации)

        Args:
            population: популяция [(особь, fitness), ...]

        Returns:
            Выбранная особь
        """
        max_fitness = max(fit for _, fit in population)

        # Инвертированные fitness (большие значения становятся маленькими)
        inverted_fitness = [max_fitness - fit + 1 for _, fit in population]
        total_fitness = sum(inverted_fitness)

        # Рулетка
        pick = random.uniform(0, total_fitness)
        current = 0

        for i, fitness in enumerate(inverted_fitness):
            current += fitness
            if current >= pick:
                return population[i][0].copy()

        # На случай ошибок округления
        return population[-1][0].copy()

    def uniform_crossover(self, parent1: List[int], parent2: List[int]) -> Tuple[List[int], List[int]]:
        """
        Равномерное скрещивание
        Каждый ген выбирается случайно от одного из родителей
        """
        if random.random() > self.crossover_rate:
            # Скрещивание не происходит
            return parent1.copy(), parent2.copy()

        if len(parent1) == 0:
            return [], []

        child1 = []
        child2 = []

        for gene1, gene2 in zip(parent1, parent2):
            if random.random() < 0.5:
                child1.append(gene1)
                child2.append(gene2)
            else:
                child1.append(gene2)
                child2.append(gene1)

        return child1, child2

    def one_point_crossover(self, parent1: List[int], parent2: List[int]) -> Tuple[List[int], List[int]]:
        """
        Одноточечное скрещивание
        """
        if random.random() > self.crossover_rate:
            return parent1.copy(), parent2.copy()

        if len(parent1) <= 1:
            return parent1.copy(), parent2.copy()

        # Точка разреза
        point = random.randint(1, len(parent1) - 1)

        child1 = parent1[:point] + parent2[point:]
        child2 = parent2[:point] + parent1[point:]

        return child1, child2

    def two_point_crossover(self, parent1: List[int], parent2: List[int]) -> Tuple[List[int], List[int]]:
        """
        Двухточечное скрещивание
        """
        if random.random() > self.crossover_rate:
            return parent1.copy(), parent2.copy()

        if len(parent1) <= 2:
            return self.one_point_crossover(parent1, parent2)

        # Две точки разреза
        point1 = random.randint(1, len(parent1) - 2)
        point2 = random.randint(point1 + 1, len(parent1) - 1)

        child1 = parent1[:point1] + parent2[point1:point2] + parent1[point2:]
        child2 = parent2[:point1] + parent1[point1:point2] + parent2[point2:]

        return child1, child2

    def mutate(self, individual: List[int]) -> List[int]:
        """
        Мутация особи
        С вероятностью mutation_rate заменяем случайный ген
        """
        if len(individual) == 0:
            return individual.copy()

        mutated = individual.copy()

        for i in range(len(mutated)):
            if random.random() < self.mutation_rate:
                # Заменяем ген на случайную вершину
                mutated[i] = random.randint(1, self.num_vertices)

        return mutated

    def mutate_swap(self, individual: List[int]) -> List[int]:
        """
        Мутация обменом: меняем местами два случайных гена
        """
        if random.random() > self.mutation_rate or len(individual) < 2:
            return individual.copy()

        mutated = individual.copy()
        i, j = random.sample(range(len(mutated)), 2)
        mutated[i], mutated[j] = mutated[j], mutated[i]

        return mutated
