import os
import pty
import select
import subprocess
import signal
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QPlainTextEdit
from PyQt6.QtCore import QTimer, Qt
from PyQt6.QtGui import QFont, QTextCursor, QColor, QTextCharFormat


class EmbeddedTerminal(QWidget):
    """Embedded interactive terminal at bottom. Uses pty + bash. Retro amber style."""
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
        header.setStyleSheet("background:#f4e8c1; border-bottom:3px solid #1a1207; border-top:2px solid #3d2810;")
        hl = QHBoxLayout(header)
        hl.setContentsMargins(10, 4, 6, 4)
        hl.setSpacing(8)
        title = QLabel("▓ TERMINALE  [bash]  ■ REC")
        title.setStyleSheet("color:#1a1207; font-size:10px; font-weight:bold; letter-spacing:1px; border:none;")
        hl.addWidget(title)
        hl.addStretch()
        # retro led
        led = QLabel("●")
        led.setStyleSheet("color:#00c800; font-size:14px; border:none;")
        hl.addWidget(led)
        self.clear_btn = QPushButton("[ PULISCI ]")
        self.clear_btn.setFixedHeight(24)
        self.clear_btn.setFixedWidth(94)
        self.clear_btn.clicked.connect(lambda: self.output.clear())
        hl.addWidget(self.clear_btn)

        layout.addWidget(header)

        self.output = QPlainTextEdit()
        self.output.setReadOnly(False)
        self.output.setStyleSheet("""
            QPlainTextEdit {
                background:#0a0804;
                border:2px solid #3d2810;
                border-top:none;
                color:#ffb000;
                font-family:'IBM Plex Mono','JetBrains Mono','Courier New',monospace;
                font-size:12px;
                padding:6px;
            }
        """)
        font = QFont("IBM Plex Mono")
        if not font.exactMatch():
            font = QFont("JetBrains Mono")
        font.setPointSize(10)
        font.setStyleHint(QFont.StyleHint.Monospace)
        self.output.setFont(font)
        self.input_history = []
        self.hist_idx = -1
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
            env={**os.environ, "PS1": r"\[\e[38;5;214m\]▶\[\e[0m\] ", "TERM": "xterm-256color"},
            text=False,
            bufsize=0,
        )
        os.close(slave_fd)
        import fcntl
        flags = fcntl.fcntl(self.master_fd, fcntl.F_GETFL)
        fcntl.fcntl(self.master_fd, fcntl.F_SETFL, flags | os.O_NONBLOCK)
        self._append("\n", "#8a7a5a")

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
        if color:
            fmt.setForeground(QColor(color))
        else:
            fmt.setForeground(QColor("#ffb000"))
        cursor.insertText(text, fmt) if color else cursor.insertText(text)
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
                    try:
                        os.write(self.master_fd, b"\x03")
                    except OSError:
                        pass
                return True
            if mods & Qt.KeyboardModifier.ControlModifier and key == Qt.Key.Key_D:
                if self.master_fd:
                    try:
                        os.write(self.master_fd, b"\x04")
                    except OSError:
                        pass
                return True
            if key in (Qt.Key.Key_Return, Qt.Key.Key_Enter):
                cursor = self.output.textCursor()
                cursor.select(QTextCursor.SelectionType.LineUnderCursor)
                line = cursor.selectedText()
                if "▶" in line:
                    cmd = line.split("▶")[-1].strip()
                else:
                    block_text = self.output.textCursor().block().text()
                    cmd = block_text.strip()
                to_send = cmd
                if self.master_fd:
                    try:
                        os.write(self.master_fd, (to_send + "\n").encode())
                    except OSError:
                        pass
                new_cursor = self.output.textCursor()
                new_cursor.movePosition(QTextCursor.MoveOperation.End)
                self.output.setTextCursor(new_cursor)
                return True
        return super().eventFilter(obj, event)

    def run_command(self, cmd: str):
        if self.master_fd:
            try:
                os.write(self.master_fd, (cmd + "\n").encode())
                self._append(f"\n$ {cmd}\n", "#ff7a00")
            except OSError:
                pass

    def set_workdir(self, path):
        self.workdir = path
        self.run_command(f'cd "{path}"')

    def closeEvent(self, event):
        self.timer.stop()
        if self.proc:
            try:
                os.killpg(os.getpgid(self.proc.pid), signal.SIGTERM)
            except Exception:
                pass
        if self.master_fd:
            try:
                os.close(self.master_fd)
            except Exception:
                pass
        super().closeEvent(event)
