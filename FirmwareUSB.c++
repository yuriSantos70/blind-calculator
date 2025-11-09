/*
  Pro Micro HID Keyboard – Calculadora sem FN (5x7 = 35 teclas)
  - Matriz 5x7
  - Debounce simples
  - Envia caracteres/atalhos compatíveis com seu app Tkinter
  - ÷ -> '/', × -> '*', − -> '-'
  - '=' -> Enter, 'BS' -> Backspace, 'C' -> Esc
*/

#include <Keyboard.h>

// ===== PINAGEM =====
const uint8_t ROWS = 5;
const uint8_t COLS = 7;
// Rows: saem LOW uma por vez
const uint8_t rowPins[ROWS] = {2, 3, 4, 5, 6};
// Cols: entradas com pull-up
const uint8_t colPins[COLS] = {7, 8, 9, 10, 16, 14, 15};


const uint16_t DEBOUNCE_MS = 15;
const uint16_t SCAN_INTERVAL_MS = 3;

// ===== Estado =====
struct KeyState {
  bool pressed;          // estado estabilizado
  bool reading;          // leitura bruta
  uint32_t lastChangeMs; // timestamp bounce
};

KeyState keys[ROWS][COLS];
uint32_t lastScan = 0;

// ===== Helpers HID =====
void sendString(const char* s) {
  if (!s) return;
  while (*s) {
    Keyboard.write(*s);
    s++;
  }
}

void sendEnter()      { Keyboard.write(KEY_RETURN); }
void sendBackspace()  { Keyboard.write(KEY_BACKSPACE); }
void sendEsc()        { Keyboard.write(KEY_ESC); }

// ===== Mapear tecla pressionada (r,c) =====
void onKeyPress(uint8_t r, uint8_t c) {
  // ---- LINHA 0 ----
  if (r == 0 && c == 0) { sendString("7"); return; }
  if (r == 0 && c == 1) { sendString("8"); return; }
  if (r == 0 && c == 2) { sendString("9"); return; }
  if (r == 0 && c == 3) { sendString("/"); return; }        // ÷
  if (r == 0 && c == 4) { sendString("sin("); return; }
  if (r == 0 && c == 5) { sendString("cos("); return; }
  if (r == 0 && c == 6) { sendString("tan("); return; }

  // ---- LINHA 1 ----
  if (r == 1 && c == 0) { sendString("4"); return; }
  if (r == 1 && c == 1) { sendString("5"); return; }
  if (r == 1 && c == 2) { sendString("6"); return; }
  if (r == 1 && c == 3) { sendString("*"); return; }        // ×
  if (r == 1 && c == 4) { sendString("asin("); return; }
  if (r == 1 && c == 5) { sendString("acos("); return; }
  if (r == 1 && c == 6) { sendString("atan("); return; }

  // ---- LINHA 2 ----
  if (r == 2 && c == 0) { sendString("1"); return; }
  if (r == 2 && c == 1) { sendString("2"); return; }
  if (r == 2 && c == 2) { sendString("3"); return; }
  if (r == 2 && c == 3) { sendString("-"); return; }        // −
  if (r == 2 && c == 4) { sendString("ln("); return; }
  if (r == 2 && c == 5) { sendString("log("); return; }
  if (r == 2 && c == 6) { sendString("exp("); return; }

  // ---- LINHA 3 ----
  if (r == 3 && c == 0) { sendString("0"); return; }
  if (r == 3 && c == 1) { sendString("."); return; }
  if (r == 3 && c == 2) { sendString("("); return; }
  if (r == 3 && c == 3) { sendString(")"); return; }
  if (r == 3 && c == 4) { sendString("sqrt("); return; }
  if (r == 3 && c == 5) { sendString("^"); return; }
  if (r == 3 && c == 6) { sendString("pi"); return; }       // π

  // ---- LINHA 4 ----
  if (r == 4 && c == 0) { sendString("ANS"); return; }
  if (r == 4 && c == 1) { sendBackspace(); return; }        // BS
  if (r == 4 && c == 2) { sendEsc(); return; }              // C (Clear)
  if (r == 4 && c == 3) { sendEnter(); return; }            // =
  if (r == 4 && c == 4) { sendString("nCr("); return; }
  if (r == 4 && c == 5) { sendString("nPr("); return; }
  if (r == 4 && c == 6) { sendString("fact("); return; }
}

// ===== Setup =====
void setup() {
  // Colunas com pull-up
  for (uint8_t c = 0; c < COLS; c++) {
    pinMode(colPins[c], INPUT_PULLUP);
  }
  // Linhas inicialmente em alta impedância
  for (uint8_t r = 0; r < ROWS; r++) {
    pinMode(rowPins[r], INPUT);
  }

  Keyboard.begin();
}

// ===== Loop =====
void loop() {
  uint32_t now = millis();
  if (now - lastScan < SCAN_INTERVAL_MS) return;
  lastScan = now;

  for (uint8_t r = 0; r < ROWS; r++) {
    // Ativa a linha r: OUTPUT LOW
    pinMode(rowPins[r], OUTPUT);
    digitalWrite(rowPins[r], LOW);
    delayMicroseconds(80);

    for (uint8_t c = 0; c < COLS; c++) {
      bool rawPressed = (digitalRead(colPins[c]) == LOW); // fecha p/ GND

      KeyState &ks = keys[r][c];
      if (rawPressed != ks.reading) {
        ks.reading = rawPressed;
        ks.lastChangeMs = now;
      }

      if ((now - ks.lastChangeMs) > DEBOUNCE_MS) {
        if (ks.pressed != ks.reading) {
          ks.pressed = ks.reading;
          if (ks.pressed) {
            onKeyPress(r, c);
          }
        }
      }
    }

    // Desativa a linha r: volta para INPUT (alta impedância)
    pinMode(rowPins[r], INPUT);
  }
}
