import tkinter as tk
from tkinter import ttk


class StatisticsFrame:
    """Фрейм со статистикой"""
    
    def __init__(self, parent):
        self.frame = ttk.LabelFrame(parent, text="Статистика")
        self.frame.pack(fill="x", padx=10, pady=5)
        
        ttk.Label(self.frame, text="Поколение:").grid(row=0, column=0, sticky="w", padx=10, pady=2)
        self.generation_label = ttk.Label(self.frame, text="-")
        self.generation_label.grid(row=0, column=1, sticky="w", padx=5)
        
        ttk.Label(self.frame, text="Лучшее значение:").grid(row=1, column=0, sticky="w", padx=10, pady=2)
        self.best_label = ttk.Label(self.frame, text="-")
        self.best_label.grid(row=1, column=1, sticky="w", padx=5)
        
        ttk.Label(self.frame, text="Среднее значение:").grid(row=2, column=0, sticky="w", padx=10, pady=2)
        self.avg_label = ttk.Label(self.frame, text="-")
        self.avg_label.grid(row=2, column=1, sticky="w", padx=5)
        
        ttk.Label(self.frame, text="Худшее значение:").grid(row=3, column=0, sticky="w", padx=10, pady=2)
        self.worst_label = ttk.Label(self.frame, text="-")
        self.worst_label.grid(row=3, column=1, sticky="w", padx=5)
        
        ttk.Label(self.frame, text="Вес МОД:").grid(row=4, column=0, sticky="w", padx=10, pady=2)
        self.weight_label = ttk.Label(self.frame, text="-")
        self.weight_label.grid(row=4, column=1, sticky="w", padx=5)
    
    def update_stats(self, stats):
        """Обновление статистики"""
        if stats:
            self.generation_label.config(text=stats.get("generation", "-"))
            self.best_label.config(text=f"{stats.get('best_fitness_history', [0])[-1]:.2f}")
            self.avg_label.config(text=f"{stats.get('avg_fitness_history', [0])[-1]:.2f}")
            self.worst_label.config(text=f"{stats.get('worst_fitness_history', [0])[-1]:.2f}")
    
    def update_weight(self, weight):
        """Обновление веса МОД"""
        if weight is not None:
            self.weight_label.config(text=f"{weight:.2f}")
    
    def reset(self):
        """Сброс статистики"""
        self.generation_label.config(text="-")
        self.best_label.config(text="-")
        self.avg_label.config(text="-")
        self.worst_label.config(text="-")
        self.weight_label.config(text="-")