from tkinter import ttk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


class StatisticsFrame:
    """Фрейм со статистикой и графиком"""

    def __init__(self, parent):
        self.frame = ttk.LabelFrame(parent, text="Статистика и график")
        self.frame.pack(fill="both", expand=True, padx=10, pady=5)

        # Текстовые метрики
        metrics_frame = ttk.Frame(self.frame)
        metrics_frame.pack(fill="x", padx=5, pady=5)

        ttk.Label(metrics_frame, text="Поколение:").grid(
            row=0, column=0, sticky="w", padx=5, pady=2
        )
        self.generation_label = ttk.Label(metrics_frame, text="-")
        self.generation_label.grid(row=0, column=1, sticky="w", padx=5)

        ttk.Label(metrics_frame, text="Лучшее значение:").grid(
            row=1, column=0, sticky="w", padx=5, pady=2
        )
        self.best_label = ttk.Label(metrics_frame, text="-")
        self.best_label.grid(row=1, column=1, sticky="w", padx=5)

        ttk.Label(metrics_frame, text="Среднее значение:").grid(
            row=2, column=0, sticky="w", padx=5, pady=2
        )
        self.avg_label = ttk.Label(metrics_frame, text="-")
        self.avg_label.grid(row=2, column=1, sticky="w", padx=5)

        ttk.Label(metrics_frame, text="Худшее значение:").grid(
            row=3, column=0, sticky="w", padx=5, pady=2
        )
        self.worst_label = ttk.Label(metrics_frame, text="-")
        self.worst_label.grid(row=3, column=1, sticky="w", padx=5)

        ttk.Label(metrics_frame, text="Вес МОД:").grid(
            row=4, column=0, sticky="w", padx=5, pady=2
        )
        self.weight_label = ttk.Label(metrics_frame, text="-")
        self.weight_label.grid(row=4, column=1, sticky="w", padx=5)

        # График
        self._create_plot()

    def _create_plot(self):
        """Создание графика"""
        self.fig, self.ax = plt.subplots(figsize=(5, 2.5), dpi=100)
        self.fig.patch.set_facecolor("#f0f0f0")
        self.ax.set_facecolor("#f8f8f8")

        self.ax.set_xlabel("Поколение", fontsize=8)
        self.ax.set_ylabel("Вес МОД", fontsize=8)
        self.ax.tick_params(labelsize=7)
        self.ax.grid(True, alpha=0.3, linestyle="--")

        self.generations = []
        self.weights = []

        (self.best_line,) = self.ax.plot([], [], "g-", linewidth=2, label="Лучший вес")
        self.scatter = self.ax.scatter(
            [], [], c="red", s=20, alpha=0.7, label="Найденные решения"
        )

        self.ax.legend(loc="upper right", fontsize=7)

        self.canvas = FigureCanvasTkAgg(self.fig, master=self.frame)
        self.canvas.get_tk_widget().pack(fill="both", expand=True, padx=5, pady=5)

    def update_stats(self, stats):
        """Обновление статистики"""
        if stats:
            self.generation_label.config(text=stats.get("generation", "-"))
            self.best_label.config(
                text=f"{stats.get('best_fitness_history', [0])[-1]:.2f}"
            )
            self.avg_label.config(
                text=f"{stats.get('avg_fitness_history', [0])[-1]:.2f}"
            )
            self.worst_label.config(
                text=f"{stats.get('worst_fitness_history', [0])[-1]:.2f}"
            )

    def update_weight(self, weight, generation, is_valid=True):
        """Обновление веса МОД и графика"""
        if weight is not None and is_valid:
            self.weight_label.config(text=f"{weight:.2f}")

            if generation is not None:
                self.generations.append(generation)
                self.weights.append(weight)

                # Обновляем линию
                self.best_line.set_data(self.generations, self.weights)

                # Находим точки с улучшением
                current_best = float("inf")
                best_points_x = []
                best_points_y = []

                for i, w in enumerate(self.weights):
                    if w < current_best:
                        current_best = w
                        best_points_x.append(self.generations[i])
                        best_points_y.append(w)

                # Удаляем старый scatter и создаем новый
                self.scatter.remove()
                if best_points_x:
                    self.scatter = self.ax.scatter(
                        best_points_x,
                        best_points_y,
                        c="red",
                        s=20,
                        alpha=0.7,
                        label="Найденные решения",
                    )
                else:
                    self.scatter = self.ax.scatter(
                        [], [], c="red", s=20, alpha=0.7, label="Найденные решения"
                    )

                # Обновляем оси
                if self.generations:
                    self.ax.set_xlim(0, max(self.generations) + 5)
                    min_weight = min(self.weights) - 5 if self.weights else 0
                    max_weight = max(self.weights) + 5 if self.weights else 100
                    self.ax.set_ylim(max(0, min_weight), max_weight)

                self.fig.canvas.draw()

    def truncate(self, generation):
        """Обрезает данные графика до указанного поколения (включительно)."""
        if generation < 0:
            self.generations = []
            self.weights = []
        else:
            cut_index = 0
            for i, gen in enumerate(self.generations):
                if gen <= generation:
                    cut_index = i + 1
                else:
                    break
            self.generations = self.generations[:cut_index]
            self.weights = self.weights[:cut_index]

        self.best_line.set_data(self.generations, self.weights)

        self.scatter.remove()
        current_best = float("inf")
        best_points_x = []
        best_points_y = []
        for i, w in enumerate(self.weights):
            if w < current_best:
                current_best = w
                best_points_x.append(self.generations[i])
                best_points_y.append(w)
        if best_points_x:
            self.scatter = self.ax.scatter(
                best_points_x,
                best_points_y,
                c="red",
                s=20,
                alpha=0.7,
                label="Найденные решения",
            )
        else:
            self.scatter = self.ax.scatter(
                [], [], c="red", s=20, alpha=0.7, label="Найденные решения"
            )

        # Обновляем оси
        if self.generations:
            self.ax.set_xlim(0, max(self.generations) + 5)
            min_weight = min(self.weights) - 5 if self.weights else 0
            max_weight = max(self.weights) + 5 if self.weights else 100
            self.ax.set_ylim(max(0, min_weight), max_weight)
        else:
            self.ax.set_xlim(0, 10)
            self.ax.set_ylim(0, 100)

        self.fig.canvas.draw()

    def bulk_update_weights(self, weight_data: list[tuple[int, float, bool]]):
        """
        Пакетное обновление графика
        """
        for gen, weight, is_valid in weight_data:
            if weight is not None and is_valid:
                if gen is not None:
                    self.generations.append(gen)
                    self.weights.append(weight)

        # Обновляем линию
        self.best_line.set_data(self.generations, self.weights)

        # Находим точки с улучшением
        current_best = float("inf")
        best_points_x = []
        best_points_y = []

        for i, w in enumerate(self.weights):
            if w < current_best:
                current_best = w
                best_points_x.append(self.generations[i])
                best_points_y.append(w)

        # Обновляем scatter
        self.scatter.remove()
        if best_points_x:
            self.scatter = self.ax.scatter(
                best_points_x,
                best_points_y,
                c="red",
                s=20,
                alpha=0.7,
                label="Найденные решения",
            )
        else:
            self.scatter = self.ax.scatter(
                [], [], c="red", s=20, alpha=0.7, label="Найденные решения"
            )

        # Обновляем оси
        if self.generations:
            self.ax.set_xlim(0, max(self.generations) + 5)
            min_weight = min(self.weights) - 5 if self.weights else 0
            max_weight = max(self.weights) + 5 if self.weights else 100
            self.ax.set_ylim(max(0, min_weight), max_weight)
        else:
            self.ax.set_xlim(0, 10)
            self.ax.set_ylim(0, 100)

        self.fig.canvas.draw()

    def reset(self):
        """Сброс статистики и графика"""
        self.generation_label.config(text="-")
        self.best_label.config(text="-")
        self.avg_label.config(text="-")
        self.worst_label.config(text="-")
        self.weight_label.config(text="-")

        # Очищаем данные
        self.generations = []
        self.weights = []

        # Очищаем график
        self.best_line.set_data([], [])

        # Удаляем старый scatter и создаем новый пустой
        self.scatter.remove()
        self.scatter = self.ax.scatter(
            [], [], c="red", s=20, alpha=0.7, label="Найденные решения"
        )

        self.ax.set_xlim(0, 10)
        self.ax.set_ylim(0, 100)
        self.fig.canvas.draw()
