import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from tkinter.scrolledtext import ScrolledText

from gui.graph_drawer import GraphDrawer
from gui.controls.control_buttons import ControlButtons
from gui.controls.parameter_frame import ParameterFrame
from gui.controls.statistics_frame import StatisticsFrame
from gui.dialogs.generate_graph_dialog import GenerateGraphDialog
from gui.dialogs.manual_input_dialog import ManualInputDialog

from data.graph_manager import GraphManager
from core.ga_engine import GeneticAlgorithmMST
from models.graph import Graph


class GA_GUI:
    
    def __init__(self, root):
        self.graph_manager = GraphManager()
        self.root = root
        self.root.title("Генетический алгоритм поиска МОД")
        self.algorithm_running = False
        
        # Атрибуты для пошагового управления
        self.current_step = 0
        self.is_playing = False
        self.max_generations = 200
        self.best_mst_weight = float("inf")
        
        self._create_layout()
        
        self.ga = None
        self.all_edges = []
    
    def _create_layout(self):
        main_panel = ttk.Frame(self.root)
        main_panel.pack(fill="both", expand=True)
        
        left_panel = ttk.Frame(main_panel)
        left_panel.pack(side="left", fill="both", expand=True)
        
        right_panel = ttk.Frame(main_panel, width=500)
        right_panel.pack(side="right", fill="both", expand=False)
        right_panel.pack_propagate(False)
        
        # Верхняя часть - лог
        log_frame = ttk.LabelFrame(right_panel, text="Лог")
        log_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        self.log = ScrolledText(log_frame, height=15, width=60)
        self.log.pack(fill="both", expand=True)
        
        # Нижняя часть - статистика с графиком
        self.stats = StatisticsFrame(right_panel)
        
        # Левая панель
        self.params = ParameterFrame(left_panel)
        
        self.controls = ControlButtons(
            left_panel,
            on_generate=self._show_generate_dialog,
            on_load=self.load_graph,
            on_manual=self._show_manual_dialog,
            on_run=self.run_algorithm,
            on_reset=self.reset,
            on_step_back=self.prev_step,
            on_step_forward=self.next_step,
            on_play=self.toggle_play,
            on_skip=self.skip_to_end
        )
        
        graph_frame = ttk.LabelFrame(left_panel, text="Граф и МОД")
        graph_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        # Панель выбора особи из популяции
        selector_frame = ttk.Frame(graph_frame)
        selector_frame.pack(fill="x", padx=5, pady=(5, 0))
        
        ttk.Label(selector_frame, text="Особь:").pack(side="left", padx=(0, 5))
        self.individual_var = tk.StringVar()
        self.individual_combo = ttk.Combobox(
            selector_frame,
            textvariable=self.individual_var,
            state="readonly",
            width=40
        )
        self.individual_combo.pack(side="left", fill="x", expand=True)
        self.individual_combo.bind("<<ComboboxSelected>>", self._on_individual_selected)
        self.individual_info_label = ttk.Label(selector_frame, text="")
        self.individual_info_label.pack(side="left", padx=5)
        # Храним список решений для быстрого доступа по индексу из combobox
        self.individual_solutions = []
        
        self.canvas = tk.Canvas(graph_frame, bg="white", height=500)
        self.canvas.pack(fill="both", expand=True)
        
        self.drawer = GraphDrawer(self.canvas)
    
    def _show_generate_dialog(self):
        GenerateGraphDialog(self.root, self._on_generate_graph)
    
    def _show_manual_dialog(self):
        ManualInputDialog(self.root, self._on_manual_input)
    
    def _on_generate_graph(self, n, p, w_min, w_max):
        self.graph_manager.generate_random_graph(n, p, w_min, w_max)
        self._update_after_graph_load(f"Создание графа: вершин={n}, p={p}, вес=[{w_min}, {w_max}]")
    
    def _on_manual_input(self, edges):
        self.graph_manager.load_from_tuple(edges)
        num_vertices = self.graph_manager.get_graph().num_vertices
        self._update_after_graph_load(f"Граф введен вручную: вершин={num_vertices}, ребер={len(edges)}")
    
    def _update_after_graph_load(self, message):
        num_vertices = self.graph_manager.get_graph().num_vertices
        self.drawer.clear()
        self.drawer.draw(num_vertices, self.graph_manager.get_edges())
        self.log.insert("end", f"{message}\n")
        self.log.see("end")
        self.all_edges = self.graph_manager.get_edges()
        self.controls.enable_controls(False)
    
    def load_graph(self):
        filename = filedialog.askopenfilename(
            filetypes=[("Текстовые файлы", "*.txt"), ("Все файлы", "*.*")]
        )
        if filename:
            self.graph_manager.load(filename)
            num_vertices = self.graph_manager.get_graph().num_vertices
            self.drawer.clear()
            self.drawer.draw(num_vertices, self.graph_manager.get_edges())
            self.log.insert("end", f"Загружен граф: {filename}\n")
            self.log.see("end")
            self.all_edges = self.graph_manager.get_edges()
            self.controls.enable_controls(False)
    
    def load_in_ga(self):
        if self.graph_manager.get_graph() is None:
            messagebox.showerror("Ошибка", "Сначала загрузите или сгенерируйте граф!")
            return False
        
        params = self.params.get_parameters()
        self.max_generations = params.pop('generations')
        
        self.ga = GeneticAlgorithmMST(
            self.graph_manager.get_graph(),
            **params
        )
        
        self.all_edges = self.graph_manager.get_edges()
        self.current_step = 0
        self.best_mst_weight = float("inf")
        
        # Сбрасываем график при загрузке нового графа
        self.stats.reset()
        
        return True
    
    def reset(self):
        self.algorithm_running = False
        self.is_playing = False
        self.current_step = 0
        
        self.log.insert("end", "Сброс состояния.\n")
        self.log.see("end")
        
        self.drawer.clear()
        self.stats.reset()  # Сбрасываем статистику и график
        self.controls.enable_controls(False)
        self.controls.set_play_button_text(False)
        self._populate_individual_selector()
        
        if self.ga:
            self.ga = None
    
    def _populate_individual_selector(self):
        """Заполняет комбобокс списком особей из текущей популяции"""
        if not self.ga:
            self.individual_combo.configure(values=[])
            self.individual_combo.set("")
            self.individual_info_label.configure(text="")
            self.individual_solutions = []
            return
        
        self.individual_solutions = self.ga.get_all_solutions()
        
        labels = []
        for sol in self.individual_solutions:
            weight_str = f"{sol['weight']:.2f}"
            labels.append(f"#{sol['rank']} (вес: {weight_str}) | код: {'-'.join(map(str, sol['prufer_code']))}")
        
        self.individual_combo.configure(values=labels)
        
        # Сбросить выбор, если он вышел за пределы
        if self.individual_var.get():
            try:
                idx = labels.index(self.individual_var.get())
                self.individual_var.set(labels[idx])
            except ValueError:
                self.individual_var.set("")
                self.individual_info_label.configure(text="")
    
    def _on_individual_selected(self, event=None):
        """Обработчик выбора особи из комбобокса"""
        selected_label = self.individual_var.get()
        if not selected_label or not self.individual_solutions:
            return
        
        try:
            idx = self.individual_combo.cget("values").index(selected_label)
            if 0 <= idx < len(self.individual_solutions):
                sol = self.individual_solutions[idx]
                self.individual_info_label.configure(
                    text=f"вес: {sol['weight']:.2f}"
                )
                self._redraw_with_selected(sol['edges'])
        except ValueError:
            pass
    
    def _redraw_with_selected(self, selected_edges=None):
        """Перерисовывает граф с учётом выбранной особи и лучшей МОД"""
        if not self.ga or self.ga.generation == 0:
            self.drawer.draw(
                vertices_count=self.graph_manager.get_graph().num_vertices,
                edges_list=self.all_edges,
                mst_edges=None,
                selected_edges=selected_edges,
                reset_layout=False
            )
            return
        
        best_solution = self.ga.get_best_solution()
        current_mst = best_solution['edges']
        
        self.show_stats()
        
        if self._is_valid_solution(best_solution):
            self.drawer.draw(
                vertices_count=self.graph_manager.get_graph().num_vertices,
                edges_list=self.all_edges,
                mst_edges=current_mst,
                selected_edges=selected_edges,
                reset_layout=False
            )
        else:
            self.drawer.draw(
                vertices_count=self.graph_manager.get_graph().num_vertices,
                edges_list=self.all_edges,
                mst_edges=None,
                selected_edges=selected_edges,
                reset_layout=False
            )
    
    def show_stats(self):
        if not self.ga:
            return
        
        stats = self.ga.get_statistics()
        if stats:
            self.stats.update_stats(stats)
            
            best_solution = self.ga.get_best_solution()
            if best_solution:
                mst_weight = best_solution['weight']
                generation = stats.get('generation', 0)
                
                # Проверяем, валидно ли решение
                # Считаем валидным, если вес меньше определенного порога
                # (например, если граф имеет N вершин, максимальный вес МОД не может быть больше (N-1) * max_weight)
                is_valid = self._is_valid_solution(best_solution)
                
                # Обновляем вес и график только для валидных решений
                self.stats.update_weight(mst_weight, generation, is_valid)
                
                if is_valid and mst_weight < self.best_mst_weight:
                    self.best_mst_weight = mst_weight
                    self.log.insert("end", f"Найдено новое решение: Вес: {mst_weight}, поколение: {generation}\n")
                    self.log.see("end")

    def _is_valid_solution(self, solution):
        """Проверка валидности решения"""
        # Проверяем, что количество ребер равно n-1
        num_vertices = self.graph_manager.get_graph().num_vertices
        
        return Graph.is_tree(num_vertices, solution['edges'], self.ga.graph)
    
    def update_plot(self):
        # Обновляем список особей в селекторе
        self._populate_individual_selector()
        
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
        
        # Проверяем валидность перед отрисовкой
        if self._is_valid_solution(best_solution):
            self.drawer.draw(
                vertices_count=self.graph_manager.get_graph().num_vertices,
                edges_list=self.all_edges,
                mst_edges=current_mst,
                reset_layout=False
            )
        else:
            # Если невалидно, рисуем только граф без МОД
            self.drawer.draw(
                vertices_count=self.graph_manager.get_graph().num_vertices,
                edges_list=self.all_edges,
                mst_edges=None,
                reset_layout=False
            )
        
        self.controls.enable_step_buttons(
            can_back=self.ga.generation > 1,
            can_skip=self.ga.generation < self.max_generations
        )
    
    def run_algorithm(self):
        if self.algorithm_running:
            return
        
        self.algorithm_running = True
        self.log.insert("end", "Запуск алгоритма...\n")
        self.log.see("end")
        
        try:
            if not self.load_in_ga():
                self.algorithm_running = False
                return
            
            # Сбрасываем график перед запуском
            self.stats.reset()
            self.best_mst_weight = float("inf")
            
            self.controls.enable_controls(True)
            self.ga.run(1)
            self.update_plot()
            self.is_playing = False
            
        except Exception as e:
            messagebox.showerror("Ошибка", str(e))
            self.log.insert("end", f"Ошибка: {e}\n")
        finally:
            self.algorithm_running = False
    
    def next_step(self):
        if not self.ga:
            return
        
        self.ga.step()
        self.update_plot()
        self.log.insert("end", f"Поколение {self.ga.generation} завершено\n")
        self.log.see("end")
    
    def prev_step(self):
        if not self.ga or self.ga.generation <= 1:
            return
        
        old_generation = self.ga.generation
        
        self.ga.rollback(steps=1)
        
        self.stats.truncate(self.ga.generation - 1)
        
        self.update_plot()
        self.log.insert("end", f"Откат с поколения {old_generation} к поколению {self.ga.generation}\n")
        self.log.see("end")
    
    def skip_to_end(self):
        if not self.ga or self.ga.generation >= self.max_generations:
            return
        
        self.is_playing = False
        self.controls.set_play_button_text(False)
        
        start_gen = self.ga.generation
        remaining = self.max_generations - start_gen
        
        # Сохраняем текущую длину истории fitness до запуска
        history_len_before = len(self.ga.best_fitness_history)
        
        self.ga.run(max_generations=remaining)
        
        # Собираем данные для пакетного обновления графика
        max_possible = self.ga.max_possible_tree_weight
        weight_data = []
        for gen_idx in range(history_len_before, len(self.ga.best_fitness_history)):
            weight = self.ga.best_fitness_history[gen_idx]
            is_valid = weight < max_possible * 2
            if is_valid:
                weight_data.append((gen_idx, weight, True))
                
                if weight < self.best_mst_weight:
                    self.best_mst_weight = weight
                    self.log.insert("end", f"Найдено новое решение: Вес: {weight:.2f}, поколение: {gen_idx}\n")
                    self.log.see("end")
        
        if weight_data:
            self.stats.bulk_update_weights(weight_data)
        
        stats = self.ga.get_statistics()
        if stats:
            self.stats.update_stats(stats)
        
        # Обновляем комбобокс особей
        self._populate_individual_selector()
        
        # Отрисовка графа МОД
        best_solution = self.ga.get_best_solution()
        current_mst = best_solution['edges']
        
        self.stats.weight_label.config(text=f"{best_solution["weight"]:.2f}")
        
        if self._is_valid_solution(best_solution):
            self.drawer.draw(
                vertices_count=self.graph_manager.get_graph().num_vertices,
                edges_list=self.all_edges,
                mst_edges=current_mst,
                reset_layout=False
            )
        else:
            self.drawer.draw(
                vertices_count=self.graph_manager.get_graph().num_vertices,
                edges_list=self.all_edges,
                mst_edges=None,
                reset_layout=False
            )
        
        self.controls.enable_step_buttons(
            can_back=self.ga.generation > 1,
            can_skip=self.ga.generation < self.max_generations
        )
        
        self.log.insert("end", f"Пропуск к поколению {self.ga.generation}\n")
        self.log.see("end")
    
    def toggle_play(self):
        if not self.ga:
            return
        
        if self.is_playing:
            self.is_playing = False
            self.controls.set_play_button_text(False)
        else:
            self.is_playing = True
            self.controls.set_play_button_text(True)
            self.play_loop()
    
    def play_loop(self):
        if self.is_playing:
            self.next_step()
            self.root.after(500, self.play_loop)
        else:
            self.is_playing = False
            self.controls.set_play_button_text(False)
