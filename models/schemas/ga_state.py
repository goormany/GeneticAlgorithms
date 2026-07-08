from pydantic import BaseModel, Field

class GAStateStep(BaseModel):
    generation: int = Field(description="Номер поколения", ge=0)
    population: list[list[int]] = Field(description="Список хромосом(кодов Прюфера)",
                                        default_factory=list)
    best_fitness: float = Field(description="Лучший фитнесс")
    avg_fitness: float = Field(description="Средний фитнесс")
    worst_fitness: float = Field(description="Худший фитнесс")
    
    def to_dict(self) -> dict:
        return self.model_dump()
    
    def from_dict(cls, data: dict):
        return cls(**data)


class GAHistory(BaseModel):
    generations_count: int = Field(description="Кол-во поколоений", default=0, ge=0)
    best_fitness_history: list[float] = Field(description="История лучшего фитнеса",
                                              default_factory=list)
    avg_fitness_history: list[float] = Field(description="История среднего фитнеса",
                                              default_factory=list)
    wrost_fitness_history: list[float] = Field(description="История худшего фитнеса",
                                              default_factory=list)
    populations: list[list[list[int]]] = Field(
        default_factory=list,
        description="История популяций (список поколений, каждое со списком хромосом)"
    )
    
    def add_step(self, step: GAStateStep):
        self.generations_count += 1
        self.best_fitness_history.append(step)
        self.avg_fitness_history.append(step)
        self.wrost_fitness_history.append(step)
        self.populations.append(step.population.copy())
    
    def get_step(self, index: int) -> GAStateStep | None:
        if not (0 <= index < self.generations_count):
            return None
        
        return GAStateStep(
            generation=index,
            population=self.populations[index].copy() if self.populations else [],
            best_fitness=self.best_fitness_history[index],
            avg_fitness=self.avg_fitness_history[index],
            worst_fitness=self.worst_fitness_history[index]
        )
    
    def get_last_step(self) -> GAStateStep | None:
        if self.generations_count == 0:
            return None
        
        return self.get_step(self.generations_count - 1)
    
    def get_best_fitness_overall(self) -> float | None:
        return min(self.best_fitness_history) if self.best_fitness_history else None

    def to_dict(self) -> dict:
        return self.model_dump()
