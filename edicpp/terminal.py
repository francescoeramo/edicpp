import os
import pty
import select
import subprocess
import signal
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QPlainTextEdit
from PyQt6.QtCore import QTimer, Qt
from PyQt6.QtGui import QFont, QTextCursor, QColor, QTextCharFormat


class EmbeddedTerminal(QWidget):
    """Arcade terminal — neon cyan on deep navy."""
    def __init__(self, workdir=None, parent=None):
        super().__init__(parent)
        self.workdir = workdir or os.path.expanduser("~")
        self.master_fd = None
        self.proc = None
        self._setup_ui()
        self._spawn_shell()
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._read_output)
        self.timer.start(30)

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        header = QWidget()
        header.setFixedHeight(34)
        header.setStyleSheet("background:#0a0c1e; border:1px solid #1e2348; border-radius:8px;")
        hl = QHBoxLayout(header)
        hl.setContentsMargins(10, 4, 8, 4)
        hl.setSpacing(8)
        title = QLabel("◉ TERMINALE")
        title.setStyleSheet("color:#00e5ff; font-size:10px; font-weight:500; letter-spacing:0.8px; border:none;")
        hl.addWidget(title)
        # scanline hint
        hint = QLabel("— bash — arcade ready")
        hint.setStyleSheet("color:#6b73a3; font-size:10px; font-weight:400; border:none;")
        hl.addWidget(hint)
        hl.addStretch()
        led = QLabel("● REC")
        led.setStyleSheet("color:#ff2e97; font-size:10px; font-weight:500; border:none;")
        hl.addWidget(led)
        self.clear_btn = QPushButton("Pulisci")
        self.clear_btn.setFixedHeight(24)
        self.clear_btn.setFixedWidth(72)
        # override to lighter weight
        self.clear_btn.setStyleSheet("font-weight:400; font-size:11px;")
        self.clear_btn.clicked.connect(lambda: self.output.clear())
        hl.addWidget(self.clear_btn)
        # add small bottom spacing container to avoid overlap
        wrapper = QWidget()
        wl = QVBoxLayout(wrapper)
        wl.setContentsMargins(0, 0, 0, 0)
        wl.setSpacing(6)
        wl.addWidget(header)

        layout.addWidget(wrapper)

        self.output = QPlainTextEdit()
        self.output.setReadOnly(False)
        self.output.setStyleSheet("""
            QPlainTextEdit {
                background:#06080f;
                border:1px solid #1e2348;
                border-radius:8px;
                color:#dbe2ff;
                font-family:'JetBrains Mono','IBM Plex Mono','Courier New',monospace;
                font-size:12px;
                padding:8px;
            }
        """)
        font = QFont("JetBrains Mono")
        if not font.exactMatch():
            font = QFont("IBM Plex Mono")
        font.setPointSize(10)
        font.setWeight(QFont.Weight.Normal)
        self.output.setFont(font)
        layout.addWidget(self.output, 1)
        self.output.installEventFilter(self)

    def _spawn_shell(self):
        self.master_fd, slave_fd = pty.openpty()
        self.proc = subprocess.Popen(
            ["bash", "--norc", "-i"],
            preexec_fn=os.setsid,
            stdin=slave_fd,
            stdout=slave_fd,
            stderr=slave_fd,
            cwd=self.workdir,
            env={**os.environ, "PS1": r"\[\e[38;5;51m\]▸\[\e[0m\] ", "TERM": "xterm-256color"},
            text=False,
            bufsize=0,
        )
        os.close(slave_fd)
        import fcntl
        flags = fcntl.fcntl(self.master_fd, fcntl.F_GETFL)
        fcntl.fcntl(self.master_fd, fcntl.F_SETFL, flags | os.O_NONBLOCK)
        self._append("\n", "#6b73a3")

    def _read_output(self):
        if self.master_fd is None:
            return
        try:
            r, _, _ = select.select([self.master_fd], [], [], 0)
            if r:
                data = os.read(self.master_fd, 4096)
                if data:
                    text = data.decode("utf-8", errors="replace")
                    import re
                    ansi = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
                    clean = ansi.sub("", text)
                    clean = clean.replace("\r\n", "\n").replace("\r", "\n")
                    self._append(clean, None)
        except OSError:
            pass

    def _append(self, text, color=None):
        cursor = self.output.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)
        fmt = QTextCharFormat()
        fmt.setForeground(QColor(color) if color else QColor("#dbe2ff"))
        cursor.insertText(text, fmt)
        self.output.setTextCursor(cursor)
        self.output.ensureCursorVisible()
        sb = self.output.verticalScrollBar()
        sb.setValue(sb.maximum())

    def eventFilter(self, obj, event):
        from PyQt6.QtCore import QEvent
        if obj is self.output and event.type() == QEvent.Type.KeyPress:
            key = event.key()
            mods = event.modifiers()
            if mods & Qt.KeyboardModifier.ControlModifier and key == Qt.Key.Key_L:
                self.output.clear()
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
            if key in (Qt.Key.Key_Return, Qt.Key.Key_Enter):
                cursor = self.output.textCursor()
                cursor.select(QTextCursor.SelectionType.LineUnderCursor)
                line = cursor.selectedText()
                cmd = line.split("▸")[-1].strip() if "▸" in line else self.output.textCursor().block().text().strip()
                if self.master_fd:
                    try: os.write(self.master_fd, (cmd + "\n").encode())
                    except OSError: pass
                nc = self.output.textCursor()
                nc.movePosition(QTextCursor.MoveOperation.End)
                self.output.setTextCursor(nc)
                return True
        return super().eventFilter(obj, event)

    def run_command(self, cmd: str):
        if self.master_fd:
            try:
                os.write(self.master_fd, (cmd + "\n").encode())
                self._append(f"\n$ {cmd}\n", "#00e5ff")
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
