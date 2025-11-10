"""Motor de cálculo com suporte a graus/radianos e funções científicas."""

from __future__ import annotations

import math
import re
from typing import Any, Dict


class CalcEngine:
    """Responsável por avaliar expressões matemáticas de forma controlada."""

    def __init__(self) -> None:
        self.mode = "DEG"
        self.last: float = 0.0

    # ---------- namespace seguro ----------
    def _namespace(self) -> Dict[str, Any]:
        def _sin(x: float) -> float:
            return math.sin(math.radians(x)) if self.mode == "DEG" else math.sin(x)

        def _cos(x: float) -> float:
            return math.cos(math.radians(x)) if self.mode == "DEG" else math.cos(x)

        def _tan(x: float) -> float:
            return math.tan(math.radians(x)) if self.mode == "DEG" else math.tan(x)

        def _asin(x: float) -> float:
            return math.degrees(math.asin(x)) if self.mode == "DEG" else math.asin(x)

        def _acos(x: float) -> float:
            return math.degrees(math.acos(x)) if self.mode == "DEG" else math.acos(x)

        def _atan(x: float) -> float:
            return math.degrees(math.atan(x)) if self.mode == "DEG" else math.atan(x)

        def _fact(n: float) -> int:
            return math.factorial(int(n))

        def _comb(n: float, r: float) -> int:
            n_int = int(n)
            r_int = int(r)
            if hasattr(math, "comb"):
                return math.comb(n_int, r_int)
            return int(_fact(n_int) / (_fact(r_int) * _fact(n_int - r_int)))

        def _perm(n: float, r: float) -> int:
            n_int = int(n)
            r_int = int(r)
            if hasattr(math, "perm"):
                return math.perm(n_int, r_int)
            return int(_fact(n_int) // _fact(n_int - r_int))

        return {
            "pi": math.pi,
            "e": math.e,
            "ANS": self.last,
            "abs": abs,
            "floor": math.floor,
            "ceil": math.ceil,
            "round": round,
            "sin": _sin,
            "cos": _cos,
            "tan": _tan,
            "asin": _asin,
            "acos": _acos,
            "atan": _atan,
            "sqrt": math.sqrt,
            "exp": math.exp,
            "ln": math.log,
            "log": lambda x, b=10: math.log(x, b),
            "pow": pow,
            "fact": _fact,
            "factorial": _fact,
            "nCr": _comb,
            "comb": _comb,
            "nPr": _perm,
            "perm": _perm,
            "rad": math.radians,
            "deg": math.degrees,
        }

    @staticmethod
    def _preprocess(expr: str) -> str:
        """Normaliza símbolos comuns antes da avaliação."""
        normalized = expr.replace("×", "*").replace("÷", "/").replace("^", "**").replace("π", "pi")
        normalized = normalized.replace("√", "sqrt")
        normalized = re.sub(r"log10\s*\(", "log(", normalized)
        return normalized

    # ---------- API pública ----------
    def evaluate(self, expr: str) -> Any:
        expression = expr.strip()
        if not expression:
            return ""

        expression = self._preprocess(expression)
        try:
            value = eval(expression, {"__builtins__": {}}, self._namespace())
            self.last = value
            return value
        except Exception as exc:  # noqa: BLE001 - queremos repassar msg amigável
            raise ValueError(str(exc)) from exc
