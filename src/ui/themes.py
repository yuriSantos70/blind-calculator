"""Configuração de temas e estilos Tkinter."""

from __future__ import annotations

from tkinter import ttk


def apply_base_theme(root) -> ttk.Style:
    """Aplica um estilo padrão e retorna a instância de Style."""
    style = ttk.Style(root)
    try:
        style.theme_use("clam")
    except Exception:
        pass

    style.configure("TButton", padding=(6, 4), font=("Segoe UI", 12))
    style.configure("TLabel", font=("Segoe UI", 12))
    style.configure("TCheckbutton", font=("Segoe UI", 11))
    style.configure("TLabelframe", font=("Segoe UI", 11, "bold"))
    return style
