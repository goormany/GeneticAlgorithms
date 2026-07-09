import random
from typing import List, Tuple, Dict, Optional
from models.graph import Graph
from models.prufer import PruferCode
from core.operators import GeneticOperators
from utils.enums.crossover_types import CrossoverType
from utils.enums.mutation_types import MutationType
from utils.enums.selection_types import SelectionType

class GeneticAlgorithmMST:
    def __init__(self, graph: Graph,
                 population_size: int = 100,
                 mutation_rate: float = 0.1,
                 crossover_rate: float = 0.8,
                 elitism_count: int = 2,
                 selection_type: str = SelectionType.TOURNAMENT.value,
                 crossover_type: str = CrossoverType.UNIFORM.value,
                 mutation_type: str = MutationType.SWAP.value,
                 tournament_size: int = 3):
        """
        Args:
            graph: граф для поиска МОД
            population_size: размер популяции
            mutation_rate: вероятность мутации
            crossover_rate: вероятность скрещивания
            elitism_count: количество лучших особей, переходящих в следующее поколение
            selection_type: тип селекции ("tournament" или "roulette")
            crossover_type: тип скрещивания ("uniform", "one_point", "two_point")
            mutation_type: тип мутации ("swap" или "random_reset")
            tournament_size: размер турнира для турнирной селекции
        """
        self.graph = graph
        self.population_size = population_size
        self.mutation_rate = mutation_rate
        self.crossover_rate = crossover_rate
        self.elitism_count = elitism_count
        self.selection_type = selection_type
        self.crossover_type = crossover_type
        self.mutation_type = mutation_type
        self.tournament_size = tournament_size

        self.operators = GeneticOperators(
            graph.num_vertices,
            mutation_rate,
            crossover_rate
        )

        self.population: List[List[int]] = []

        # История: для возможности отката
        self.history: List[Dict] = []

        # Текущее поколение
        self.generation = 0

        # Статистика
        self.best_fitness_history: List[float] = []
        self.avg_fitness_history: List[float] = []
        self.worst_fitness_history: List[float] = []

        self._initialize_population()

    def _initialize_population(self):
        self.population = []

        for _ in range(self.population_size):
            individual = self.operators.create_random_individual()
            self.population.append(individual)

        self._save_state()

    def _calculate_fitness(self, individual: List[int]) -> float:
        """Вычисление fitness особи (вес дерева)"""
        edges = PruferCode.code_to_edges(self.graph.num_vertices, individual)

        weight = self.graph.get_edges_weight(edges)

        # Штраф для невалидных деревьев
        if weight == float('inf'):
            max_edge_weight = max((w for _, _, w in self.graph.get_edges()), default=100.0)
            weight = max_edge_weight * self.graph.num_vertices * 10

        return weight

    def _evaluate_population(self) -> List[Tuple[List[int], float]]:
        evaluated = []
        for individual in self.population:
            fitness = self._calculate_fitness(individual)
            evaluated.append((individual, fitness))

        return evaluated

    def _select_parent(self, evaluated_population: List[Tuple[List[int], float]]) -> List[int]:
        if self.selection_type == SelectionType.TOURNAMENT.value:
            return self.operators.tournament_selection(
                evaluated_population,
                self.tournament_size
            )
        elif self.selection_type == SelectionType.ROULETTE.value:
            return self.operators.roulette_selection(evaluated_population)
        else:
            raise ValueError(f"Неизвестный тип селекции: {self.selection_type}")

    def _crossover(self, parent1: List[int], parent2: List[int]) -> Tuple[List[int], List[int]]:
        if self.crossover_type == CrossoverType.UNIFORM.value:
            return self.operators.uniform_crossover(parent1, parent2)
        elif self.crossover_type == CrossoverType.ONE_POINT.value:
            return self.operators.one_point_crossover(parent1, parent2)
        elif self.crossover_type == CrossoverType.TWO_POINT.value:
            return self.operators.two_point_crossover(parent1, parent2)
        else:
            raise ValueError(f"Неизвестный тип скрещивания: {self.crossover_type}")

    def _mutate(self, individual: List[int]) -> List[int]:
        if self.mutation_type == MutationType.SWAP.value:
            return self.operators.mutate_swap(individual)
        elif self.mutation_type == MutationType.RANDOM_RESET.value:
            return self.operators.random_reset_mutation(individual)
        else:
            raise ValueError(f"Неизвестный тип мутации: {self.mutation_type}")

    def _save_state(self):
        """Сохранить текущее состояние в историю"""
        state = {
            'generation': self.generation,
            'population': [ind.copy() for ind in self.population],
            'best_fitness_history': self.best_fitness_history.copy(),
            'avg_fitness_history': self.avg_fitness_history.copy(),
            'worst_fitness_history': self.worst_fitness_history.copy()
        }
        self.history.append(state)

    def step(self) -> Dict:
        """Выполнить один шаг алгоритма (одно поколение)"""
        evaluated_population = self._evaluate_population()

        evaluated_population.sort(key=lambda x: x[1])

        best_fitness = evaluated_population[0][1]
        worst_fitness = evaluated_population[-1][1]
        avg_fitness = sum(fit for _, fit in evaluated_population) / len(evaluated_population)

        self.best_fitness_history.append(best_fitness)
        self.avg_fitness_history.append(avg_fitness)
        self.worst_fitness_history.append(worst_fitness)

        new_population = []

        # Элитизм
        for i in range(min(self.elitism_count, len(evaluated_population))):
            new_population.append(evaluated_population[i][0].copy())

        # Генерация остальных особей через селекцию, скрещивание и мутацию
        while len(new_population) < self.population_size:
            parent1 = self._select_parent(evaluated_population)
            parent2 = self._select_parent(evaluated_population)

            child1, child2 = self._crossover(parent1, parent2)

            child1 = self._mutate(child1)
            child2 = self._mutate(child2)

            new_population.append(child1)
            if len(new_population) < self.population_size:
                new_population.append(child2)

        self.population = new_population
        self.generation += 1

        self._save_state()

        # Вернуть статистику
        best_individual = evaluated_population[0][0]
        best_edges = PruferCode.code_to_edges(self.graph.num_vertices, best_individual)

        return {
            'generation': self.generation - 1,  # Номер завершённого поколения
            'best_fitness': best_fitness,
            'avg_fitness': avg_fitness,
            'worst_fitness': worst_fitness,
            'best_individual': best_individual,
            'best_edges': best_edges
        }

    def run(self, max_generations: int) -> Dict:
        """Запустить алгоритм на заданное количество поколений"""
        for _ in range(max_generations):
            stats = self.step()

        return stats

    def get_best_solution(self) -> Dict:
        """Получить лучшее решение из текущей популяции"""
        evaluated = self._evaluate_population()
        evaluated.sort(key=lambda x: x[1])

        best_individual, best_fitness = evaluated[0]
        best_edges = PruferCode.code_to_edges(self.graph.num_vertices, best_individual)

        return {
            'prufer_code': best_individual,
            'edges': best_edges,
            'weight': best_fitness,
            'generation': self.generation
        }

    def get_population_solutions(self, top_k: int = 10) -> List[Dict]:
        """Получить топ-k решений из текущей популяции"""
        evaluated = self._evaluate_population()
        evaluated.sort(key=lambda x: x[1])

        solutions = []
        for individual, fitness in evaluated[:top_k]:
            edges = PruferCode.code_to_edges(self.graph.num_vertices, individual)
            solutions.append({
                'prufer_code': individual,
                'edges': edges,
                'weight': fitness
            })

        return solutions

    def get_statistics(self) -> Dict:
        """Получить статистику алгоритма"""
        return {
            'generation': self.generation,
            'best_fitness_history': self.best_fitness_history.copy(),
            'avg_fitness_history': self.avg_fitness_history.copy(),
            'worst_fitness_history': self.worst_fitness_history.copy()
        }

    def rollback(self, steps: int = 1) -> bool:
        """Откатить алгоритм на заданное количество шагов назад"""
        if steps <= 0 or len(self.history) <= 1:
            return False

        target_index = max(0, len(self.history) - steps - 1)

        state = self.history[target_index]
        self.generation = state['generation']
        self.population = [ind.copy() for ind in state['population']]
        self.best_fitness_history = state['best_fitness_history'].copy()
        self.avg_fitness_history = state['avg_fitness_history'].copy()
        self.worst_fitness_history = state['worst_fitness_history'].copy()

        self.history = self.history[:target_index + 1]

        return True

    def reset(self):
        """Сбросить алгоритм в начальное состояние"""
        self.generation = 0
        self.history = []
        self.best_fitness_history = []
        self.avg_fitness_history = []
        self.worst_fitness_history = []
        self._initialize_population()
