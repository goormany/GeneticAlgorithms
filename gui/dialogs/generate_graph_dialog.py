import tkinter as tk
from tkinter import ttk


class GenerateGraphDialog:
    """Диалог генерации графа"""

    def __init__(self, parent, on_generate):
        self.parent = parent
        self.on_generate = on_generate

        self.window = tk.Toplevel(parent)
        self.window.title("Генерация случайного графа")
        self.window.geometry("350x230")
        self.window.resizable(False, False)

        ttk.Label(self.window, text="Количество вершин").grid(
            row=0, column=0, padx=10, pady=8, sticky="w"
        )
        self.vertices = ttk.Entry(self.window)
        self.vertices.insert(0, "20")
        self.vertices.grid(row=0, column=1)

        ttk.Label(self.window, text="Вероятность появления ребра").grid(
            row=1, column=0, padx=10, pady=8, sticky="w"
        )
        self.probability = ttk.Entry(self.window)
        self.probability.insert(0, "0.3")
        self.probability.grid(row=1, column=1)

        ttk.Label(self.window, text="Минимальный вес").grid(
            row=2, column=0, padx=10, pady=8, sticky="w"
        )
        self.min_weight = ttk.Entry(self.window)
        self.min_weight.insert(0, "1")
        self.min_weight.grid(row=2, column=1)

        ttk.Label(self.window, text="Максимальный вес").grid(
            row=3, column=0, padx=10, pady=8, sticky="w"
        )
        self.max_weight = ttk.Entry(self.window)
        self.max_weight.insert(0, "100")
        self.max_weight.grid(row=3, column=1)

        btn_frame = ttk.Frame(self.window)
        btn_frame.grid(row=4, column=0, columnspan=2, pady=20)

        ttk.Button(btn_frame, text="Сгенерировать", command=self._create).pack(
            side="left", padx=10
        )
        ttk.Button(btn_frame, text="Отмена", command=self.window.destroy).pack(
            side="left", padx=10
        )

    def _create(self):
        n = int(self.vertices.get())
        p = float(self.probability.get())
        w_min = int(self.min_weight.get())
        w_max = int(self.max_weight.get())

        self.on_generate(n, p, w_min, w_max)
        self.window.destroy()
