import json
from typing import Any

from models.schemas.graph import GraphData
from models.schemas.edge import EdgeData


class Graph:
    def __init__(self, num_vertices: int):
        if num_vertices <= 0:
            raise ValueError("Кол-во вершин не может быть <= 0")
        
        self.num_vertices = num_vertices
        
        self._data = GraphData(num_vercites=num_vertices, edges=[])
        self._matrix: list[list[float]] | None = None
        self._adj_list: list[list[tuple[int, float]]] | None = None
    
    def get_edges(self) -> list[tuple[int, int, float]]:
        return self._data.to_edges_list()
    
    def get_matrix(self) -> list[list[float]]:
        if self._matrix is None:
            self._build_matrix()
        return self._matrix
    
    def get_data(self) -> GraphData:
        return self._data
    
    def _build_matrix(self):
        self._matrix = [[0] * self.num_vertices for _ in range(self.num_vertices)]
        
        for u, v, w in self.get_edges():
            self._matrix[u-1][v-1] = self._matrix[v-1][u-1] = w

    def _build_adj_list(self) -> None:
        n = self.num_vertices
        self._adj_list = [[] for _ in range(n)]
        
        for u, v, w in self.edges:
            self._adj_list[u-1].append((v, w))
            self._adj_list[v-1].append((u, w))

    def _validate_vertex(self, vertex: int) -> None:
        if not (1 <= vertex <= self.num_vertices):
            raise IndexError(f"Вершина {vertex} не существует")

    def _normalize_edge(self, u: int, v: int) -> tuple[int, int]:
        return (u, v) if u < v else (v, u)
    
    
    def add_edge(self, u: int, v: int, w: float):
        if u == v:
            raise ValueError("Не допускаются петли")

        if w <= 0:
            raise ValueError("Не допускаются не положительные ребра")
        
        a, b = self._normalize_edge(u, v)
        if self.has_edge(a, b):
            raise ValueError("Не допускаются кратные ребра")
        
        new_edge = EdgeData(u=a, v=b, w=w)
        self._data.edges.append(new_edge)
        
        self._matrix = None
        
    def find_edge(self, u: int, v: int) -> tuple[int, int, float] | None:
        if u == v:
            return None
        
        a, b = self._normalize_edge(u, v)
        
        for edge_u, edge_v, w in self.get_edges():
            if edge_u == a and edge_v == b:
                return (edge_u, edge_v, w)
        return None
    
    def has_edge(self, u: int, v: int) -> bool:
        
        edge = self.find_edge(u, v)
        if edge is None:
            return False
        return True
    
    def get_edge_weight(self, u: int, v: int) -> float:
        edge = self.find_edge(u, v)
        
        if edge is None:
            return 0
        return edge[-1]
        
    def get_copy_edges(self) -> list[tuple[int, int, float]]:
        return self.get_edges().copy()
    
    def get_copy_neighbors(self, vertex: int) -> list[tuple[int, float]]:
        self._validate_vertex(vertex)
        
        if self._adj_list is None:
            self._build_adj_list()
        
        return self._adj_list[vertex-1].copy()
    
    def get_degree(self, vertex: int) -> int:
        self._validate_vertex(vertex)
        
        return len(self.get_copy_neighbors(vertex))
    
    def get_total_edges(self) -> int:
        return len(self.get_edges())
    
    def get_total_weight(self) -> float:
        return sum(w for _, _, w in self.edges)
    
    def to_dict(self) -> dict[str, Any]:
        return self._data.model_dump()
    
    def to_json(self, filepath: str, indent: int = 4) -> None:
        with open(filepath, "w", encoding="utf8") as f:
            json.dump(self.to_dict(), f, indent=indent)