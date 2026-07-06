from pydantic import BaseModel, Field, model_validator, field_validator

from models.schemas.edge import EdgeData

class GraphData(BaseModel):
    num_vercites: int = Field(gt=0, description="Кол-во вершин")
    edges: list[EdgeData] = []
    
    @model_validator("after")
    def validate_vertices_exists(self):
        if not self.edges:
            return self
        
        max_vertex = 0
        for edge in self.edges:
            max_vertex = max(max_vertex, edge.u, edge.v)
        
        if max_vertex > self.num_vercites:
            raise ValueError("Вершина вне диапозона")
        return self
    
    @model_validator("after")
    def validate_no_duplicates(self):
        viewed = set()
        for edge in self.edges:
            key = (edge.u, edge.v)
            
            if key in viewed:
                raise ValueError(f"Дублирующие ребро ({edge.u}, {edge.v})")
            
            viewed.add(key)
        return self
    
    @classmethod
    def from_edges_list(cls, n: int, edges: list[tuple[int, int, float]]):
        return cls(num_vercites=n, edges=[EdgeData(edge) for edge in edges])
    
    def to_edges_list(self) -> list[tuple[int, int, float]]:
        return [edge.to_tuple() for edge in self.edges]