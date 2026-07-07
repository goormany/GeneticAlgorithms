import tkinter as tk
from tkinter import ttk, filedialog
from tkinter.scrolledtext import ScrolledText

from gui.graph_drawer import GraphDrawer
from data.graph_generator import GraphGenerator
from data.file_io import FileIO


class GA_GUI:

    def __init__(self, root):

        self.root = root
        self.root.title("Генетический алгоритм поиска МОД")
        self.algorithm_running = False

        main_panel = ttk.Frame(root)
        main_panel.pack(fill="both", expand=True)

        left_panel = ttk.Frame(main_panel)
        left_panel.pack(side="left", fill="both", expand=True)

        right_panel = ttk.Frame(main_panel, width=400)  # Фиксированная ширина для лога
        right_panel.pack(side="right", fill="both", expand=False)
        right_panel.pack_propagate(False)  # Чтобы ширина не сжималась

        # Параметры
        frame = ttk.LabelFrame(left_panel, text="Параметры")
        frame.pack(fill="x", padx=10, pady=5)

        # Размер популяции
        ttk.Label(frame, text="Размер популяции").grid(row=0, column=0, sticky="w", padx=5, pady=3)

        self.population = ttk.Entry(frame, width=12)
        self.population.insert(0, "100")
        self.population.grid(row=0, column=1)

        # Количество поколений
        ttk.Label(frame, text="Количество поколений").grid(row=1, column=0, sticky="w", padx=5, pady=3)

        self.generations = ttk.Entry(frame, width=12)
        self.generations.insert(0, "200")
        self.generations.grid(row=1, column=1)

        # Вероятность скрещивания
        ttk.Label(frame, text="Вероятность скрещивания").grid(row=2, column=0, sticky="w", padx=5, pady=3)

        self.crossover = ttk.Entry(frame, width=12)
        self.crossover.insert(0, "0.8")
        self.crossover.grid(row=2, column=1)

        # Вероятность мутации
        ttk.Label(frame, text="Вероятность мутации").grid(row=3, column=0, sticky="w", padx=5, pady=3)

        self.mutation = ttk.Entry(frame, width=12)
        self.mutation.insert(0, "0.05")
        self.mutation.grid(row=3, column=1)

        # Метод селекции
        ttk.Label(frame, text="Метод селекции").grid(row=4, column=0, sticky="w", padx=5, pady=3)

        self.selection = ttk.Combobox(
            frame,
            values=[
                "Турнирная",
                "Рулетка"
            ],
            state="readonly",
            width=18
        )
        self.selection.current(0)
        self.selection.grid(row=4, column=1)

        # Размер турнира
        ttk.Label(frame, text="Размер турнира").grid(row=5, column=0, sticky="w", padx=5, pady=3)

        self.tournament_size = ttk.Entry(frame, width=12)
        self.tournament_size.insert(0, "5")
        self.tournament_size.grid(row=5, column=1)

        self.selection.bind("<<ComboboxSelected>>", self.update_selection)
        self.update_selection()

        # Метод скрещивания
        ttk.Label(frame, text="Метод скрещивания").grid(row=6, column=0, sticky="w", padx=5, pady=3)

        self.crossover_method = ttk.Combobox(
            frame,
            values=[
                "Одноточечное",
                "Двухточечное",
                "Равномерное"
            ],
            state="readonly",
            width=18
        )
        self.crossover_method.current(0)
        self.crossover_method.grid(row=6, column=1)

        # Метод мутации
        ttk.Label(frame, text="Метод мутации").grid(row=7, column=0, sticky="w", padx=5, pady=3)

        self.mutation_method = ttk.Combobox(
            frame,
            values=[
                "Замена генов",
                "Обмен генов"
            ],
            state="readonly",
            width=18
        )
        self.mutation_method.current(0)
        self.mutation_method.grid(row=7, column=1)

        # Элитизм
        ttk.Label(frame, text="Элитизм").grid(row=8, column=0, sticky="w", padx=5, pady=3)

        self.elitism = ttk.Entry(frame, width=12)
        self.elitism.insert(0, "2")
        self.elitism.grid(row=8, column=1)

        # Кнопки
        buttons = ttk.Frame(left_panel)
        buttons.pack(fill="x", pady=5)

        ttk.Button(buttons,
                   text="Сгенерировать граф",
                   command=self.generate_graph).pack(side="left", padx=5)

        ttk.Button(buttons,
                   text="Загрузить граф",
                   command=self.load_graph).pack(side="left", padx=5)

        ttk.Button(buttons,
                   text="Запустить",
                   command=self.run_algorithm).pack(side="left", padx=5)

        ttk.Button(buttons,
                   text="Сброс",
                   command=self.reset).pack(side="left", padx=5)

        # Статистика
        info = ttk.LabelFrame(left_panel, text="Статистика")
        info.pack(fill="x", padx=10, pady=5)

        ttk.Label(info, text="Лучшее значение:").grid(row=0, column=0, sticky="w", padx=10, pady=2)
        self.best_label = ttk.Label(info, text="-")
        self.best_label.grid(row=0, column=1, sticky="w", padx=5)

        ttk.Label(info, text="Среднее значение:").grid(row=1, column=0, sticky="w", padx=10, pady=2)
        self.avg_label = ttk.Label(info, text="-")
        self.avg_label.grid(row=1, column=1, sticky="w", padx=5)

        ttk.Label(info, text="Худшее значение:").grid(row=2, column=0, sticky="w", padx=10, pady=2)
        self.worst_label = ttk.Label(info, text="-")
        self.worst_label.grid(row=2, column=1, sticky="w", padx=5)

        # Поле под граф
        graph_frame = ttk.LabelFrame(left_panel, text="Граф")
        graph_frame.pack(fill="both", expand=True, padx=10, pady=5)

        self.canvas = tk.Canvas(graph_frame, bg="white", height=250)
        self.canvas.pack(fill="both", expand=True)

        self.drawer = GraphDrawer(self.canvas)
        
        
        log_frame = ttk.LabelFrame(right_panel, text="Лог")
        log_frame.pack(fill="both", expand=True, padx=10, pady=5)

        self.log = ScrolledText(log_frame, height=10, width=50)
        self.log.pack(fill="both", expand=True)

    def update_selection(self, event=None):
        if self.selection.get() == "Турнирная":
            self.tournament_size.configure(state="normal")
        else:
            self.tournament_size.configure(state="disabled")

    def load_graph(self):
        filename = filedialog.askopenfilename(
            filetypes=[("Текстовые файлы", "*.txt"), ("Все файлы", "*.*")]
        )
        if filename:
            
            graph = FileIO.load(filename)
            
            num_vercites = graph.get_data().num_vercites
            
            self.drawer.clear()
            self.drawer.draw(num_vercites, graph.get_edges())
            
            self.log.insert("end", f"Загружен граф:\n{filename}\n")
            self.log.see("end")

    def generate_graph(self):
        window = tk.Toplevel(self.root)
        window.title("Генерация случайного графа")
        window.geometry("350x230")
        window.resizable(False, False)

        ttk.Label(window, text="Количество вершин").grid(row=0, column=0, padx=10, pady=8, sticky="w")
        vertices = ttk.Entry(window)
        vertices.insert(0, "20")
        vertices.grid(row=0, column=1)

        ttk.Label(window, text="Вероятность появления ребра").grid(row=1, column=0, padx=10, pady=8, sticky="w")
        probability = ttk.Entry(window)
        probability.insert(0, "0.3")
        probability.grid(row=1, column=1)

        ttk.Label(window, text="Минимальный вес").grid(row=2, column=0, padx=10, pady=8, sticky="w")
        min_weight = ttk.Entry(window)
        min_weight.insert(0, "1")
        min_weight.grid(row=2, column=1)

        ttk.Label(window, text="Максимальный вес").grid(row=3, column=0, padx=10, pady=8, sticky="w")
        max_weight = ttk.Entry(window)
        max_weight.insert(0, "100")
        max_weight.grid(row=3, column=1)
        
        def create():
            n = int(vertices.get())
            p = float(probability.get())
            w_min = int(min_weight.get())
            w_max = int(max_weight.get())
            
            graph = GraphGenerator.gen_graph(n, p, w_min, w_max)
            
            self.drawer.draw(n, graph.get_edges())
            self.log.insert(
                "end",
                f"Создание графа: вершин={n}, p={p}, вес=[{w_min}, {w_max}]\n"
            )
            self.log.see("end")
            window.destroy()

        ttk.Button(window, text="Сгенерировать", command=create).grid(row=4, column=0, pady=20)
        ttk.Button(window, text="Отмена", command=window.destroy).grid(row=4, column=1)

    def reset(self):
        self.algorithm_running = False

        self.log.insert("end", "Алгоритм остановлен пользователем.\n")
        self.log.see("end")

        self.canvas.delete("all")
        self.best_label.config(text="-")
        self.avg_label.config(text="-")
        self.worst_label.config(text="-")

    def run_algorithm(self):
        self.algorithm_running = True
        self.log.insert("end", "Алгоритм запущен\n")
        self.log.see("end")

        self.best_label.config(text="Расчет...")
        self.avg_label.config(text="Расчет...")
        self.worst_label.config(text="Расчет...")


