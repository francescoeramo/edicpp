import os
import pty
import select
import subprocess
import signal
import re
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QPlainTextEdit
from PyQt6.QtCore import QTimer, Qt
from PyQt6.QtGui import QFont, QTextCursor, QColor, QTextCharFormat


class EmbeddedTerminal(QWidget):
    """Win98 MS-DOS prompt look ma bash Linux vera — input solo a fine riga."""
    def __init__(self, workdir=None, parent=None):
        super().__init__(parent)
        self.workdir = workdir or os.path.expanduser("~")
        self.master_fd = None
        self.proc = None
        self._input_start = 0  # posizione dove inizia l'input corrente
        self._setup_ui()
        self._spawn_shell()
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._read_output)
        self.timer.start(30)

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        self.setStyleSheet("background:#c0c0c0;")

        header = QWidget()
        header.setFixedHeight(22)
        header.setStyleSheet("background:#000080; border: none;")
        hl = QHBoxLayout(header)
        hl.setContentsMargins(4, 2, 4, 2)
        hl.setSpacing(6)
        icon = QLabel("C:\\>")
        icon.setStyleSheet("color:#ffffff; font-family:'MS Sans Serif'; font-size:11px; font-weight:700; border:none; background:transparent;")
        hl.addWidget(icon)
        title = QLabel("MS-DOS Prompt")
        title.setStyleSheet("color:#ffffff; font-family:'MS Sans Serif'; font-size:11px; font-weight:700; border:none; background:transparent;")
        hl.addWidget(title)
        hl.addStretch()
        self.clear_btn = QPushButton("Pulisci")
        self.clear_btn.setFixedHeight(16)
        self.clear_btn.setFixedWidth(58)
        self.clear_btn.setStyleSheet("font-size:11px; font-weight:400; padding:1px 6px;")
        self.clear_btn.clicked.connect(self._clear)
        hl.addWidget(self.clear_btn)

        layout.addWidget(header)

        self.output = QPlainTextEdit()
        self.output.setReadOnly(False)
        self.output.setUndoRedoEnabled(False)
        self.output.setStyleSheet("""
            QPlainTextEdit {
                background:#000000;
                color:#c0c0c0;
                border-top: 2px solid #404040;
                border-left: 2px solid #404040;
                border-bottom: 1px solid #ffffff;
                border-right: 1px solid #ffffff;
                font-family:'Courier New', monospace;
                font-size:11px;
                padding:4px;
            }
        """)
        font = QFont("Courier New")
        font.setPointSize(9)
        font.setWeight(QFont.Weight.Normal)
        self.output.setFont(font)
        self.output.setLineWrapMode(QPlainTextEdit.LineWrapMode.WidgetWidth)
        layout.addWidget(self.output, 1)
        self.output.installEventFilter(self)
        # keep cursor at end on focus
        self.output.cursorPositionChanged.connect(self._on_cursor_changed)

    def _spawn_shell(self):
        self.master_fd, slave_fd = pty.openpty()
        # PS1 Linux vero con cartella — solo grafica Win98, contenuto Linux
        # Mostra user@host:cartella$ come su Fedora
        ps1 = r'\[\e[32m\]\u@\h\[\e[0m\]:\[\e[34m\]\w\[\e[0m\]\$ '
        self.proc = subprocess.Popen(
            ["bash", "--norc", "-i"],
            preexec_fn=os.setsid,
            stdin=slave_fd,
            stdout=slave_fd,
            stderr=slave_fd,
            cwd=self.workdir,
            env={**os.environ, "PS1": ps1, "TERM": "xterm-256color"},
            text=False,
            bufsize=0,
        )
        os.close(slave_fd)
        import fcntl
        flags = fcntl.fcntl(self.master_fd, fcntl.F_GETFL)
        fcntl.fcntl(self.master_fd, fcntl.F_SETFL, flags | os.O_NONBLOCK)
        self._append("Microsoft(R) Windows 98\n(C)Copyright Microsoft Corp 1981-1998.\n\n", "#808080")

    def _read_output(self):
        if self.master_fd is None:
            return
        try:
            r, _, _ = select.select([self.master_fd], [], [], 0)
            if r:
                data = os.read(self.master_fd, 4096)
                if data:
                    text = data.decode("utf-8", errors="replace")
                    ansi = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
                    clean = ansi.sub("", text)
                    clean = clean.replace("\r\n", "\n").replace("\r", "\n")
                    self._append(clean, None)
                    # aggiorna input_start su prompt shell ($/#) o prompt programma (: )
                    stripped = clean.rstrip()
                    if (stripped.endswith("$") or stripped.endswith("#") or stripped.endswith(">") or stripped.endswith(":")
                        or "$ " in clean[-6:] or ": " in clean[-10:]):
                        self._input_start = self.output.document().characterCount() - 1
                    if "Windows 98" in clean:
                        self._input_start = self.output.document().characterCount() - 1
                    # anche se è solo un prompt senza newline (es. "Inserisci...: "), aggiorna subito
                    if clean.endswith(": ") or clean.endswith("$ "):
                        self._input_start = self.output.document().characterCount() - 1
        except OSError:
            pass

    def _append(self, text, color=None):
        cursor = self.output.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)
        fmt = QTextCharFormat()
        fmt.setForeground(QColor(color) if color else QColor("#c0c0c0"))
        for ch in text:
            # ignora controllo tranne \n \t e gestisci backspace come cancellazione
            if ch == "\x08" or ch == "\x7f":
                if cursor.position() > self._input_start:
                    cursor.deletePreviousChar()
                continue
            if ch == "\r":
                continue
            if ord(ch) < 32 and ch not in ("\n", "\t"):
                # carattere di controllo invisibile — ignora invece di mostrare quadratino
                continue
            cursor.insertText(ch, fmt)
        self.output.setTextCursor(cursor)
        self.output.ensureCursorVisible()
        sb = self.output.verticalScrollBar()
        sb.setValue(sb.maximum())

    def _clear(self):
        self.output.clear()
        self._input_start = 0

    def _get_input_text(self):
        """Prende solo ciò che l'utente ha digitato dopo il prompt (shell $  o programma : )."""
        block_text = self.output.textCursor().block().text()
        # cerca l'ultimo delimitatore di prompt nella riga corrente
        for delim in ["$ ", "# ", "> ", ": ", "C:\\> ", "]$ "]:
            if delim in block_text:
                return block_text.rsplit(delim, 1)[-1]
        # se nessun delimitatore, usa il testo dopo _input_start come fallback
        try:
            doc = self.output.document()
            if 0 <= self._input_start < doc.characterCount():
                cur = QTextCursor(doc)
                cur.setPosition(self._input_start)
                cur.movePosition(QTextCursor.MoveOperation.End, QTextCursor.MoveMode.KeepAnchor)
                txt = cur.selectedText().replace("\u2029", "\n")
                # se contiene newline, prendi ultima riga
                if "\n" in txt:
                    txt = txt.split("\n")[-1]
                return txt
        except:
            pass
        return block_text

    def _on_cursor_changed(self):
        # non fare nulla qui, gestito in eventFilter
        pass

    def eventFilter(self, obj, event):
        from PyQt6.QtCore import QEvent
        if obj is self.output:
            if event.type() == QEvent.Type.KeyPress:
                key = event.key()
                mods = event.modifiers()
                cursor = self.output.textCursor()
                pos = cursor.position()

                # Ctrl+L clear
                if mods & Qt.KeyboardModifier.ControlModifier and key == Qt.Key.Key_L:
                    self._clear()
                    return True
                if mods & Qt.KeyboardModifier.ControlModifier and key == Qt.Key.Key_C:
                    if self.master_fd:
                        try: os.write(self.master_fd, b"\x03")
                        except OSError: pass
                    return True
                if mods & Qt.KeyboardModifier.ControlModifier and key == Qt.Key.Key_D:
                    if self.master_fd:
                        try: os.write(self.master_fd, b"\x04")
                        except OSError: pass
                    return True
                # Ctrl+A select only input line
                if mods & Qt.KeyboardModifier.ControlModifier and key == Qt.Key.Key_A:
                    nc = self.output.textCursor()
                    nc.setPosition(self._input_start)
                    nc.movePosition(QTextCursor.MoveOperation.End, QTextCursor.MoveMode.KeepAnchor)
                    self.output.setTextCursor(nc)
                    return True

                # Navigation — impedisci di andare prima dell'input
                if key == Qt.Key.Key_Left:
                    if pos <= self._input_start:
                        return True
                if key == Qt.Key.Key_Backspace:
                    if pos <= self._input_start:
                        return True
                    # invia DEL a pty, l'eco gestirà la cancellazione visiva
                    if self.master_fd:
                        try: os.write(self.master_fd, b"\x7f")
                        except OSError: pass
                    return True
                if key == Qt.Key.Key_Home:
                    nc = self.output.textCursor()
                    nc.setPosition(self._input_start)
                    self.output.setTextCursor(nc)
                    return True
                if key in (Qt.Key.Key_Up, Qt.Key.Key_Down):
                    if self.master_fd:
                        seq = b"\x1b[A" if key == Qt.Key.Key_Up else b"\x1b[B"
                        try: os.write(self.master_fd, seq)
                        except OSError: pass
                    return True

                if key in (Qt.Key.Key_Return, Qt.Key.Key_Enter):
                    # i caratteri digitati sono già nel buffer del pty (inviati uno a uno),
                    # basta inviare newline per sottomettere la riga — altrimenti duplica
                    if self.master_fd:
                        try: os.write(self.master_fd, b"\n")
                        except OSError: pass
                    nc = self.output.textCursor()
                    nc.movePosition(QTextCursor.MoveOperation.End)
                    self.output.setTextCursor(nc)
                    return True

                if pos < self._input_start:
                    nc = self.output.textCursor()
                    nc.movePosition(QTextCursor.MoveOperation.End)
                    self.output.setTextCursor(nc)
                    return False

                # Permetti scrittura solo dopo _input_start — intercetta inserimento per inviare a pty?
                # Invece di scrivere direttamente nel QPlainTextEdit, scriviamo nel pty e lasciamo che l'echo del pty ce lo ridia.
                # Ma pty echo è abilitato, quindi se scriviamo nel widget e poi nel pty, duplichiamo.
                # Soluzione: intercetta caratteri stampabili e inviali solo al pty, NON inserirli direttamente.
                # Però dobbiamo mostrare subito l'eco? Con pty canonical, l'eco arriva via _read_output dopo pochi ms.
                # Per reattività, possiamo sia scrivere nel widget (locale) che nel pty — ma poi l'eco del pty duplica.
                # Meglio: disabilitare echo del pty e gestire locale? Complicato.
                # Approccio semplice Win98: scrivi locale + invia a pty senza eco (stty -echo)? No.
                # Scelta: scrivi SOLO nel pty e aspetta eco — per ora lasciamo scrittura locale + pty ma filtriamo eco duplicato?
                # Per semplicità qui: intercetta caratteri e invia a pty, e lascia che Qt inserisca localmente, poi _read_output filtrerà duplicati? Per ora accettiamo duplicato minimo e gestiamo così:
                # Se è carattere stampabile senza Ctrl/Alt, invia a pty e lascia anche inserimento locale (duplice ma con pty raw potrebbe non duplicare se bash in cooked?)
                # Test con pty: bash echoa, quindi vedremmo doppio. Per evitarlo, inviamo a pty e blocchiamo inserimento locale, aspettando eco.
                if event.text() and not (mods & Qt.KeyboardModifier.ControlModifier) and not (mods & Qt.KeyboardModifier.AltModifier):
                    ch = event.text()
                    if ch:
                        if self.master_fd:
                            try: os.write(self.master_fd, ch.encode())
                            except OSError: pass
                        return True

                # per altri tasti (Tab, etc) lascia passare ma solo se in input area
                if pos < self._input_start:
                    return True

            elif event.type() == QEvent.Type.MouseButtonPress:
                # se clicca prima dell'input, sposta in fondo
                cursor = self.output.cursorForPosition(event.pos())
                if cursor.position() < self._input_start:
                    self.output.setTextCursor(self.output.textCursor())
                    nc = self.output.textCursor()
                    nc.movePosition(QTextCursor.MoveOperation.End)
                    self.output.setTextCursor(nc)
                    return True
        return super().eventFilter(obj, event)

    def run_command(self, cmd: str):
        if self.master_fd:
            try:
                os.write(self.master_fd, (cmd + "\n").encode())
                # l'echo del pty mostrerà il comando, non serve append manuale (evita duplicazione)
            except OSError:
                pass

    def set_workdir(self, path):
        self.workdir = path
        self.run_command(f'cd "{path}"')

    def closeEvent(self, event):
        self.timer.stop()
        if self.proc:
            try: os.killpg(os.getpgid(self.proc.pid), signal.SIGTERM)
            except Exception: pass
        if self.master_fd:
            try: os.close(self.master_fd)
            except Exception: pass
        super().closeEvent(event)
