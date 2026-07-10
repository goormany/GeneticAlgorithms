from pathlib import Path
from typing import Any

from models.graph import Graph
from models.prufer import PruferCode
from models.schemas.graph import GraphData
from models.schemas.ga_state import GAHistory, GAStateStep
from data.file_io import FileIO
from data.graph_generator import GraphGenerator


class GraphManager:
    def __init__(self):
        self._graph: Graph | None = None
        self._file_io: FileIO = FileIO()
        self._generator: GraphGenerator = GraphGenerator()
    
    def get_graph(self) -> Graph | None:
        return self._graph
    
    def has_graph(self) -> bool:
        return self._graph is not None
    
    def set_graph(self, graph: Graph) -> None:
        self._graph = graph
    
    def clear(self) -> None:
        self._graph = None
    
    def load(self, filepath: str) -> Graph:
        path = Path(filepath)
        if not path.exists():
            raise ValueError("Не найден файл")
        
        try:
            graph = self._file_io.load(filepath)
        except Exception as e:
            raise ValueError(f"Ошибка загрузки графа: {e}")
        
        self.set_graph(graph)
        return graph
        
    def load_from_tuple(self, edges: list[tuple[int, int, float]]) -> Graph:
        num_vertices = max(max(u, v) for u, v, _ in edges)
        graph = Graph(num_vertices)
        
        for u, v, w in edges:
            graph.add_edge(u, v, w)
        self.set_graph(graph)
        
        return self._graph
    
    def generate_random_graph(self,
                              num_vertices: int,
                              edge_probability: float,
                              min_weight: int,
                              max_weight: int) -> Graph:
        self._graph = self._generator.gen_graph(num_vertices, edge_probability, min_weight, max_weight)
        return self._graph
    
    # методы графа
    def get_edges(self) -> list[tuple[int, int, float]]:
        if self._graph is None:
            return ValueError("Не существует графа")
        return self._graph.get_edges()
    
    def get_matrix(self) -> list[list[float]]:
        if self._graph is None:
            return ValueError("Не существует графа")
        return self._graph.get_matrix()
    
    def get_data(self) -> GraphData:
        if self._graph is None:
            return ValueError("Не существует графа")
        return self._graph.get_data()
    
    def add_edge(self, u: int, v: int, w: float):
        if self._graph is None:
            return ValueError("Не существует графа")
        return self._graph.add_edge(u, v, w)
    
    def find_edge(self, u: int, v: int) -> tuple[int, int, float] | None:
        if self._graph is None:
            return ValueError("Не существует графа")
        return self._graph.find_edge(u, v)
    
    def has_edge(self, u: int, v: int) -> bool:
        if self._graph is None:
            return ValueError("Не существует графа")
        return self._graph.has_edge(u, v)
    
    def get_edge_weight(self, u: int, v: int) -> float:
        if self._graph is None:
            return ValueError("Не существует графа")
        return self._graph.get_edge_weight(u, v)
    
    def get_copy_edges(self) -> list[tuple[int, int, float]]:
        if self._graph is None:
            return ValueError("Не существует графа")
        return self._graph.get_copy_edges()
    
    def get_copy_neighbors(self, vertex: int) -> list[tuple[int, float]]:
        if self._graph is None:
            return ValueError("Не существует графа")
        return self._graph.get_copy_neighbors(vertex)
    
    def get_degree(self, vertex: int) -> int:
        if self._graph is None:
            return ValueError("Не существует графа")
        return self._graph.get_degree(vertex)
    
    def get_total_edges(self) -> int:
        if self._graph is None:
            return ValueError("Не существует графа")
        return self._graph.get_total_edges()
    
    def get_total_weight(self) -> float:
        if self._graph is None:
            return ValueError("Не существует графа")
        return self._graph.get_total_weight()
    
    def get_edges_weight(self, edges: list[tuple[int, int]]) -> float:
        if self._graph is None:
            return ValueError("Не существует графа")
        return self._graph.get_edges_weight(edges)
    
    def graph_to_dict(self) -> dict[str, Any]:
        if self._graph is None:
            return ValueError("Не существует графа")
        if self._graph is None:
            return ValueError("Не существует графа")
        return self._graph.to_dict()
    
    def graph_is_connected(self) -> bool:
        if self._graph is None:
            return ValueError("Не существует графа")
        return self._graph.is_connected()
    
    def to_json(self, filepath: str, indent: int = 4) -> None:
        self._graph.to_json(filepath, indent)