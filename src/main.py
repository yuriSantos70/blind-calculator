"""Ponto de entrada da aplicação desktop Blind Calculator."""

from __future__ import annotations

import tkinter as tk
from pathlib import Path

from src.ui.calculator_ui import CalculatorApp


def main() -> None:
    root = tk.Tk()
    assets_dir = Path(__file__).resolve().parent.parent / "assets"
    CalculatorApp(root, assets_dir=assets_dir)
    root.mainloop()


if __name__ == "__main__":
    main()
