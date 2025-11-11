"""Benchmark simples: mede tempo de reprodução de voz por dígito.

O script testa cada dígito ('0'..'9') pronunciado como palavra em português
para uma lista de valores de 'rate' do pyttsx3. Para cada combinação é feita
uma média em N repetições. Os resultados são impressos e gravados em CSV
em `tests/voice_speed_results.csv`.

Uso: python tests\TesteAudio1.py
"""

from __future__ import annotations

import csv
import time
from pathlib import Path
from statistics import mean
from typing import Dict, List, Tuple

import pyttsx3


DIGIT_WORDS: Dict[str, str] = {
    "0": "zero",
    "1": "um",
    "2": "dois",
    "3": "três",
    "4": "quatro",
    "5": "cinco",
    "6": "seis",
    "7": "sete",
    "8": "oito",
    "9": "nove",
}


def measure_utterance_time(engine: pyttsx3.Engine, text: str) -> float:
    """Fala o texto e retorna o tempo (segundos) que a chamada bloqueante levou."""
    start = time.perf_counter()
    engine.say(text)
    engine.runAndWait()
    end = time.perf_counter()
    return end - start


def run_benchmark(
    rates: List[int], digits: List[str], repeats: int = 3
) -> List[Tuple[int, str, float, List[float]]]:
    """Executa o benchmark e retorna lista de tuplas (rate, digit, mean, samples).

    Cada sample é o tempo (segundos) de uma reprodução completa do texto.
    """
    engine = pyttsx3.init()
    engine.setProperty("volume", 1.0)

    results: List[Tuple[int, str, float, List[float]]] = []

    for rate in rates:
        engine.setProperty("rate", rate)
        for d in digits:
            word = DIGIT_WORDS.get(d, d)
            samples: List[float] = []
            # aquecimento rápido (melhora estabilidade do primeiro run)
            engine.say("")
            engine.runAndWait()
            for _ in range(repeats):
                t = measure_utterance_time(engine, word)
                samples.append(t)
                # pequeno silêncio entre tentativas
                time.sleep(0.15)
            avg = mean(samples)
            results.append((rate, d, avg, samples))

    return results


def save_csv(path: Path, rows: List[Tuple[int, str, float, List[float]]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["rate", "digit", "mean_seconds", "samples_seconds"])
        for rate, digit, mean_s, samples in rows:
            writer.writerow([rate, digit, f"{mean_s:.4f}", ";".join(f"{s:.4f}" for s in samples)])


def print_summary(rows: List[Tuple[int, str, float, List[float]]]) -> None:
    print("Benchmark de velocidade de voz (pyttsx3)")
    print("rate\tdigit\tmean(s)\tsamples(s)")
    for rate, digit, mean_s, samples in rows:
        samples_str = ", ".join(f"{s:.3f}" for s in samples)
        print(f"{rate}\t{digit}\t{mean_s:.3f}\t[{samples_str}]")


def main() -> None:
    # parâmetros do benchmark — ajuste conforme necessário
    rates = [120, 150, 180, 210, 240]
    digits = [str(i) for i in range(10)]
    repeats = 3

    print("Iniciando benchmark — isso irá falar vários números.\n")
    rows = run_benchmark(rates, digits, repeats=repeats)

    out_csv = Path(__file__).resolve().parent / "voice_speed_results.csv"
    save_csv(out_csv, rows)
    print_summary(rows)
    print(f"\nResultados salvos em: {out_csv}")


if __name__ == "__main__":
    main()
