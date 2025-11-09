import pygame
import pyttsx3
import time

# === Configuração de sons ===
pygame.mixer.init()
som_tecla = pygame.mixer.Sound("Pyth/beep.wav")  # coloque um arquivo de beep na pasta

# === Configuração da voz ===
engine = pyttsx3.init()
engine.setProperty("rate", 180)   # velocidade da fala
engine.setProperty("volume", 1.0) # volume máximo

# Função para falar
def falar(texto):
    engine.say(texto)
    engine.runAndWait()

# Simulação de calculadora
def main():
    expressao = "1 + 2"

    # Pressionando "1"
    som_tecla.play()
    print("Tecla: 1")
    falar("what your name?")
    time.sleep(0.5)

    # Pressionando "+"
    som_tecla.play()
    print("Tecla: +")
    falar("mais")
    time.sleep(0.5)

    # Pressionando "2"
    som_tecla.play()
    print("Tecla: 2")
    falar("dois")
    time.sleep(0.5)

    # Pressionando "="
    som_tecla.play()
    print("Resultado da expressão:", expressao)
    resultado = eval(expressao)  # calcula expressão matemática
    falar(f"resultado: {resultado}")

if __name__ == "__main__":
    main()
