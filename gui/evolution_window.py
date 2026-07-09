import tkinter as tk
from tkinter import ttk
from gui.graph_drawer import GraphDrawer
from core.ga_engine import GeneticAlgorithmMST
from models.prufer import PruferCode

class EvolutionWindow:
    def __init__(self, parent, ga: GeneticAlgorithmMST):
        """
        :param parent: Родительское окно (root или main_window)
        :param ga: Объект генетического алгоритма
        """
        self.window = tk.Toplevel(parent)
        self.window.title("Пошаговая визуализация эволюции")
        self.window.geometry("650x600")
        
        self.ga = ga
        self.vertices_count = ga.graph.num_vertices
        self.all_edges = ga.graph.get_edges()
        
        self.current_step = 0
        self.is_playing = False

        graph_frame = ttk.LabelFrame(self.window, text="Текущее состояние МОД")
        graph_frame.pack(fill="both", expand=True, padx=10, pady=5)

        self.canvas = tk.Canvas(graph_frame, bg="white")
        self.canvas.pack(fill="both", expand=True)

        self.drawer = GraphDrawer(self.canvas)

        self.info_label = ttk.Label(self.window, text="", font=("Helvetica", 10, "bold"))
        self.info_label.pack(pady=5)

        control_frame = ttk.Frame(self.window)
        control_frame.pack(fill="x", pady=10)

        self.btn_back = ttk.Button(control_frame, text="Шаг назад", command=self.prev_step)
        self.btn_back.pack(side="left", padx=20, expand=True)

        self.btn_play = ttk.Button(control_frame, text="Запустить", command=self.toggle_play)
        self.btn_play.pack(side="left", padx=20, expand=True)

        self.btn_next = ttk.Button(control_frame, text="Шаг вперед", command=self.next_step)
        self.btn_next.pack(side="left", padx=20, expand=True)

        self.btn_skip = ttk.Button(control_frame, text="Пропустить", command=self.skip_to_end)
        self.btn_skip.pack(side="left", padx=20, expand=True)

        self.update_plot()

    def update_plot(self):
        """ Обновляет холст в зависимости от текущего поколения """
        if self.ga.generation == 0:
            self.info_label.config(text="Алгоритм ещё не запущен.")
            return

        best_solution = self.ga.get_best_solution()
        current_mst = best_solution['edges']

        print(f"\n[EvolutionWindow DEBUG]")
        print(f"  Поколение: {self.ga.generation}")
        print(f"  Код Прюфера: {best_solution['prufer_code']}")
        print(f"  Длина кода: {len(best_solution['prufer_code'])}")
        print(f"  Рёбер в МОД: {len(current_mst)}")
        print(f"  Рёбра: {current_mst}")
        print(f"  Вес: {best_solution['weight']}")
        
        self.info_label.config(
            text=f"Поколение: {self.ga.generation} | Ребер в МОД: {len(current_mst)} | Вес: {best_solution['weight']:.2f}"
        )
        

        # Отрисовка графа
        self.drawer.draw(
            vertices_count=self.vertices_count,
            edges_list=self.all_edges,
            mst_edges=current_mst,
            reset_layout=False
        )

        self.btn_back.configure(state="normal" if self.ga.generation > 1 else "disabled")

    def next_step(self):
        """Выполнить одно поколение эволюции"""
        stats = self.ga.step()
        self.update_plot()
        
        if self.is_playing and self.ga.has_converged():
            self.toggle_play()  

    def prev_step(self):
        """Откатить одно поколение назад"""
        if self.ga.generation > 1:
            self.ga.rollback(steps=1)
            self.update_plot()

    def skip_to_end(self):
        """Запустить алгоритм до сходимости или указанного числа поколений"""
        self.is_playing = False
        
        # Запустить ещё 50 поколений или до сходимости
        self.ga.run(max_generations=50)
        self.update_plot()

    def toggle_play(self):
        """ Запуск автопроигрывания эволюции поколений """
        if self.is_playing:
            self.is_playing = False
            self.btn_play.config(text="▶ Запустить")
        else:
            self.is_playing = True
            self.btn_play.config(text="⏸ Пауза")
            self.play_loop()

    def play_loop(self):
        """ Цикл автоматического выполнения поколений """
        if self.is_playing:
            self.next_step()
            # Скорость воспроизведения (500 мс между поколениями)
            self.window.after(500, self.play_loop)
