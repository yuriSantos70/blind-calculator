# Firmware do Teclado USB

Este diretório contém o firmware para o teclado matricial 5x7 baseado no Arduino Pro Micro. O código `FirmwareUSB.ino` expõe as teclas como um dispositivo HID padrão, enviando os atalhos esperados pela aplicação desktop Blind Calculator.

## Como usar

1. Abra o arquivo `FirmwareUSB.ino` na IDE do Arduino.
2. Selecione a placa **Arduino/Genuino Micro** ou **Arduino Leonardo** (compatível com ATmega32U4).
3. Compile e faça o upload para o dispositivo.
4. Conecte o teclado físico; as teclas geram os caracteres mapeados no código.

## Ajustes possíveis

- `rowPins` e `colPins`: altere conforme o cabeamento da sua matriz.
- `DEBOUNCE_MS`: tempo de debounce em milissegundos.
- `SCAN_INTERVAL_MS`: intervalo entre varreduras da matriz.

Adapte conforme necessário para o layout final do seu periférico.
