import random

from models.graph import Graph


class GraphGenerator:
    @staticmethod
    def gen_graph(
        num_vertices: int, edge_probability: float, min_weight: float, max_weight: float
    ) -> Graph:
        if num_vertices <= 0:
            raise ValueError("Кол-во вершин должно быть > 0")

        if not (0 <= edge_probability <= 1):
            raise ValueError("Вероятность появления ребра должна быть от 0 до 1")

        if min_weight <= 0:
            raise ValueError("Минимальный вес не может быть <= 0")

        if max_weight >= 1000:
            raise ValueError("Вес ребра не может быть >= 1000")

        if min_weight > max_weight:
            raise ValueError("Минимальное число не может быть больше максимального")

        graph = Graph(num_vertices)

        used_edges = []

        for u in range(1, num_vertices + 1):
            for v in range(1, num_vertices + 1):
                if u == v:
                    continue

                if (u, v) in used_edges:
                    continue

                if random.uniform(0, 1) < edge_probability:
                    graph.add_edge(u, v, random.randint(min_weight, max_weight))

                    used_edges.append((u, v))
                    used_edges.append((v, u))

        return graph
