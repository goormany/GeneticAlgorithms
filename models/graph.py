import json
from typing import Any

from models.schemas.graph import GraphData


class Graph:
    def __init__(self, num_vertices: int):
        if num_vertices <= 0:
            raise ValueError("Кол-во вершин не может быть <= 0")
        
        self.num_vertices = num_vertices
        
        self._data = GraphData(num_vercites=num_vertices,
                               matrix=[[0] * num_vertices for _ in range(num_vertices)])
        self._adj_list: list[list[tuple[int, float]]] | None = None
    
    def get_edges(self) -> list[tuple[int, int, float]]:
        return self._data.to_edges_list()
    
    def get_matrix(self) -> list[list[float]]:
        return self._data.matrix
    
    def get_data(self) -> GraphData:
        return self._data

    def _build_adj_list(self) -> None:
        n = self.num_vertices
        self._adj_list = [[] for _ in range(n)]
        
        for u in range(1, self.num_vertices + 1):
            for v in range(1, self.num_vertices + 1):
                self._adj_list[u-1].append((v, self.get_matrix()[u][v]))
                self._adj_list[v-1].append((u, self.get_matrix()[v][u]))

    def _validate_vertex(self, vertex: int) -> None:
        if not (1 <= vertex <= self.num_vertices):
            raise IndexError(f"Вершина {vertex} не существует")
    
    def add_edge(self, u: int, v: int, w: float):
        if u == v:
            raise ValueError("Не допускаются петли")

        if w <= 0:
            raise ValueError("Не допускаются не положительные ребра")
        
        if self.has_edge(u, v):
            raise ValueError("Не допускаются кратные ребра")
        
        self._data.matrix[u-1][v-1] = self._data.matrix[v-1][u-1] = w
        self._adj_list = None
        
    def find_edge(self, u: int, v: int) -> tuple[int, int, float] | None:
        if u == v:
            return None
        
        w = self.get_matrix()[u-1][v-1]
        if w > 0:
            return (u, v, w)
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
        return sum(self.get_matrix()[u][v] for u in range(self.num_vertices) for v in range(self.num_vertices))
    
    def get_edges_weight(self, edges: list[tuple[int, int]]) -> float:
        weight = 0
        for e in edges:
            edge_weight = self.get_edge_weight(*e)
            
            if edge_weight == 0:
                return float("inf")
            
            weight += edge_weight
        return weight
    
    def to_dict(self) -> dict[str, Any]:
        return self._data.model_dump()
    
    def to_json(self, filepath: str, indent: int = 4) -> None:
        with open(filepath, "w", encoding="utf8") as f:
            json.dump(self.to_dict(), f, indent=indent)
    
    def is_connected(self) -> bool:
        if self.num_vertices == 0:
            return False
        if self.num_vertices == 1:
            return True
        
        visited = [False] * self.num_vertices
        stack = [0]  # 0-based индекс
        visited[0] = True
        visited_count = 1
        
        while stack:
            v = stack.pop()
            for neighbor, _ in self.get_copy_neighbors(v + 1):
                idx = neighbor - 1
                if not visited[idx]:
                    visited[idx] = True
                    visited_count += 1
                    stack.append(idx)
        
        return visited_count == self.num_vertices
        
    
    @staticmethod
    def is_tree(n: int, edges: list[tuple[int, int]]) -> bool:
        if len(edges) != n - 1:
            return False
        
        adj = [[] for _ in range(n+1)]
        for u, v in edges:
            adj[u].append(v)
            adj[v].append(u)
        
        visited = [False] * (n+1)
        
        def has_cycle(v: int, p: int):
            visited[v] = True
           
            for to in adj[v]:
                if to == p:
                    continue
                if visited[to]:
                    return True
                if has_cycle(to, v):
                    return True
            return False
        
        if has_cycle(1, 0):
            return False
        
        return all(visited[1:])
        