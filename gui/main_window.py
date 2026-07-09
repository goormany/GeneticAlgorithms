import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from tkinter.scrolledtext import ScrolledText

from gui.graph_drawer import GraphDrawer
from data.graph_manager import GraphManager
from core.ga_engine import GeneticAlgorithmMST
from utils.enums.crossover_types import CrossoverType
from utils.enums.mutation_types import MutationType
from utils.enums.selection_types import SelectionType

class GA_GUI:

    def __init__(self, root):

        self.graph_manager = GraphManager()
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
                SelectionType.TOURNAMENT.value,
                SelectionType.ROULETTE.value
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
                CrossoverType.ONE_POINT.value,
                CrossoverType.TWO_POINT.value,
                CrossoverType.UNIFORM.value
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
                MutationType.SWAP.value,
                MutationType.RANDOM_RESET.value,
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

        # --- НОВАЯ КНОПКА ДЛЯ РУЧНОГО ВВОДА ---
        ttk.Button(buttons,
                   text="Ввести вручную",
                   command=self.manual_input_graph).pack(side="left", padx=5)

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

        self.ga = None  # Инициализация переменной для алгоритма

    def load_in_ga(self):
        
        self.ga = GeneticAlgorithmMST(self.graph_manager.get_graph(), 
                                   population_size=int(self.population.get()),
                                   crossover_rate=float(self.crossover.get()),
                                   mutation_rate=float(self.mutation.get()),
                                   selection_type=self.selection.get(),
                                   tournament_size=int(self.tournament_size.get()),
                                   crossover_type=self.crossover_method.get(),
                                   mutation_type=self.mutation_method.get(),
                                   elitism_count=int(self.elitism.get()))


    def update_selection(self, event=None):
        if self.selection.get() == SelectionType.TOURNAMENT.value:
            self.tournament_size.configure(state="normal")
        else:
            self.tournament_size.configure(state="disabled")

    def load_graph(self):
        filename = filedialog.askopenfilename(
            filetypes=[("Текстовые файлы", "*.txt"), ("Все файлы", "*.*")]
        )
        if filename:
            self.graph_manager.load(filename)
            num_vercites = self.graph_manager.get_graph().num_vertices

            self.drawer.clear()
            self.drawer.draw(num_vercites, self.graph_manager.get_edges())

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
            
            self.graph_manager.generate_random_graph(n, p, w_min, w_max)
            
            self.drawer.draw(n, self.graph_manager.get_edges())
            self.log.insert(
                "end",
                f"Создание графа: вершин={n}, p={p}, вес=[{w_min}, {w_max}]\n"
            )
            self.log.see("end")
            window.destroy()

        ttk.Button(window, text="Сгенерировать", command=create).grid(row=4, column=0, pady=20)
        ttk.Button(window, text="Отмена", command=window.destroy).grid(row=4, column=1)

    # --- НОВЫЙ МЕТОД ДЛЯ ДИАЛОГОВОГО ОКНА РУЧНОГО ВВОДА ---
    def manual_input_graph(self):
        window = tk.Toplevel(self.root)
        window.title("Ввод графа вручную")
        window.geometry("450x400")
        
        # Инструкция для пользователя
        instruction = (
            "Введите ребра в формате: u v w\n"
            "Где u и v — номера вершин (целые числа), w — вес.\n"
            "Каждое ребро с новой строки. Пример:\n"
            "1 2 5.5\n1 3 10\n2 3 3"
        )
        ttk.Label(window, text=instruction, justify="left", font=("Consolas", 9)).pack(padx=10, pady=5, fill="x")
        
        # Текстовое поле для ввода списка ребер
        txt_input = ScrolledText(window, height=12, width=50)
        txt_input.pack(padx=10, pady=5, fill="both", expand=True)
        
        # Пример дефолтного заполнения, чтобы пользователю было понятнее
        txt_input.insert("1.0", "1 2 10\n1 3 15\n2 3 5\n3 4 20")

        def parse_and_save():
            text_content = txt_input.get("1.0", "end-1c").strip()
            if not text_content:
                messagebox.showwarning("Предупреждение", "Поле ввода пустое!")
                return
            
            edges = []
            detected_vertices = set()
            
            try:
                for line_num, line in enumerate(text_content.split('\n'), 1):
                    line = line.strip()
                    if not line:
                        continue  # Пропускаем пустые строки
                    
                    parts = line.split()
                    if len(parts) != 3:
                        raise ValueError(f"Строка {line_num}: должно быть ровно 3 значения (u, v, w). Получено: {len(parts)}")
                    
                    u = int(parts[0])
                    v = int(parts[1])
                    w = float(parts[2])  # Вес может быть дробным, судя по graph_drawer
                    
                    edges.append((u, v, w))
                    detected_vertices.add(u)
                    detected_vertices.add(v)
            
            except ValueError as e:
                messagebox.showerror("Ошибка парсинга", f"Некорректный формат данных!\n{str(e)}")
                return

            if not edges:
                messagebox.showwarning("Предупреждение", "Не удалось распознать ни одного ребра.")
                return

            # Вычисляем количество вершин (предполагаем непрерывную нумерацию от 1 до max)
            n = max(detected_vertices) if detected_vertices else 0
            
            
            # Отрисовываем граф на холсте
            self.drawer.clear()
            self.drawer.draw(n, graph.get_edges())
            
            # Пишем в лог главного окна
            self.log.insert("end", f"Граф введен вручную: вершин={n}, ребер={len(edges)}.\n")
            self.log.see("end")
            
            window.destroy()

        # Панель кнопок внизу диалогового окна
        btn_frame = ttk.Frame(window)
        btn_frame.pack(fill="x", pady=10)
        
        ttk.Button(btn_frame, text="Применить", command=parse_and_save).pack(side="left", padx=20)
        ttk.Button(btn_frame, text="Отмена", command=window.destroy).pack(side="right", padx=20)

    def reset(self):
        self.algorithm_running = False

        self.log.insert("end", "Алгоритм остановлен пользователем.\n")
        self.log.see("end")

        self.canvas.delete("all")
        self.drawer.clear()  # Также очищаем matplotlib-отрисовку
        self.best_label.config(text="-")
        self.avg_label.config(text="-")
        self.worst_label.config(text="-")

    def run_algorithm(self):
            
        self.algorithm_running = True
        self.log.insert("end", "Алгоритм запущен\n")
        self.log.see("end")

        self.load_in_ga()  # Загружаем граф и параметры в алгоритм

        print(self.ga.run(int(self.generations.get())))

        self.best_label.config(text="Расчет...")
        self.avg_label.config(text="Расчет...")
        self.worst_label.config(text="Расчет...")
