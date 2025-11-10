"""Integração de síntese de voz (pyttsx3) com threading."""

from __future__ import annotations

import threading
from typing import Optional

import pyttsx3


class TTSTk:
    """Motor TTS que usa threading para não bloquear o Tkinter."""

    def __init__(
        self,
        root,
        rate: int = 180,
        volume: float = 1.0,
        voice_hint_ptbr: bool = True,
    ) -> None:
        self.root = root
        self.engine = pyttsx3.init(driverName=None)
        self.default_rate = int(rate)
        self.default_volume = float(volume)
        self.engine.setProperty("rate", self.default_rate)
        self.engine.setProperty("volume", self.default_volume)

        if voice_hint_ptbr:
            self._select_portuguese_voice()

    # ---------- API pública ----------
    def say(self, text: str, rate: int | None = None) -> None:
        if not text:
            return
        # Executa o TTS em um thread separado para não bloquear
        threading.Thread(
            target=self._speak_text,
            args=(text, rate),
            daemon=True
        ).start()

    def set_rate(self, rate: int) -> None:
        self.default_rate = int(rate)
        try:
            self.engine.setProperty("rate", self.default_rate)
        except Exception:
            pass

    def shutdown(self) -> None:
        try:
            self.engine.stop()
        except Exception:
            pass

    # ---------- Internos ----------
    def _speak_text(self, text: str, rate: Optional[int] = None) -> None:
        try:
            if rate is not None:
                self.engine.setProperty("rate", rate)
            self.engine.say(text)
            self.engine.runAndWait()
            # Restaura a taxa padrão
            self.engine.setProperty("rate", self.default_rate)
        except Exception:
            pass

    def _select_portuguese_voice(self) -> None:
        try:
            for voice in self.engine.getProperty("voices"):
                name = (voice.name or "").lower()
                languages = "".join(getattr(voice, "languages", [])).lower()
                if "portuguese" in name or "brazil" in name or "pt_" in languages:
                    self.engine.setProperty("voice", voice.id)
                    break
        except Exception:
            pass
