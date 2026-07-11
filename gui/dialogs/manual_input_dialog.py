import tkinter as tk
from tkinter import ttk, messagebox
from tkinter.scrolledtext import ScrolledText


class ManualInputDialog:
    """Диалог ручного ввода графа"""
    
    def __init__(self, parent, on_save):
        self.parent = parent
        self.on_save = on_save
        
        self.window = tk.Toplevel(parent)
        self.window.title("Ввод графа вручную")
        self.window.geometry("450x400")
        
        instruction = (
            "Введите ребра в формате: u v w\n"
            "Где u и v — номера вершин (целые числа), w — вес.\n"
            "Каждое ребро с новой строки. Пример:\n"
            "1 2 5.5\n1 3 10\n2 3 3"
        )
        ttk.Label(self.window, text=instruction, justify="left", font=("Consolas", 9)).pack(padx=10, pady=5, fill="x")
        
        self.txt_input = ScrolledText(self.window, height=12, width=50)
        self.txt_input.pack(padx=10, pady=5, fill="both", expand=True)
        self.txt_input.insert("1.0", "1 2 10\n1 3 15\n2 3 5\n3 4 20")
        
        btn_frame = ttk.Frame(self.window)
        btn_frame.pack(fill="x", pady=10)
        
        ttk.Button(btn_frame, text="Применить", command=self._parse_and_save).pack(side="left", padx=20)
        ttk.Button(btn_frame, text="Отмена", command=self.window.destroy).pack(side="right", padx=20)
    
    def _parse_and_save(self):
        text_content = self.txt_input.get("1.0", "end-1c").strip()
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
                    raise ValueError(f"Строка {line_num}: должно быть ровно 3 значения")
                
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
        
        self.on_save(edges)
        self.window.destroy()