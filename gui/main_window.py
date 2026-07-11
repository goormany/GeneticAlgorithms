import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from tkinter.scrolledtext import ScrolledText
from typing import Callable

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
        self.algorithm_running = False

        # Атрибуты для пошагового управления
        self.current_step = 0
        self.is_playing = False
        self.max_generations = 200

        main_panel = ttk.Frame(root)
        main_panel.pack(fill="both", expand=True)

        left_panel = ttk.Frame(main_panel)
        left_panel.pack(side="left", fill="both", expand=True)

        right_panel = ttk.Frame(main_panel, width=500)  # Увеличил ширину правой панели
        right_panel.pack(side="right", fill="both", expand=False)
        right_panel.pack_propagate(False) 

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

        # Кнопки управления графом
        buttons = ttk.Frame(left_panel)
        buttons.pack(fill="x", pady=5)

        ttk.Button(buttons,
                   text="Сгенерировать граф",
                   command=self.generate_graph).pack(side="left", padx=5)

        ttk.Button(buttons,
                   text="Загрузить граф",
                   command=self.load_graph).pack(side="left", padx=5)

        ttk.Button(buttons,
                   text="Ввести вручную",
                   command=self.manual_input_graph).pack(side="left", padx=5)

        # Кнопки управления алгоритмом
        algo_buttons = ttk.Frame(left_panel)
        algo_buttons.pack(fill="x", pady=5)

        self.btn_run = ttk.Button(algo_buttons,
                   text="Запустить алгоритм",
                   command=self.run_algorithm)
        self.btn_run.pack(side="left", padx=5)

        self.btn_reset = ttk.Button(algo_buttons,
                   text="Сброс",
                   command=self.reset)
        self.btn_reset.pack(side="left", padx=5)

        # Кнопки пошагового управления
        step_controls = ttk.Frame(left_panel)
        step_controls.pack(fill="x", pady=5)

        self.btn_back = ttk.Button(step_controls,
                                   text="Шаг назад",
                                   command=self.prev_step,
                                   state="disabled")
        self.btn_back.pack(side="left", padx=2)

        self.btn_play = ttk.Button(step_controls,
                                   text="▶️ Авто-запуск",
                                   command=self.toggle_play,
                                   state="disabled")
        self.btn_play.pack(side="left", padx=2)

        self.btn_next = ttk.Button(step_controls,
                                   text="Шаг вперед",
                                   command=self.next_step,
                                   state="disabled")
        self.btn_next.pack(side="left", padx=2)

        self.btn_skip = ttk.Button(step_controls,
                                   text="⏯️ Пропустить",
                                   command=self.skip_to_end,
                                   state="disabled")
        self.btn_skip.pack(side="left", padx=2)

        # Статистика
        info = ttk.LabelFrame(left_panel, text="Статистика")
        info.pack(fill="x", padx=10, pady=5)

        ttk.Label(info, text="Поколение:").grid(row=0, column=0, sticky="w", padx=10, pady=2)
        self.generation_label = ttk.Label(info, text="-")
        self.generation_label.grid(row=0, column=1, sticky="w", padx=5)

        ttk.Label(info, text="Лучшее значение:").grid(row=1, column=0, sticky="w", padx=10, pady=2)
        self.best_label = ttk.Label(info, text="-")
        self.best_label.grid(row=1, column=1, sticky="w", padx=5)

        ttk.Label(info, text="Среднее значение:").grid(row=2, column=0, sticky="w", padx=10, pady=2)
        self.avg_label = ttk.Label(info, text="-")
        self.avg_label.grid(row=2, column=1, sticky="w", padx=5)

        ttk.Label(info, text="Худшее значение:").grid(row=3, column=0, sticky="w", padx=10, pady=2)
        self.worst_label = ttk.Label(info, text="-")
        self.worst_label.grid(row=3, column=1, sticky="w", padx=5)

        ttk.Label(info, text="Вес МОД:").grid(row=4, column=0, sticky="w", padx=10, pady=2)
        self.weight_label = ttk.Label(info, text="-")
        self.weight_label.grid(row=4, column=1, sticky="w", padx=5)
        
        self.best_mst_weight = float("+inf")

        # Поле под граф (увеличил высоту)
        graph_frame = ttk.LabelFrame(left_panel, text="Граф и МОД")
        graph_frame.pack(fill="both", expand=True, padx=10, pady=5)

        self.canvas = tk.Canvas(graph_frame, bg="white", height=500)  # Увеличил высоту
        self.canvas.pack(fill="both", expand=True)

        self.drawer = GraphDrawer(self.canvas)
        
        log_frame = ttk.LabelFrame(right_panel, text="Лог")
        log_frame.pack(fill="both", expand=True, padx=10, pady=5)

        self.log = ScrolledText(log_frame, height=20, width=60)  # Увеличил размер
        self.log.pack(fill="both", expand=True)

        self.ga = None
        self.all_edges = []

    def load_in_ga(self):
        """Загрузка графа в генетический алгоритм"""
        if self.graph_manager.get_graph() is None:
            messagebox.showerror("Ошибка", "Сначала загрузите или сгенерируйте граф!")
            return False
        
        self.max_generations = int(self.generations.get())
        
        self.ga = GeneticAlgorithmMST(
            self.graph_manager.get_graph(),
            population_size=int(self.population.get()),
            crossover_rate=float(self.crossover.get()),
            mutation_rate=float(self.mutation.get()),
            selection_type=self.selection.get(),
            tournament_size=int(self.tournament_size.get()),
            crossover_type=self.crossover_method.get(),
            mutation_type=self.mutation_method.get(),
            elitism_count=int(self.elitism.get())
        )
        
        self.all_edges = self.graph_manager.get_edges()
        self.current_step = 0
        
        return True

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
            num_vertices = self.graph_manager.get_graph().num_vertices

            self.drawer.clear()
            self.drawer.draw(num_vertices, self.graph_manager.get_edges())

            self.log.insert("end", f"Загружен граф:\n{filename}\n")
            self.log.see("end")
            
            self.all_edges = self.graph_manager.get_edges()
            self._enable_controls(False)

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
            
            self.all_edges = self.graph_manager.get_edges()
            self._enable_controls(False)
            window.destroy()

        ttk.Button(window, text="Сгенерировать", command=create).grid(row=4, column=0, pady=20)
        ttk.Button(window, text="Отмена", command=window.destroy).grid(row=4, column=1)

    def manual_input_graph(self):
        window = tk.Toplevel(self.root)
        window.title("Ввод графа вручную")
        window.geometry("450x400")
        
        instruction = (
            "Введите ребра в формате: u v w\n"
            "Где u и v — номера вершин (целые числа), w — вес.\n"
            "Каждое ребро с новой строки. Пример:\n"
            "1 2 5.5\n1 3 10\n2 3 3"
        )
        ttk.Label(window, text=instruction, justify="left", font=("Consolas", 9)).pack(padx=10, pady=5, fill="x")
        
        txt_input = ScrolledText(window, height=12, width=50)
        txt_input.pack(padx=10, pady=5, fill="both", expand=True)
        
        txt_input.insert("1.0", "1 2 10\n1 3 15\n2 3 5\n3 4 20")

        def parse_and_save():
            text_content = txt_input.get("1.0", "end-1c").strip()
            if not text_content:
                messagebox.showwarning("Предупреждение", "Поле ввода пустое!")
                return
            
            edges = []
            
            try:
                for line_num, line in enumerate(text_content.split('\n'), 1):
                    line = line.strip()
                    if not line:
                        continue
                    
                    parts = line.split()
                    if len(parts) != 3:
                        raise ValueError(f"Строка {line_num}: должно быть ровно 3 значения (u, v, w). Получено: {len(parts)}")
                    
                    u = int(parts[0])
                    v = int(parts[1])
                    w = float(parts[2])
                    
                    edges.append((u, v, w))
            
            except ValueError as e:
                messagebox.showerror("Ошибка парсинга", f"Некорректный формат данных!\n{str(e)}")
                return

            if not edges:
                messagebox.showwarning("Предупреждение", "Не удалось распознать ни одного ребра.")
                return
            
            self.graph_manager.load_from_tuple(edges)
            
            self.drawer.clear()
            self.drawer.draw(self.graph_manager.get_graph().num_vertices, self.graph_manager.get_edges())
            
            self.log.insert("end", f"Граф введен вручную: вершин={self.graph_manager.get_graph().num_vertices}, ребер={len(edges)}.\n")
            self.log.see("end")
            
            self.all_edges = self.graph_manager.get_edges()
            self._enable_controls(False)
            window.destroy()

        btn_frame = ttk.Frame(window)
        btn_frame.pack(fill="x", pady=10)
        
        ttk.Button(btn_frame, text="Применить", command=parse_and_save).pack(side="left", padx=20)
        ttk.Button(btn_frame, text="Отмена", command=window.destroy).pack(side="right", padx=20)

    def reset(self):
        """Полный сброс"""
        self.algorithm_running = False
        self.is_playing = False
        self.current_step = 0

        self.log.insert("end", "Сброс состояния.\n")
        self.log.see("end")

        self.drawer.clear()
        self.best_label.config(text="-")
        self.avg_label.config(text="-")
        self.worst_label.config(text="-")
        self.generation_label.config(text="-")
        self.weight_label.config(text="-")
        
        self._enable_controls(False)
        
        if self.ga:
            self.ga = None

    def show_stats(self):
        """Обновление статистики"""
        if not self.ga:
            return
            
        stats = self.ga.get_statistics()
        if stats:
            self.generation_label.config(text=stats.get("generation", "-"))
            self.best_label.config(text=f"{stats.get('best_fitness_history', [0])[-1]:.2f}")
            self.avg_label.config(text=f"{stats.get('avg_fitness_history', [0])[-1]:.2f}")
            self.worst_label.config(text=f"{stats.get('worst_fitness_history', [0])[-1]:.2f}")
            
            # Получаем вес лучшего решения
            best_solution = self.ga.get_best_solution()
            if best_solution:
                mst_weight: int = best_solution['weight']
                self.weight_label.config(text=f"{mst_weight:.2f}")
                
                if mst_weight < self.best_mst_weight:
                    self.best_mst_weight = mst_weight
                    self.log.insert("end", f"Найдено новое решение: Вес: {mst_weight}, поколение: {stats["generation"]}\n")
                    self.log.see("end")

    def update_plot(self):
        """Обновление отображения графа"""
        if not self.ga or self.ga.generation == 0:
            self.drawer.draw(
                vertices_count=self.graph_manager.get_graph().num_vertices,
                edges_list=self.all_edges,
                mst_edges=None,
                reset_layout=False
            )
            return

        best_solution = self.ga.get_best_solution()
        current_mst = best_solution['edges']
        
        self.show_stats()
        
        self.drawer.draw(
            vertices_count=self.graph_manager.get_graph().num_vertices,
            edges_list=self.all_edges,
            mst_edges=current_mst,
            reset_layout=False
        )
        
        # Обновляем состояние кнопок
        self.btn_back.configure(state="normal" if self.ga.generation > 1 else "disabled")
        self.btn_skip.configure(state="normal" if self.ga.generation < self.max_generations else "disabled")

    def _enable_controls(self, enabled):
        """Включение/выключение кнопок управления"""
        state = "normal" if enabled else "disabled"
        self.btn_play.configure(state=state)
        self.btn_next.configure(state=state)
        self.btn_back.configure(state=state)
        self.btn_skip.configure(state=state)

    def run_algorithm(self):
        """Запуск алгоритма (полный прогон)"""
        if self.algorithm_running:
            return
            
        self.algorithm_running = True
        self.log.insert("end", "Запуск алгоритма...\n")
        self.log.see("end")

        try:
            if not self.load_in_ga():
                self.algorithm_running = False
                return
            
            self._enable_controls(True)
            
            # Запускаем полный прогон
            self.ga.run(1)
            
            self.update_plot()
            self.is_playing = False
            
        except Exception as e:
            messagebox.showerror("Ошибка", str(e))
            self.log.insert("end", f"Ошибка: {e}\n")
        finally:
            self.algorithm_running = False

    def next_step(self):
        """Выполнить один шаг эволюции"""
            
        self.ga.step()
        self.update_plot()
        self.log.insert("end", f"Поколение {self.ga.generation} завершено\n")
        self.log.see("end")

    def prev_step(self):
        """Откатить на один шаг назад"""
        if not self.ga or self.ga.generation <= 1:
            return
            
        self.ga.rollback(steps=1)
        self.update_plot()
        self.log.insert("end", f"Откат к поколению {self.ga.generation}\n")
        self.log.see("end")

    def skip_to_end(self):
        """Пропустить до конца"""
        if not self.ga or self.ga.generation >= self.max_generations:
            return
            
        self.is_playing = False
        self.btn_play.configure(text="▶ Авто-запуск")
        
        remaining = self.max_generations - self.ga.generation
        self.ga.run(max_generations=remaining)
        self.update_plot()
        
        self.log.insert("end", f"Пропуск к поколению {self.ga.generation}\n")
        self.log.see("end")

    def toggle_play(self):
        """Запуск/остановка автопроигрывания"""
        if not self.ga:
            return
            
        if self.is_playing:
            self.is_playing = False
            self.btn_play.configure(text="▶ Авто-запуск")
        else:
            self.is_playing = True
            self.btn_play.configure(text="⏸ Пауза")
            self.play_loop()

    def play_loop(self):
        """Цикл автопроигрывания"""
        if self.is_playing:
            self.next_step()
            self.root.after(500, self.play_loop)  # Исправлено: self.root вместо self.window
        else:
            self.is_playing = False
            self.btn_play.configure(text="▶ Авто-запуск")
