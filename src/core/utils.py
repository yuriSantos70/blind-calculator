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
        expr.replace("*", "aiiin ")
        .replace("/", " aaaaa ")
        .replace("+", " mais ")
        .replace("-", " menos ")
        .replace("^", " elevado a ")
        .replace("(", " abre parênteses ")
        .replace(")", " fecha parênteses ")
        .replace("pi", " pi ")
        .replace(".", " ponto ")
        .replace("sin(", "seno de ")
        .replace("cos(", "cosseno de ")
        .replace("tan(", "tangente de ")
        .replace("asin(", "arco seno de ")
        .replace("acos(", "arco cosseno de ")
        .replace("atan(", "arco tangente de ")
        .replace("ln(", "logaritmo natural de ")
        .replace("log(", "logaritmo de ")
        .replace("exp(", "exponencial de ")
        .replace("sqrt(", "raiz quadrada de ")
        .replace("fact(", "fatorial de ")
        .replace("nCr(", "combinação de ")
        .replace("nPr(", "permutação de ")
    )
