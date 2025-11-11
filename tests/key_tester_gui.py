"""GUI simples para testar reprodução de voz por tecla.

Abre uma janela com botões para 0-9, um campo para digitar teclas livremente,
um Spinbox para ajustar 'rate' do pyttsx3 e um botão para limpar o log.

Ao pressionar um botão ou digitar Enter no campo, o texto mapeado é falado
e o tempo de reprodução (engine.say + runAndWait) é medido e salvo em
`tests/interactive_key_log.csv`.

Uso: python tests\key_tester_gui.py
"""

from __future__ import annotations

import csv
import threading
import time
from datetime import datetime
from pathlib import Path
from typing import Dict
import sys

import pyttsx3
import tkinter as tk
from tkinter import ttk


DIGIT_WORDS: Dict[str, str] = {
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


LOG_PATH = Path(__file__).resolve().parent / "interactive_key_log.csv"


def speak_and_log(key: str, rate: int) -> None:
    """Fala a palavra mapeada para `key`, mede o tempo e grava no CSV.

    Usa um engine local (criado na thread) para maior robustez.
    """
    word = DIGIT_WORDS.get(key, key)
    engine = pyttsx3.init()
    engine.setProperty("rate", rate)
    engine.setProperty("volume", 1.0)

    start = time.perf_counter()
    engine.say(word)
    engine.runAndWait()
    end = time.perf_counter()
    duration = end - start

    # grava linha: timestamp, key, word, rate, duration
    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    with LOG_PATH.open("a", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([datetime.now().isoformat(), key, word, rate, f"{duration:.4f}"])


class KeyTesterApp(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title("Key Tester - TTS")
        self.geometry("420x300")

        self.rate_var = tk.IntVar(value=180)

        controls = ttk.Frame(self)
        controls.pack(padx=10, pady=8, fill="x")

        ttk.Label(controls, text="Rate:").pack(side="left")
        self.rate_spin = ttk.Spinbox(controls, from_=80, to=400, increment=10, textvariable=self.rate_var, width=6)
        self.rate_spin.pack(side="left", padx=(4, 12))

        ttk.Button(controls, text="Limpar log", command=self.clear_log).pack(side="right")

        # área de botões 0-9
        btn_frame = ttk.Frame(self)
        btn_frame.pack(padx=10, pady=6)

        for i in range(10):
            b = ttk.Button(btn_frame, text=str(i), width=6, command=lambda k=str(i): self.on_key(k))
            b.grid(row=i // 5, column=i % 5, padx=4, pady=4)

        # campo de digitação para testar outras teclas
        entry_frame = ttk.Frame(self)
        entry_frame.pack(padx=10, pady=8, fill="x")

        ttk.Label(entry_frame, text="Digite a tecla/texto e pressione Enter:").pack(anchor="w")
        self.entry = ttk.Entry(entry_frame)
        self.entry.pack(fill="x", pady=(4, 0))
        self.entry.bind("<Return>", self.on_entry)

        # área de status
        self.status = tk.StringVar(value=f"Log: {LOG_PATH}")
        ttk.Label(self, textvariable=self.status).pack(side="bottom", fill="x", padx=10, pady=6)

    def on_entry(self, event: tk.Event) -> None:
        text = self.entry.get().strip()
        if not text:
            return
        # pega primeiro caractere para mapping típico de tecla
        key = text[0]
        self.entry.delete(0, "end")
        self.on_key(key)

    def on_key(self, key: str) -> None:
        rate = self.rate_var.get()
        # rodar speak_and_log em thread para não travar a UI
        threading.Thread(target=self._thread_worker, args=(key, rate), daemon=True).start()

    def _thread_worker(self, key: str, rate: int) -> None:
        try:
            speak_and_log(key, rate)
            # atualizar status com último evento
            self.status.set(f"Última tecla: {key} (rate={rate}) — gravado em {LOG_PATH.name}")
        except Exception as e:
            self.status.set(f"Erro ao falar: {e}")

    def clear_log(self) -> None:
        try:
            if LOG_PATH.exists():
                LOG_PATH.unlink()
            # reescrever cabeçalho
            with LOG_PATH.open("w", encoding="utf-8", newline="") as f:
                writer = csv.writer(f)
                writer.writerow(["timestamp", "key", "word", "rate", "duration_s"])
            self.status.set("Log limpo")
        except Exception as e:
            self.status.set(f"Erro ao limpar log: {e}")


def main() -> None:
    # garante cabeçalho do CSV
    if not LOG_PATH.exists():
        with LOG_PATH.open("w", encoding="utf-8", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["timestamp", "key", "word", "rate", "duration_s"])

    app = KeyTesterApp()
    app.mainloop()


def demo_run() -> None:
    """Modo demo headless: fala uma sequência de teclas e sai.

    Útil para executar o script em ambientes sem interface gráfica.
    """
    # sequência curta de exemplo
    seq = ["1", "2", "3", "4", "5", "6", "7", "8", "9", "0"]
    # usa rate default 180
    rate = 180
    # garante cabeçalho
    if not LOG_PATH.exists():
        with LOG_PATH.open("w", encoding="utf-8", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["timestamp", "key", "word", "rate", "duration_s"])

    for k in seq:
        print(f"Demo: falando tecla {k} (rate={rate})")
        speak_and_log(k, rate)
        time.sleep(0.2)


if __name__ == "__main__":
    if "--demo" in sys.argv:
        demo_run()
    else:
        main()
