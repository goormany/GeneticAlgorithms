import tkinter as tk

from gui.main_window import GA_GUI


if __name__ == "__main__":
    root = tk.Tk()
    root.geometry("1100x900")
    app = GA_GUI(root)
    root.mainloop()
