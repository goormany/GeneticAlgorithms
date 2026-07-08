import networkx as nx
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from tkinter import Canvas

class GraphDrawer:
    def __init__(self, canvas_widget: Canvas):
        self.canvas = canvas_widget
        self.pos = None

        # Создаем фигуру Matplotlib
        self.fig, self.ax = plt.subplots(figsize=(6, 5), dpi=100)
        self.fig.patch.set_facecolor('white')
        self.ax.set_facecolor('white')

        # Интегрируем в tk.Canvas
        self.plot_canvas = FigureCanvasTkAgg(self.fig, master=self.canvas)
        self.plot_widget = self.plot_canvas.get_tk_widget()
        self.plot_widget.pack(fill="both", expand=True)

    def draw(
        self,
        vertices_count: int,
        edges_list: list[tuple[int, int, float]],
        mst_edges: list[tuple[int, int]] = None,
        reset_layout: bool = False
    ):
        self.ax.clear()
        self.ax.axis('off')

        G = nx.Graph()
        G.add_nodes_from(range(1, vertices_count + 1))

        for u, v, w in edges_list:
            G.add_edge(u, v, weight=w)

        if reset_layout or self.pos is None or len(self.pos) != vertices_count:
            if vertices_count <= 10:
                k = 2.5
            elif vertices_count <= 20:
                k = 2.0
            elif vertices_count <= 50:
                k = 1.5
            else:
                k = 1.2
            
            self.pos = nx.spring_layout(G, seed=42, k=k, iterations=100)

        # Рисуем ребра
        nx.draw_networkx_edges(G, self.pos, ax=self.ax, edge_color='lightgray', width=1.5)

        # Если передан список ребер МОД — выделяем их
        if mst_edges:
            mst_set = set(tuple(sorted(e[:2])) for e in mst_edges)
            current_mst_edges = [e for e in G.edges() if tuple(sorted(e)) in mst_set]
            
            nx.draw_networkx_edges(
                G, self.pos, ax=self.ax, 
                edgelist=current_mst_edges, edge_color='crimson', width=3.5
            )

        # Рисуем вершины
        nx.draw_networkx_nodes(G, self.pos, ax=self.ax, node_color='#1f77b4', node_size=400)

        # Подписи к вершинам
        nx.draw_networkx_labels(G, self.pos, ax=self.ax, font_color='white', font_size=10, font_weight='bold')

        # Рисуем веса ребер
        edge_labels = nx.get_edge_attributes(G, 'weight')
        nx.draw_networkx_edge_labels(
            G, self.pos, edge_labels=edge_labels, ax=self.ax, 
            font_size=9, label_pos=0.5, bbox=dict(boxstyle="round,pad=0.2", facecolor="white", alpha=0.7)
        )

        self.fig.tight_layout()
        self.plot_canvas.draw()

    def clear(self):
        self.ax.clear()
        self.ax.axis('off')
        self.pos = None
        self.plot_canvas.draw()