from pydantic import BaseModel, Field, model_validator

class GraphData(BaseModel):
    num_vercites: int = Field(gt=0, description="Кол-во вершин")
    matrix: list[list[float]] = Field(default_factory=list)
    
    @model_validator(mode="after")
    def validate_matrix(self):
        for u in range(self.num_vercites):
            for v in range(self.num_vercites):
                if u == v and self.matrix[u][v] == self.matrix[v][u] and self.matrix[u][v] != 0:
                    raise ValueError("Запрещены петли")
                
                if self.matrix[u][v] != self.matrix[v][u]:
                    raise ValueError("Допустим только орграф")
                
        return self
    
    @classmethod
    def from_edges_list(cls, n: int, edges: list[tuple[int, int, float]]):
        matrix = [[0] * n for _ in range(n)]
        for u, v, w in edges:
            matrix[u-1][v-1] = w    
        
        return cls(
            num_vercites=n,
            matrix=matrix
        )
    
    def to_edges_list(self) -> list[tuple[int, int, float]]:
        return [(u, v, self.matrix[u-1][v-1]) for u in range(1, self.num_vercites + 1) for v in range(1, self.num_vercites + 1) if self.matrix[u-1][v-1] > 0]