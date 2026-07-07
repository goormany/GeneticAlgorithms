from pydantic import BaseModel, Field, model_validator

class EdgeData(BaseModel):
    u: int = Field(gt=0)
    v: int = Field(gt=0)
    w: float = Field(description="weight", ge=0)
    
    @model_validator(mode="after")
    def validate_edge(self):
        if self.u == self.v:
            raise ValueError("Петли запрещены")
        
        if self.u > self.v:
            self.u, self.v = self.v, self.u
        
        return self
    