"""Gerência de sons e efeitos auditivos usando winsound (Windows)."""

from __future__ import annotations

import platform
from pathlib import Path
from typing import Optional

if platform.system() == "Windows":
    import winsound
else:
    winsound = None  # type: ignore[assignment]


class SoundManager:
    """Carrega e reproduz efeitos sonoros simples usando winsound."""

    def __init__(self, assets_dir: str | Path | None = None) -> None:
        self.assets_dir = Path(assets_dir) if assets_dir else None
        self._initialized = winsound is not None

    @property
    def available(self) -> bool:
        return self._initialized

    # ---------- API ----------
    def play_beep(self, enabled: bool = True) -> None:
        if not enabled or not self._initialized:
            return
        try:
            # Beep simples usando o speaker do sistema
            winsound.Beep(500, 100)  # Frequência 500Hz, duração 100ms
        except Exception:
            pass
