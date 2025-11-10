"""Funções utilitárias compartilhadas pela interface."""

from __future__ import annotations

from typing import Any


def format_number(value: Any) -> str:
    """Formata números para exibição enxuta, preservando inteiros exatos."""
    try:
        if isinstance(value, int):
            return str(value)
        if isinstance(value, float) and value.is_integer():
            return str(int(round(value)))
        return f"{float(value):.12g}"
    except Exception:
        return str(value)


def spoken_number(value: Any) -> str:
    """Gera uma string amigável para leitura via TTS."""
    formatted = format_number(value)
    return formatted.replace("-", "menos ")


def friendly_expression(expr: str) -> str:
    """Substitui símbolos por descrições faladas do operador."""
    return (
        expr.replace("*", " vezes ")
        .replace("/", " dividido ")
        .replace("+", " mais ")
        .replace("-", " menos ")
        .replace("^", " elevado a ")
        .replace("(", " abre parênteses ")
        .replace(")", " fecha parênteses ")
        .replace("pi", " pi ")
        .replace(".", " ponto ")
    )
