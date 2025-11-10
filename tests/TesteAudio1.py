"""Protótipo simples de áudio para teste manual."""

from __future__ import annotations

import time
from pathlib import Path

import pygame
import pyttsx3


def falar(engine: pyttsx3.Engine, texto: str) -> None:
    engine.say(texto)
    engine.runAndWait()


def main() -> None:
    pygame.mixer.init()
    beep_path = Path(__file__).resolve().parents[1] / "assets" / "sounds" / "beep.wav"
    beep = pygame.mixer.Sound(str(beep_path)) if beep_path.exists() else None

    engine = pyttsx3.init()
    engine.setProperty("rate", 180)
    engine.setProperty("volume", 1.0)

    sequencia = [
        ("1", "um"),
        ("+", "mais"),
        ("2", "dois"),
        ("=", "resultado"),
    ]

    expressao = "1 + 2"
    falar(engine, "Teste de áudio iniciando")
    for tecla, fala in sequencia:
        if beep:
            beep.play()
        print(f"Tecla: {tecla}")
        falar(engine, fala)
        time.sleep(0.5)

    resultado = eval(expressao)
    falar(engine, f"Resultado: {resultado}")


if __name__ == "__main__":
    main()
