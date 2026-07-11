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
        
        if self.ga:
            self.ga = None
    
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
        
        self.ga.rollback(steps=1)
        self.update_plot()
        self.log.insert("end", f"Откат к поколению {self.ga.generation}\n")
        self.log.see("end")
    
    def skip_to_end(self):
        if not self.ga or self.ga.generation >= self.max_generations:
            return
        
        self.is_playing = False
        self.controls.set_play_button_text(False)
        
        remaining = self.max_generations - self.ga.generation
        self.ga.run(max_generations=remaining)
        self.update_plot()
        
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

def main():
    root = tk.Tk()
    app = GA_GUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()