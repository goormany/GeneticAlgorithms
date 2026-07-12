from models.schemas.ga_state import GAHistory, GAStateStep

class HistoryManager:
    def __init__(self):
        self._cur_index = -1
        self._history = GAHistory()
    
    def add_steps(self, step: GAStateStep):
        # Если мы не в конце истории, обрезаем будущие состояния
        if self._cur_index < len(self._history) - 1:
            # Обрезаем историю
            self._history.steps = self._history.steps[:self._cur_index + 1]
            self._history.best_fitness_history = self._history.best_fitness_history[:self._cur_index + 1]
            self._history.avg_fitness_history = self._history.avg_fitness_history[:self._cur_index + 1]
            self._history.worst_fitness_history = self._history.worst_fitness_history[:self._cur_index + 1]
            self._history.generations_count = len(self._history.steps)
        
        self._history.add_step(step)
        self._cur_index += 1
    
    def go_forward(self) -> GAStateStep | None:
        if self._cur_index < len(self._history) - 1:
            self._cur_index += 1
            return self.get_current()
        return None
    
    def go_back(self) -> GAStateStep | None:
        if self._cur_index > 0:
            self._cur_index -= 1
            return self.get_current()
        return None
    
    def go_to(self, index: int) -> GAStateStep | None:
        if 0 <= index < len(self._history):
            self._cur_index = index
            return self.get_current()
        return None
    
    def go_to_end(self) -> GAStateStep | None:
        if self._history:
            self._cur_index = len(self._history) - 1
            return self.get_current()
        return None
    
    def go_to_start(self) -> GAStateStep | None:
        if self._history:
            self._cur_index = 0
            return self.get_current()
        return None
    
    def get_current(self) -> GAStateStep | None:
        if 0 <= self._current_index < len(self._history):
            return self._history.steps[self._current_index]
        return None

    def get_step(self, index: int) -> GAStateStep | None:
        """Получение шага по индексу"""
        return self._history.get_step(index)
    
    def get_all(self) -> list[GAStateStep]:
        """Получение всей истории"""
        return self._history.steps.copy()
    
    def get_history_stats(self) -> GAHistory:
        """Получение статистики истории (для графиков)"""
        return self._history
    
    def get_last(self) -> GAStateStep | None:
        """Получение последнего шага"""
        return self._history.get_last_step()
    
    def get_first(self) -> GAStateStep | None:
        """Получение первого шага"""
        if self._history:
            return self._history.steps[0]
        return None
    
    def get_best_overall(self) -> GAStateStep | None:
        """Получение шага с лучшим фитнесом"""
        if not self._history.steps:
            return None
        best_index = self._history.get_best_generation()
        if best_index is not None:
            return self._history.steps[best_index]
        return None

    def clear(self) -> None:
        """Очистка истории"""
        self._history.clear()
        self._current_index = -1

    def is_empty(self) -> bool:
        """Проверка, пуста ли история"""
        return self._history.is_empty()
    
    def __len__(self) -> int:
        return len(self._history)