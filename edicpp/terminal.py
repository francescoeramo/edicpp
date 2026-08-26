import os
import pty
import select
import subprocess
import signal
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QPlainTextEdit
from PyQt6.QtCore import QTimer, Qt
from PyQt6.QtGui import QFont, QTextCursor, QColor, QTextCharFormat


class EmbeddedTerminal(QWidget):
    """Win98 MS-DOS prompt — nero su nero, header grigio."""
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
        # outer sunken frame like Win98
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
        self.clear_btn.setFixedWidth(52)
        self.clear_btn.setStyleSheet("font-size:10px; padding:1px 4px;")
        self.clear_btn.clicked.connect(lambda: self.output.clear())
        hl.addWidget(self.clear_btn)

        layout.addWidget(header)

        # terminal area sunken
        self.output = QPlainTextEdit()
        self.output.setReadOnly(False)
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
            env={**os.environ, "PS1": r"C:\\> ", "TERM": "xterm-256color"},
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
        fmt.setForeground(QColor(color) if color else QColor("#c0c0c0"))
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
                cmd = line.split("C:\\>")[-1].strip() if "C:\\>" in line else self.output.textCursor().block().text().strip()
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
                self._append(f"\nC:\\> {cmd}\n", "#ffffff")
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
