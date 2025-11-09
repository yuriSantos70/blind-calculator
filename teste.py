import tkinter as tk
from tkinter import ttk
import math
import re

# ======= TTS no thread principal (pyttsx3 + Tkinter) =======
import pyttsx3

class TTSTk:
    """
    TTS integrado ao loop do Tkinter (thread principal).
    Suporta:
      - set_rate() dinâmico
      - rate por fala (say(text, rate=?))
    """
    def __init__(self, root, rate=180, volume=1.0, voice_hint_ptbr=True, pump_ms=15):
        self.root = root
        self.engine = pyttsx3.init(driverName=None)  # no Windows escolhe SAPI5
        self.default_rate = int(rate)
        self.default_volume = float(volume)
        self.engine.setProperty("rate", self.default_rate)
        self.engine.setProperty("volume", self.default_volume)

        if voice_hint_ptbr:
            try:
                for v in self.engine.getProperty("voices"):
                    name = (v.name or "").lower()
                    langs = "".join(getattr(v, "languages", [])).lower()
                    if "portuguese" in name or "brazil" in name or "pt_" in langs:
                        self.engine.setProperty("voice", v.id)
                        break
            except Exception:
                pass

        # Fila de (texto, rate_override or None)
        self._queue = []
        self._speaking = False
        self._current_rate = self.default_rate

        # Callbacks
        self.engine.connect('finished-utterance', self._on_done)

        # Inicia loop interno do engine sem bloquear
        try:
            self.engine.startLoop(False)
        except Exception:
            pass

        self._pump_ms = pump_ms
        self._pump()

    def say(self, text: str, rate: int | None = None):
        if not text:
            return
        self._queue.append((str(text), rate))

    def set_rate(self, rate: int):
        """Ajusta o rate padrão para próximas falas (e aplica se estiver ocioso)."""
        self.default_rate = int(rate)
        # se não está falando agora, atualiza o motor já
        if not self._speaking:
            try:
                self.engine.setProperty("rate", self.default_rate)
            except Exception:
                pass

    def _on_done(self, name, completed):
        # Ao terminar, volta o rate ao padrão
        self._speaking = False
        try:
            self.engine.setProperty("rate", self.default_rate)
        except Exception:
            pass

    def _pump(self):
        try:
            if not self._speaking and self._queue:
                self._speaking = True
                text, rate_override = self._queue.pop(0)

                # aplica rate específico desta fala (se houver)
                if rate_override is not None:
                    self._current_rate = int(rate_override)
                else:
                    self._current_rate = self.default_rate

                try:
                    self.engine.setProperty("rate", self._current_rate)
                except Exception:
                    pass

                self.engine.say(text)

            self.engine.iterate()
        except Exception:
            self._speaking = False

        self.root.after(self._pump_ms, self._pump)


# ======= Som opcional (pygame) =======
# pygame não instalado - sons desabilitados
pygame = None
BEEP = None


# ======= Motor de cálculo com "eval" seguro =======
class CalcEngine:
    def __init__(self):
        self.mode = "DEG"   # DEG ou RAD
        self.last = 0       # ANS

    def _ns(self):
        import math
        def _sin(x):   return math.sin(math.radians(x)) if self.mode == "DEG" else math.sin(x)
        def _cos(x):   return math.cos(math.radians(x)) if self.mode == "DEG" else math.cos(x)
        def _tan(x):   return math.tan(math.radians(x)) if self.mode == "DEG" else math.tan(x)
        def _asin(x):  return math.degrees(math.asin(x)) if self.mode == "DEG" else math.asin(x)
        def _acos(x):  return math.degrees(math.acos(x)) if self.mode == "DEG" else math.acos(x)
        def _atan(x):  return math.degrees(math.atan(x)) if self.mode == "DEG" else math.atan(x)

        def _fact(n):  return math.factorial(int(n))
        def _comb(n, r):
            n = int(n); r = int(r)
            return math.comb(n, r) if hasattr(math, "comb") else int(_fact(n) / (_fact(r) * _fact(n - r)))
        def _perm(n, r):
            n = int(n); r = int(r)
            if hasattr(math, "perm"):
                return math.perm(n, r)
            return int(_fact(n) // _fact(n - r))

        return {
            "pi": math.pi, "e": math.e, "ANS": self.last,
            "abs": abs, "floor": math.floor, "ceil": math.ceil, "round": round,
            "sin": _sin, "cos": _cos, "tan": _tan,
            "asin": _asin, "acos": _acos, "atan": _atan,
            "sqrt": math.sqrt, "exp": math.exp,
            "ln": math.log,                        # ln(x)
            "log": lambda x, b=10: math.log(x, b), # log base 10 padrão
            "pow": pow,
            "fact": _fact, "factorial": _fact,
            "nCr": _comb, "comb": _comb,
            "nPr": _perm, "perm": _perm,
            "rad": math.radians, "deg": math.degrees
        }

    @staticmethod
    def _preprocess(expr: str) -> str:
        expr = expr.replace("×", "*").replace("÷", "/").replace("^", "**").replace("π", "pi")
        expr = expr.replace("√", "sqrt")
        expr = re.sub(r"log10\s*\(", "log(", expr)
        return expr

    def evaluate(self, expr: str):
        expr = expr.strip()
        if not expr:
            return ""
        expr = self._preprocess(expr)
        try:
            val = eval(expr, {"__builtins__": {}}, self._ns())
            self.last = val
            return val
        except Exception as e:
            raise ValueError(str(e))


# ======= App Tkinter =======
class CalculatorApp:
    KEY_SPEECH = {
        "+": "mais", "-": "menos", "*": "vezes", "/": "dividido",
        "(": "abre parênteses", ")": "fecha parênteses", ".": "ponto",
        "=": "igual", "^": "elevado a", "sqrt": "raiz quadrada", "pi": "pi",
        "sin": "seno", "cos": "cosseno", "tan": "tangente",
        "asin": "arco seno", "acos": "arco cosseno", "atan": "arco tangente",
        "ln": "logaritmo natural", "log": "logaritmo", "exp": "exponencial",
        "fact": "fatorial", "nCr": "combinação", "nPr": "permuta",
        "ANS": "resultado anterior", "C": "limpar", "⌫": "apagar",
    }

    def __init__(self, root):
        self.root = root
        self.root.title("Calculadora Científica Acessível")
        self.root.geometry("560x760")

        # TTS no thread principal
        self.tts = TTSTk(root, rate=180, volume=1.0)
        self.engine = CalcEngine()
        self.beep_enabled = tk.BooleanVar(value=True)

        # Controle de velocidade
        self.rate_var = tk.IntVar(value=180)
        self.fast_digits_enabled = tk.BooleanVar(value=True)
        self.fast_digits_mult = tk.DoubleVar(value=2.0)  # 2x mais rápido p/ dígitos

        self._build_ui()
        self._bind_keys()

    # ---------- UI ----------
    def _build_ui(self):
        style = ttk.Style(self.root)
        try:
            style.theme_use("clam")
        except Exception:
            pass

        main = ttk.Frame(self.root, padding=10)
        main.pack(fill="both", expand=True)

        # Campo de expressão
        self.expr_var = tk.StringVar()
        expr_entry = ttk.Entry(main, textvariable=self.expr_var, font=("Segoe UI", 20))
        expr_entry.pack(fill="x", pady=(0, 8))
        expr_entry.focus_set()

        # Label de resultado
        self.res_var = tk.StringVar(value="Resultado: ")
        res_label = ttk.Label(main, textvariable=self.res_var, font=("Segoe UI", 16))
        res_label.pack(fill="x", pady=(0, 8))

        # Linha de controles (modo, ler, limpar, beep)
        topbar = ttk.Frame(main)
        topbar.pack(fill="x", pady=(0, 8))

        self.mode_btn = ttk.Button(topbar, text="Modo: Graus", command=self.toggle_mode)
        self.mode_btn.pack(side="left")

        ttk.Button(topbar, text="Ler expressão", command=self.read_expression).pack(side="left", padx=6)
        ttk.Button(topbar, text="Limpar (C)", command=lambda: self._press("C")).pack(side="left")
        ttk.Button(topbar, text="Apagar (⌫)", command=lambda: self._press("⌫")).pack(side="left", padx=6)

        beep_chk = ttk.Checkbutton(topbar, text="Beep", variable=self.beep_enabled)
        beep_chk.pack(side="left", padx=6)

        # ---- Painel de voz ----
        voice_frame = ttk.LabelFrame(main, text="Voz e velocidade")
        voice_frame.pack(fill="x", pady=(6, 8))

        # Slider de velocidade global
        row = ttk.Frame(voice_frame)
        row.pack(fill="x", pady=4)
        ttk.Label(row, text="Velocidade da fala:").pack(side="left")
        rate_scale = ttk.Scale(row, from_=50, to=300, variable=self.rate_var,
                               command=self._on_rate_change)
        rate_scale.pack(side="left", fill="x", expand=True, padx=8)
        self.rate_label = ttk.Label(row, text=f"{self.rate_var.get()} wpm")
        self.rate_label.pack(side="left")

        # Aceleração de dígitos
        row2 = ttk.Frame(voice_frame)
        row2.pack(fill="x", pady=4)
        fast_chk = ttk.Checkbutton(row2, text="Acelerar leitura de dígitos",
                                   variable=self.fast_digits_enabled)
        fast_chk.pack(side="left")
        ttk.Label(row2, text="Multiplicador:").pack(side="left", padx=(12, 4))
        fast_scale = ttk.Scale(row2, from_=1.0, to=3.0, variable=self.fast_digits_mult,
                               command=lambda _=None: self._update_fast_label())
        fast_scale.pack(side="left", fill="x", expand=True, padx=8)
        self.fast_label = ttk.Label(row2, text=f"{self.fast_digits_mult.get():.1f}x")
        self.fast_label.pack(side="left")

        # Botão de teste
        ttk.Button(voice_frame, text="Testar voz",
                   command=lambda: self.tts.say("Teste de voz. Um dois três.")).pack(pady=6)

        # ---- Grade de botões ----
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

        for r, rowbtn in enumerate(buttons):
            for c, (label, token) in enumerate(rowbtn):
                b = ttk.Button(grid, text=label, command=lambda t=token: self._press(t))
                b.grid(row=r, column=c, sticky="nsew", padx=3, pady=3)
        for i in range(4):
            grid.columnconfigure(i, weight=1)
        for i in range(len(buttons)):
            grid.rowconfigure(i, weight=1)

        # Histórico
        hist_frame = ttk.LabelFrame(main, text="Histórico")
        hist_frame.pack(fill="both", expand=True, pady=(8, 0))
        self.history = tk.Listbox(hist_frame, font=("Consolas", 12), height=6)
        self.history.pack(fill="both", expand=True)

        # Dicas
        tips = ttk.Label(
            main,
            text="Atalhos: Enter=Igual | Backspace=Apagar | Esc=C | F9=Graus/Radianos",
            font=("Segoe UI", 10),
            foreground="#555"
        )
        tips.pack(fill="x", pady=(6, 0))

        # aplica rate inicial
        self.tts.set_rate(self.rate_var.get())

    def _update_fast_label(self):
        self.fast_label.config(text=f"{self.fast_digits_mult.get():.1f}x")

    def _on_rate_change(self, _):
        val = int(self.rate_var.get())
        self.rate_label.config(text=f"{val} wpm")
        self.tts.set_rate(val)

    def _bind_keys(self):
        self.root.bind("<Return>", lambda e: self._press("="))
        self.root.bind("<KP_Enter>", lambda e: self._press("="))
        self.root.bind("<BackSpace>", lambda e: self._press("⌫"))
        self.root.bind("<Escape>", lambda e: self._press("C"))
        self.root.bind("<F9>", lambda e: self.toggle_mode())
        

        for ch in "0123456789.+-*/()^":
            self.root.bind(ch, self._key_insert)
        self.root.bind("x", lambda e: self._press("×"))
        self.root.bind("X", lambda e: self._press("×"))

    # ---------- Lógica de interação ----------
    def _key_insert(self, event):
        ch = event.char
        if ch:
            self._insert_text(ch)
            self._speak_key(ch)

    def _insert_text(self, text):
        self._beep()
        cur = self.expr_var.get()
        self.expr_var.set(cur + text)

    def _beep(self):
        if getattr(self, "beep_enabled", None) and self.beep_enabled.get() and BEEP:
            try:
                BEEP.play()
            except Exception:
                pass

    def _speak_key(self, token):
        # Mapeia texto a falar
        spoken = self.KEY_SPEECH.get(token, token)
        rate_override = None

        if token.isdigit():
            spoken = {
                "0": "zero", "1": "um", "2": "dois", "3": "três", "4": "quatro",
                "5": "cinco", "6": "seis", "7": "sete", "8": "oito", "9": "nove"
            }.get(token, token)
            # se modo de dígitos acelerados estiver ligado, aplica rate maior
            if self.fast_digits_enabled.get():
                rate_override = int(self.rate_var.get() * float(self.fast_digits_mult.get()))

        elif token == ".":
            spoken = "ponto"
            if self.fast_digits_enabled.get():
                rate_override = int(self.rate_var.get() * float(self.fast_digits_mult.get()))
        elif token in {"×", "÷"}:
            spoken = "vezes" if token == "×" else "dividido"

        self.tts.say(spoken, rate=rate_override)

    def _press(self, token):
        self._beep()

        # Fala da tecla (com possível aceleração de dígitos)
        self._speak_key(token)

        if token == "C":
            self.expr_var.set("")
            self.res_var.set("Resultado: ")
            return

        if token == "⌫":
            cur = self.expr_var.get()
            if cur:
                self.expr_var.set(cur[:-1])
            return

        if token == "=":
            self._evaluate()
            return

        # Inserções especiais
        if token in {"sin(", "cos(", "tan(", "asin(", "acos(", "atan(", "ln(", "log(", "exp(", "sqrt(", "nCr(", "nPr(", "fact("}:
            self._insert_text(token); return
        if token == "π":
            self._insert_text("pi"); return
        if token == "ANS":
            self._insert_text("ANS"); return
        if token in {"×", "÷"}:
            self._insert_text("*" if token == "×" else "/"); return

        self._insert_text(token)

    def _evaluate(self):
        expr = self.expr_var.get()
        if not expr.strip():
            self.tts.say("expressão vazia")
            return

        try:
            val = self.engine.evaluate(expr)
            val_str = self._format_number(val)
            self.res_var.set(f"Resultado: {val_str}")
            self.history.insert(tk.END, f"{expr} = {val_str}")
            self.history.see(tk.END)
            self.tts.say(f"resultado: {self._speak_number(val)}")
        except Exception:
            self.res_var.set("Erro")
            self.tts.say("erro de cálculo")

    def _format_number(self, x):
        try:
            if isinstance(x, (int,)) or (isinstance(x, float) and x.is_integer()):
                return str(int(round(x)))
            return f"{float(x):.12g}"
        except Exception:
            return str(x)

    def _speak_number(self, x):
        s = self._format_number(x)
        return s.replace("-", "menos ")

    def toggle_mode(self):
        self.engine.mode = "RAD" if self.engine.mode == "DEG" else "DEG"
        txt = "Modo: Radianos" if self.engine.mode == "RAD" else "Modo: Graus"
        self.mode_btn.config(text=txt)
        self.tts.say("modo radianos" if self.engine.mode == "RAD" else "modo graus")

    def read_expression(self):
        expr = self.expr_var.get().strip()
        if not expr:
            self.tts.say("expressão vazia")
            return
        friendly = (expr.replace("*", " vezes ")
                         .replace("/", " dividido ")
                         .replace("+", " mais ")
                         .replace("-", " menos ")
                         .replace("^", " elevado a ")
                         .replace("(", " abre parênteses ")
                         .replace(")", " fecha parênteses ")
                         .replace("pi", " pi ")
                         .replace(".", " ponto "))
        self.tts.say(f"expressão: {friendly}")


if __name__ == "__main__":
    root = tk.Tk()
    app = CalculatorApp(root)
    root.mainloop()
