from tkinter import ttk


class ControlButtons:
    """Кнопки управления"""

    def __init__(
        self,
        parent,
        on_generate=None,
        on_load=None,
        on_manual=None,
        on_run=None,
        on_reset=None,
        on_step_back=None,
        on_step_forward=None,
        on_play=None,
        on_skip=None,
    ):

        # Кнопки управления графом
        buttons = ttk.Frame(parent)
        buttons.pack(fill="x", pady=5)

        self.btn_generate = ttk.Button(
            buttons, text="Сгенерировать граф", command=on_generate
        )
        self.btn_generate.pack(side="left", padx=5)

        self.btn_load = ttk.Button(buttons, text="Загрузить граф", command=on_load)
        self.btn_load.pack(side="left", padx=5)

        self.btn_manual = ttk.Button(buttons, text="Ввести вручную", command=on_manual)
        self.btn_manual.pack(side="left", padx=5)

        # Кнопки управления алгоритмом
        algo_buttons = ttk.Frame(parent)
        algo_buttons.pack(fill="x", pady=5)

        self.btn_run = ttk.Button(
            algo_buttons, text="Запустить алгоритм", command=on_run
        )
        self.btn_run.pack(side="left", padx=5)

        self.btn_reset = ttk.Button(algo_buttons, text="Сброс", command=on_reset)
        self.btn_reset.pack(side="left", padx=5)

        # Кнопки пошагового управления
        step_controls = ttk.Frame(parent)
        step_controls.pack(fill="x", pady=5)

        self.btn_back = ttk.Button(
            step_controls, text="Шаг назад", command=on_step_back, state="disabled"
        )
        self.btn_back.pack(side="left", padx=2)

        self.btn_play = ttk.Button(
            step_controls, text="▶️ Авто-запуск", command=on_play, state="disabled"
        )
        self.btn_play.pack(side="left", padx=2)

        self.btn_next = ttk.Button(
            step_controls, text="Шаг вперед", command=on_step_forward, state="disabled"
        )
        self.btn_next.pack(side="left", padx=2)

        self.btn_skip = ttk.Button(
            step_controls, text="⏯️ Пропустить", command=on_skip, state="disabled"
        )
        self.btn_skip.pack(side="left", padx=2)

    def enable_controls(self, enabled):
        """Включение/выключение кнопок управления"""
        state = "normal" if enabled else "disabled"
        self.btn_play.configure(state=state)
        self.btn_next.configure(state=state)
        self.btn_back.configure(state=state)
        self.btn_skip.configure(state=state)

    def enable_step_buttons(self, can_back, can_skip):
        """Включение кнопок шагов"""
        self.btn_back.configure(state="normal" if can_back else "disabled")
        self.btn_skip.configure(state="normal" if can_skip else "disabled")

    def set_play_button_text(self, is_playing):
        """Установка текста кнопки автозапуска"""
        if is_playing:
            self.btn_play.configure(text="⏸ Пауза")
        else:
            self.btn_play.configure(text="▶️ Авто-запуск")
