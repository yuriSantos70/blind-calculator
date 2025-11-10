"""Integração de síntese de voz (pyttsx3) com threading."""

from __future__ import annotations

import queue
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
        self.default_rate = int(rate)
        self.default_volume = float(volume)
        self.voice_hint_ptbr = voice_hint_ptbr
        self.selected_voice_id = None

        self.queue = queue.Queue()
        self.worker_thread = threading.Thread(target=self._worker, daemon=True)
        self.worker_thread.start()

    # ---------- API pública ----------
    def say(self, text: str, rate: int | None = None) -> None:
        if not text:
            return
        # Coloca na fila para processamento sequencial
        self.queue.put((text, rate))

    def set_rate(self, rate: int) -> None:
        self.default_rate = int(rate)

    def set_voice(self, voice_id: str) -> None:
        self.selected_voice_id = voice_id

    def get_voices(self) -> list[tuple[str, str]]:
        try:
            engine = pyttsx3.init()
            voices = engine.getProperty('voices')
            return [(voice.name, voice.id) for voice in voices]
        except Exception:
            return []

    def shutdown(self) -> None:
        pass

    # ---------- Internos ----------
    def _worker(self) -> None:
        while True:
            text, rate = self.queue.get()
            self._speak_text(text, rate)
            self.queue.task_done()
    def _speak_text(self, text: str, rate: Optional[int] = None) -> None:
        try:
            # Cria uma nova instância do engine para cada fala, evitando problemas de estado compartilhado
            engine = pyttsx3.init(driverName=None)
            engine.setProperty("volume", self.default_volume)
            if self.selected_voice_id:
                engine.setProperty("voice", self.selected_voice_id)
            elif self.voice_hint_ptbr:
                self._select_portuguese_voice_for_engine(engine)
            if rate is not None:
                engine.setProperty("rate", rate)
            else:
                engine.setProperty("rate", self.default_rate)
            engine.say(text)
            engine.runAndWait()
        except Exception:
            pass

    def _select_portuguese_voice_for_engine(self, engine) -> None:
        try:
            for voice in engine.getProperty("voices"):
                name = (voice.name or "").lower()
                languages = "".join(getattr(voice, "languages", [])).lower()
                id_lower = (voice.id or "").lower()
                if ("portuguese" in name or "brazil" in name or "pt" in languages or 
                    "pt-br" in id_lower or "maria" in name):
                    engine.setProperty("voice", voice.id)
                    break
        except Exception:
            pass
