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

    # Paleta de botões para destacar grupos específicos na calculadora.
    style.configure(
        "CalcDigit.TButton",
        background="#f4f4f5",
        foreground="#1f2937",
        font=("Segoe UI", 13),
        relief="flat",
    )
    style.map(
        "CalcDigit.TButton",
        background=[("active", "#e5e7eb"), ("pressed", "#d1d5db")],
    )

    style.configure(
        "CalcFunction.TButton",
        background="#e0f2fe",
        foreground="#1e293b",
        font=("Segoe UI", 12),
        relief="flat",
    )
    style.map(
        "CalcFunction.TButton",
        background=[("active", "#bae6fd"), ("pressed", "#7dd3fc")],
    )

    style.configure(
        "CalcOperator.TButton",
        background="#2563eb",
        foreground="#ffffff",
        font=("Segoe UI", 13, "bold"),
        relief="flat",
    )
    style.map(
        "CalcOperator.TButton",
        background=[("active", "#1d4ed8"), ("pressed", "#1e40af")],
        foreground=[("disabled", "#94a3b8")],
    )

    style.configure(
        "CalcAction.TButton",
        background="#dc2626",
        foreground="#ffffff",
        font=("Segoe UI", 12, "bold"),
        relief="flat",
    )
    style.map(
        "CalcAction.TButton",
        background=[("active", "#b91c1c"), ("pressed", "#991b1b")],
        foreground=[("disabled", "#fca5a5")],
    )

    style.configure(
        "CalcPrimary.TButton",
        background="#f97316",
        foreground="#ffffff",
        font=("Segoe UI", 14, "bold"),
        relief="flat",
    )
    style.map(
        "CalcPrimary.TButton",
        background=[("active", "#ea580c"), ("pressed", "#c2410c")],
        foreground=[("disabled", "#fed7aa")],
    )
    return style
