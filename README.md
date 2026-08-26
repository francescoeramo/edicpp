# EdiCpp — Editor C++ leggero per Linux

> Bello. Veloce. Nativo. Pensato per Fedora.

Editor minimal ma completo per C++, scritto in **Python + PyQt6** (Qt6 nativo, zero Electron/webapp).

![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![Qt](https://img.shields.io/badge/Qt-6-green)
![Platform](https://img.shields.io/badge/Platform-Fedora%20%7C%20Linux-lightgrey)

## ✨ Funzionalità

- **Highlight C++ completo** — keyword, tipi STL, stringhe, numeri, commenti, direttive `#include`/`#define`, chiamate a funzione
- **Numeri di riga** + riga corrente evidenziata + indentazione automatica + chiusura parentesi
- **Scorciatoie** — `Ctrl+N/O/S`, `Ctrl+F` cerca, `Ctrl+/` commenta, `F5` compila&esegui, `Ctrl+B` solo compila, zoom, ecc.
- **Explorer file** a sinistra — apri cartella, doppio click per aprire
- **Terminale integrato in basso** — vera `bash` interattiva con `pty` (input, `Ctrl+C`, `Ctrl+L`, `cd`, `make`, `gdb`, ecc.)
- **Compila & Esegui** con `g++ -std=c++17 -O2 -Wall -Wextra`
- **Guida integrata** (`F1`) e tema scuro **Tokyo Night** curato esteticamente
- **Schede multiple** + salvataggio automatico prima di compilare

## 📸 Aspetto

Tema scuro blu-notte, bordi arrotondati, accento `#7aa2f7`, font `JetBrains Mono / Fira Code`, layout a 3 pannelli (explorer | editor | terminale).

## 🚀 Installazione su Fedora

```bash
# 1. Dipendenze di sistema
sudo dnf install gcc-c++ python3-pip

# 2. Clona
git clone https://github.com/francescoeramo/edicpp.git
cd edicpp

# 3. Dipendenze Python
pip install -r requirements.txt
# oppure: pip install --user PyQt6

# 4. Avvio
./run.sh
# oppure:
python3 -m edicpp.main
```

### Avvio da launcher

```bash
cp edicpp.desktop ~/.local/share/applications/
# poi cerca "EdiCpp" nel menu
```

## ⌨️ Scorciatoie

| Tasto | Azione |
|-------|--------|
| `Ctrl+N` | Nuovo file |
| `Ctrl+O` | Apri file |
| `Ctrl+K` | Apri cartella |
| `Ctrl+S` | Salva |
| `Ctrl+Shift+S` | Salva con nome |
| `Ctrl+F` | Cerca |
| `Ctrl+/` | Commenta / Decommenta |
| `Ctrl+Z` / `Ctrl+Y` | Annulla / Ripeti |
| `Ctrl+E` | Mostra/nascondi Explorer |
| `Ctrl+J` | Mostra/nascondi Terminale |
| `Ctrl+B` | Compila |
| `F5` | Compila & Esegui |
| `Ctrl+ + / -` | Zoom |
| `F1` | Guida |

## 🛠️ Struttura

```
edicpp/
├── edicpp/
│   ├── main.py       # Finestra principale, editor, schede
│   ├── highlighter.py# Syntax highlighter C++
│   ├── terminal.py   # Terminale pty + bash
│   └── theme.py      # Stylesheet Tokyo Night
├── requirements.txt
├── run.sh
└── edicpp.desktop
```



