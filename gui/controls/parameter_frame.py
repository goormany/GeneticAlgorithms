from tkinter import ttk

from utils.enums.crossover_types import CrossoverType
from utils.enums.mutation_types import MutationType
from utils.enums.selection_types import SelectionType


class ParameterFrame:
    """Фрейм с параметрами генетического алгоритма"""

    def __init__(self, parent):
        self.frame = ttk.LabelFrame(parent, text="Параметры")
        self.frame.pack(fill="x", padx=10, pady=5)

        # Размер популяции
        ttk.Label(self.frame, text="Размер популяции").grid(
            row=0, column=0, sticky="w", padx=5, pady=3
        )
        self.population = ttk.Entry(self.frame, width=12)
        self.population.insert(0, "100")
        self.population.grid(row=0, column=1)

        # Количество поколений
        ttk.Label(self.frame, text="Количество поколений").grid(
            row=1, column=0, sticky="w", padx=5, pady=3
        )
        self.generations = ttk.Entry(self.frame, width=12)
        self.generations.insert(0, "200")
        self.generations.grid(row=1, column=1)

        # Вероятность скрещивания
        ttk.Label(self.frame, text="Вероятность скрещивания").grid(
            row=2, column=0, sticky="w", padx=5, pady=3
        )
        self.crossover = ttk.Entry(self.frame, width=12)
        self.crossover.insert(0, "0.8")
        self.crossover.grid(row=2, column=1)

        # Вероятность мутации
        ttk.Label(self.frame, text="Вероятность мутации").grid(
            row=3, column=0, sticky="w", padx=5, pady=3
        )
        self.mutation = ttk.Entry(self.frame, width=12)
        self.mutation.insert(0, "0.05")
        self.mutation.grid(row=3, column=1)

        # Метод селекции
        ttk.Label(self.frame, text="Метод селекции").grid(
            row=4, column=0, sticky="w", padx=5, pady=3
        )
        self.selection = ttk.Combobox(
            self.frame,
            values=[SelectionType.TOURNAMENT.value, SelectionType.ROULETTE.value],
            state="readonly",
            width=18,
        )
        self.selection.current(0)
        self.selection.grid(row=4, column=1)

        # Размер турнира
        ttk.Label(self.frame, text="Размер турнира").grid(
            row=5, column=0, sticky="w", padx=5, pady=3
        )
        self.tournament_size = ttk.Entry(self.frame, width=12)
        self.tournament_size.insert(0, "5")
        self.tournament_size.grid(row=5, column=1)

        self.selection.bind("<<ComboboxSelected>>", self._update_selection)
        self._update_selection()

        # Метод скрещивания
        ttk.Label(self.frame, text="Метод скрещивания").grid(
            row=6, column=0, sticky="w", padx=5, pady=3
        )
        self.crossover_method = ttk.Combobox(
            self.frame,
            values=[
                CrossoverType.ONE_POINT.value,
                CrossoverType.TWO_POINT.value,
                CrossoverType.UNIFORM.value,
            ],
            state="readonly",
            width=18,
        )
        self.crossover_method.current(0)
        self.crossover_method.grid(row=6, column=1)

        # Метод мутации
        ttk.Label(self.frame, text="Метод мутации").grid(
            row=7, column=0, sticky="w", padx=5, pady=3
        )
        self.mutation_method = ttk.Combobox(
            self.frame,
            values=[MutationType.SWAP.value, MutationType.RANDOM_RESET.value],
            state="readonly",
            width=18,
        )
        self.mutation_method.current(0)
        self.mutation_method.grid(row=7, column=1)

        # Элитизм
        ttk.Label(self.frame, text="Элитизм").grid(
            row=8, column=0, sticky="w", padx=5, pady=3
        )
        self.elitism = ttk.Entry(self.frame, width=12)
        self.elitism.insert(0, "2")
        self.elitism.grid(row=8, column=1)

    def _update_selection(self, event=None):
        if self.selection.get() == SelectionType.TOURNAMENT.value:
            self.tournament_size.configure(state="normal")
        else:
            self.tournament_size.configure(state="disabled")

    def get_parameters(self):
        """Возвращает словарь с параметрами"""
        return {
            "population_size": int(self.population.get()),
            "generations": int(self.generations.get()),
            "crossover_rate": float(self.crossover.get()),
            "mutation_rate": float(self.mutation.get()),
            "selection_type": self.selection.get(),
            "tournament_size": int(self.tournament_size.get()),
            "crossover_type": self.crossover_method.get(),
            "mutation_type": self.mutation_method.get(),
            "elitism_count": int(self.elitism.get()),
        }
