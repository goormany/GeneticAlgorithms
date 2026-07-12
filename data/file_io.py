from models.graph import Graph


class FileIO:
    @staticmethod
    def load(filepath: str) -> Graph:
        edges: list[tuple[int, int, float]] = []
        num_vertices = 0
        with open(filepath, "r", encoding="utf-8") as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()

                parts = line.split()
                if len(parts) != 3:
                    raise ValueError(
                        "Некорретное значение в файле. Не хваает параметра"
                    )
                try:
                    u = int(parts[0])
                    v = int(parts[1])
                    w = float(parts[2])
                except ValueError as e:
                    raise ValueError(
                        f"Строка: {line_num}: Ошибка приеобразования - {e}"
                    )

                edges.append((u, v, w))
                num_vertices = max(num_vertices, u, v)

        if not edges:
            raise ValueError("Нет ребер для загрузки")

        graph = Graph(num_vertices)
        for edge in edges:
            graph.add_edge(*edge)

        return graph
