"""Interface Tkinter da calculadora acessível."""

from __future__ import annotations

import tkinter as tk
from tkinter import ttk

from src.accessibility.sounds import SoundManager
from src.accessibility.speech import TTSTk
from src.core.calculator_engine import CalcEngine
from src.core.utils import friendly_expression, format_number, spoken_number
from src.ui.themes import apply_base_theme


class CalculatorApp:
    KEY_SPEECH = {
        "+": "mais",
        "-": "menos",
        "*": "vezes",
        "/": "dividido",
        "(": "abre parênteses",
        ")": "fecha parênteses",
        ".": "ponto",
        "=": "igual",
        "^": "elevado a",
        "sqrt": "raiz quadrada",
        "pi": "pi",
        "sin": "seno",
        "cos": "cosseno",
        "tan": "tangente",
        "asin": "arco seno",
        "acos": "arco cosseno",
        "atan": "arco tangente",
        "ln": "logaritmo natural",
        "log": "logaritmo",
        "exp": "exponencial",
        "fact": "fatorial",
        "nCr": "combinação",
        "nPr": "permuta",
        "ANS": "resultado anterior",
        "C": "limpar",
        "⌫": "apagar",
    }

    DIGIT_NAMES = {
        "0": "zero",
        "1": "um",
        "2": "dois",
        "3": "três",
        "4": "quatro",
        "5": "cinco",
        "6": "seis",
        "7": "sete",
        "8": "oito",
        "9": "nove",
    }

    def __init__(self, root: tk.Tk, assets_dir=None) -> None:
        self.root = root
        self.root.title("Calculadora Científica Acessível")
        self.root.geometry("560x760")

        apply_base_theme(root)

        self.tts = TTSTk(root, rate=180, volume=1.0)
        self.engine = CalcEngine()
        self.sound_manager = SoundManager(assets_dir=assets_dir)

        self.beep_enabled = tk.BooleanVar(value=self.sound_manager.available)
        self.rate_var = tk.IntVar(value=180)
        self.fast_digits_enabled = tk.BooleanVar(value=True)
        self.fast_digits_mult = tk.DoubleVar(value=2.0)

        self._build_ui()
        self._bind_keys()
        self.tts.set_rate(self.rate_var.get())

    # ---------- UI ----------
    def _build_ui(self) -> None:
        main = ttk.Frame(self.root, padding=10)
        main.pack(fill="both", expand=True)

        self.expr_var = tk.StringVar()
        expr_entry = ttk.Entry(main, textvariable=self.expr_var, font=("Segoe UI", 20))
        expr_entry.pack(fill="x", pady=(0, 8))
        expr_entry.focus_set()

        self.res_var = tk.StringVar(value="Resultado: ")
        res_label = ttk.Label(main, textvariable=self.res_var, font=("Segoe UI", 16))
        res_label.pack(fill="x", pady=(0, 8))

        topbar = ttk.Frame(main)
        topbar.pack(fill="x", pady=(0, 8))

        self.mode_btn = ttk.Button(topbar, text="Modo: Graus", command=self.toggle_mode)
        self.mode_btn.pack(side="left")

        ttk.Button(topbar, text="Ler expressão", command=self.read_expression).pack(side="left", padx=6)
        ttk.Button(topbar, text="Limpar (C)", command=lambda: self._press("C")).pack(side="left")
        ttk.Button(topbar, text="Apagar (⌫)", command=lambda: self._press("⌫")).pack(side="left", padx=6)

        beep_chk = ttk.Checkbutton(topbar, text="Beep", variable=self.beep_enabled)
        beep_chk.pack(side="left", padx=6)

        voice_frame = ttk.LabelFrame(main, text="Voz e velocidade")
        voice_frame.pack(fill="x", pady=(6, 8))

        row = ttk.Frame(voice_frame)
        row.pack(fill="x", pady=4)
        ttk.Label(row, text="Velocidade da fala:").pack(side="left")
        rate_scale = ttk.Scale(row, from_=50, to=300, variable=self.rate_var, command=self._on_rate_change)
        rate_scale.pack(side="left", fill="x", expand=True, padx=8)
        self.rate_label = ttk.Label(row, text=f"{self.rate_var.get()} wpm")
        self.rate_label.pack(side="left")

        row2 = ttk.Frame(voice_frame)
        row2.pack(fill="x", pady=4)
        fast_chk = ttk.Checkbutton(
            row2,
            text="Acelerar leitura de dígitos",
            variable=self.fast_digits_enabled,
        )
        fast_chk.pack(side="left")
        ttk.Label(row2, text="Multiplicador:").pack(side="left", padx=(12, 4))
        fast_scale = ttk.Scale(
            row2,
            from_=1.0,
            to=3.0,
            variable=self.fast_digits_mult,
            command=lambda _=None: self._update_fast_label(),
        )
        fast_scale.pack(side="left", fill="x", expand=True, padx=8)
        self.fast_label = ttk.Label(row2, text=f"{self.fast_digits_mult.get():.1f}x")
        self.fast_label.pack(side="left")

        ttk.Button(voice_frame, text="Testar voz", command=lambda: self.tts.say("Teste de voz. Um dois três.")).pack(pady=6)

        grid = ttk.Frame(main)
        grid.pack(fill="both", expand=True)

        buttons = [
            [("sin", "sin("), ("cos", "cos("), ("tan", "tan("), ("π", "pi")],
            [("asin", "asin("), ("acos", "acos("), ("atan", "atan("), ("^", "^")],
            [("ln", "ln("), ("log", "log("), ("exp", "exp("), ("√", "sqrt(")],
            [("nCr", "nCr("), ("nPr", "nPr("), ("!", "fact("), ("ANS", "ANS")],
            [("7", "7"), ("8", "8"), ("9", "9"), ("÷", "÷")],
            [("4", "4"), ("5", "5"), ("6", "6"), ("×", "×")],
            [("1", "1"), ("2", "2"), ("3", "3"), ("-", "-")],
            [("0", "0"), (".", "."), ("(", "("), (")", ")")],
            [("C", "C"), ("⌫", "⌫"), ("=", "="), ("+", "+")],
        ]

        for r_index, row_def in enumerate(buttons):
            for c_index, (label, token) in enumerate(row_def):
                button = ttk.Button(grid, text=label, command=lambda t=token: self._press(t))
                button.grid(row=r_index, column=c_index, sticky="nsew", padx=3, pady=3)
        for idx in range(4):
            grid.columnconfigure(idx, weight=1)
        for idx in range(len(buttons)):
            grid.rowconfigure(idx, weight=1)

        hist_frame = ttk.LabelFrame(main, text="Histórico")
        hist_frame.pack(fill="both", expand=True, pady=(8, 0))
        self.history = tk.Listbox(hist_frame, font=("Consolas", 12), height=6)
        self.history.pack(fill="both", expand=True)

        tips = ttk.Label(
            main,
            text="Atalhos: Enter=Igual | Backspace=Apagar | Esc=C | F9=Graus/Radianos",
            font=("Segoe UI", 10),
            foreground="#555",
        )
        tips.pack(fill="x", pady=(6, 0))

    def _update_fast_label(self) -> None:
        self.fast_label.config(text=f"{self.fast_digits_mult.get():.1f}x")

    def _on_rate_change(self, _event) -> None:
        value = int(self.rate_var.get())
        self.rate_label.config(text=f"{value} wpm")
        self.tts.set_rate(value)

    def _bind_keys(self) -> None:
        self.root.bind("<Return>", lambda event: self._press("="))
        self.root.bind("<KP_Enter>", lambda event: self._press("="))
        self.root.bind("<BackSpace>", lambda event: self._press("⌫"))
        self.root.bind("<Escape>", lambda event: self._press("C"))
        self.root.bind("<F9>", lambda event: self.toggle_mode())

        for char in "0123456789.+-*/()^":
            self.root.bind(char, self._key_insert)
        self.root.bind("x", lambda event: self._press("×"))
        self.root.bind("X", lambda event: self._press("×"))

    # ---------- Lógica de interação ----------
    def _key_insert(self, event) -> None:
        char = event.char
        if char:
            self._insert_text(char)
            self._speak_key(char)

    def _insert_text(self, text: str) -> None:
        self._beep()
        current = self.expr_var.get()
        self.expr_var.set(current + text)

    def _beep(self) -> None:
        self.sound_manager.play_beep(enabled=self.beep_enabled.get())

    def _speak_key(self, token: str) -> None:
        spoken = self.KEY_SPEECH.get(token, token)
        rate_override = None

        if token.isdigit():
            spoken = self.DIGIT_NAMES.get(token, token)
            if self.fast_digits_enabled.get():
                rate_override = int(self.rate_var.get() * float(self.fast_digits_mult.get()))
        elif token == ".":
            spoken = "ponto"
            if self.fast_digits_enabled.get():
                rate_override = int(self.rate_var.get() * float(self.fast_digits_mult.get()))
        elif token in {"×", "÷"}:
            spoken = "vezes" if token == "×" else "dividido"

        self.tts.say(spoken, rate=rate_override)

    def _press(self, token: str) -> None:
        self._beep()
        self._speak_key(token)

        if token == "C":
            self.expr_var.set("")
            self.res_var.set("Resultado: ")
            return

        if token == "⌫":
            current = self.expr_var.get()
            if current:
                self.expr_var.set(current[:-1])
            return

        if token == "=":
            self._evaluate()
            return

        if token in {"sin(", "cos(", "tan(", "asin(", "acos(", "atan(", "ln(", "log(", "exp(", "sqrt(", "nCr(", "nPr(", "fact("}:
            self._insert_text(token)
            return

        if token == "π":
            self._insert_text("pi")
            return

        if token == "ANS":
            self._insert_text("ANS")
            return

        if token in {"×", "÷"}:
            self._insert_text("*" if token == "×" else "/")
            return

        self._insert_text(token)

    def _evaluate(self) -> None:
        expression = self.expr_var.get()
        if not expression.strip():
            self.tts.say("expressão vazia")
            return

        try:
            result = self.engine.evaluate(expression)
            formatted = format_number(result)
            self.res_var.set(f"Resultado: {formatted}")
            self.history.insert(tk.END, f"{expression} = {formatted}")
            self.history.see(tk.END)
            self.tts.say(f"resultado: {spoken_number(result)}")
        except Exception:
            self.res_var.set("Erro")
            self.tts.say("erro de cálculo")

    def toggle_mode(self) -> None:
        self.engine.mode = "RAD" if self.engine.mode == "DEG" else "DEG"
        text = "Modo: Radianos" if self.engine.mode == "RAD" else "Modo: Graus"
        self.mode_btn.config(text=text)
        self.tts.say("modo radianos" if self.engine.mode == "RAD" else "modo graus")

    def read_expression(self) -> None:
        expression = self.expr_var.get().strip()
        if not expression:
            self.tts.say("expressão vazia")
            return
        self.tts.say(f"expressão: {friendly_expression(expression)}")
