import os
import pty
import select
import subprocess
import signal
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QPlainTextEdit
from PyQt6.QtCore import QTimer, Qt, pyqtSignal
from PyQt6.QtGui import QFont, QTextCursor, QColor, QTextCharFormat


class EmbeddedTerminal(QWidget):
    """Embedded interactive terminal at bottom. Uses pty + bash."""
    def __init__(self, workdir=None, parent=None):
        super().__init__(parent)
        self.workdir = workdir or os.path.expanduser("~")
        self.master_fd = None
        self.proc = None
        self._setup_ui()
        self._spawn_shell()
        # timer to poll output
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._read_output)
        self.timer.start(30)

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # header
        header = QWidget()
        header.setStyleSheet("background:#0f1423; border-bottom:1px solid #1e2030;")
        hl = QHBoxLayout(header)
        hl.setContentsMargins(12, 6, 8, 6)
        title = QLabel("⟐  TERMINALE")
        title.setStyleSheet("color:#7aa2f7; font-size:11px; font-weight:bold; letter-spacing:1px; border:none;")
        hl.addWidget(title)
        hl.addStretch()
        self.clear_btn = QPushButton("Pulisci")
        self.clear_btn.setFixedHeight(26)
        self.clear_btn.setStyleSheet("QPushButton{background:#1a1e32; border:1px solid #2a2e44; border-radius:6px; padding:2px 12px; font-size:12px;} QPushButton:hover{border-color:#7aa2f7; color:#7aa2f7;}")
        self.clear_btn.clicked.connect(lambda: self.output.clear())
        hl.addWidget(self.clear_btn)

        layout.addWidget(header)

        self.output = QPlainTextEdit()
        self.output.setReadOnly(False)
        self.output.setStyleSheet("""
            QPlainTextEdit {
                background:#0a0e1a;
                border:none;
                border-radius:0;
                color:#c0caf5;
                font-family:'JetBrains Mono','Fira Code',monospace;
                font-size:13px;
                padding:6px;
            }
        """)
        font = QFont("JetBrains Mono")
        if not font.exactMatch():
            font = QFont("Fira Code")
        font.setPointSize(10)
        self.output.setFont(font)
        # keep cursor at end
        self.input_history = []
        self.hist_idx = -1
        self.current_cmd = ""
        layout.addWidget(self.output, 1)

        # we capture key presses via eventFilter
        self.output.installEventFilter(self)
        self.output.setPlaceholderText("")

    def _spawn_shell(self):
        self.master_fd, slave_fd = pty.openpty()
        self.proc = subprocess.Popen(
            ["bash", "--norc", "-i"],
            preexec_fn=os.setsid,
            stdin=slave_fd,
            stdout=slave_fd,
            stderr=slave_fd,
            cwd=self.workdir,
            env={**os.environ, "PS1": r"\[\e[38;5;111m\]❯\[\e[0m\] ", "TERM": "xterm-256color"},
            text=False,
            bufsize=0,
        )
        os.close(slave_fd)
        # make non-blocking
        import fcntl
        flags = fcntl.fcntl(self.master_fd, fcntl.F_GETFL)
        fcntl.fcntl(self.master_fd, fcntl.F_SETFL, flags | os.O_NONBLOCK)
        # welcome
        self._append("\n", "#565f89")

    def _read_output(self):
        if self.master_fd is None:
            return
        try:
            r, _, _ = select.select([self.master_fd], [], [], 0)
            if r:
                data = os.read(self.master_fd, 4096)
                if data:
                    text = data.decode("utf-8", errors="replace")
                    # strip some ANSI? keep simple - remove most escapes but keep colors via plain
                    import re
                    # remove ANSI escape sequences for simplicity but keep text
                    ansi = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
                    clean = ansi.sub("", text)
                    # avoid flooding with \r
                    clean = clean.replace("\r\n", "\n").replace("\r", "\n")
                    self._append(clean, None)
        except OSError:
            pass

    def _append(self, text, color=None):
        # append without moving user input weirdly
        cursor = self.output.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)
        fmt = QTextCharFormat()
        if color:
            fmt.setForeground(QColor(color))
        else:
            fmt.setForeground(QColor("#c0caf5"))
        # insert
        # Use plain insertion to keep formatting
        cursor.insertText(text, fmt) if color else cursor.insertText(text)
        self.output.setTextCursor(cursor)
        self.output.ensureCursorVisible()
        # autoscroll
        sb = self.output.verticalScrollBar()
        sb.setValue(sb.maximum())

    def eventFilter(self, obj, event):
        from PyQt6.QtCore import QEvent
        from PyQt6.QtGui import QKeyEvent
        if obj is self.output and event.type() == QEvent.Type.KeyPress:
            key = event.key()
            mods = event.modifiers()
            # Ctrl+L clear
            if mods & Qt.KeyboardModifier.ControlModifier and key == Qt.Key.Key_L:
                self.output.clear()
                return True
            # Ctrl+C -> SIGINT
            if mods & Qt.KeyboardModifier.ControlModifier and key == Qt.Key.Key_C:
                if self.master_fd:
                    try:
                        os.write(self.master_fd, b"\x03")
                    except OSError:
                        pass
                return True
            # Ctrl+D -> EOF
            if mods & Qt.KeyboardModifier.ControlModifier and key == Qt.Key.Key_D:
                if self.master_fd:
                    try:
                        os.write(self.master_fd, b"\x04")
                    except OSError:
                        pass
                return True
            if key in (Qt.Key.Key_Return, Qt.Key.Key_Enter):
                # get current line after last newline? Simpler: get text after last prompt char?
                # Instead, extract last line from cursor line
                cursor = self.output.textCursor()
                cursor.select(QTextCursor.SelectionType.LineUnderCursor)
                line = cursor.selectedText()
                # The line contains the prompt char + command; try to extract after ❯
                if "❯" in line:
                    cmd = line.split("❯")[-1].strip()
                else:
                    # fallback: last line up to cursor
                    block_text = self.output.textCursor().block().text()
                    cmd = block_text.strip()
                    # if empty, try to get typed after last newline
                    if not cmd:
                        cmd = ""
                # Alternative robust: track typed buffer? Simpler send whatever after prompt or whole line if no prompt
                # We actually send the text after prompt, but we need to know what user typed since last output
                # Simpler approach: send line content after prompt, or if no prompt send empty
                # If we couldn't parse, send empty newline
                to_send = cmd
                # Write to pty
                if self.master_fd:
                    try:
                        os.write(self.master_fd, (to_send + "\n").encode())
                    except OSError:
                        pass
                # move cursor to end and add newline visually (shell will echo)
                # Let shell echo handle it, but ensure cursor at end
                new_cursor = self.output.textCursor()
                new_cursor.movePosition(QTextCursor.MoveOperation.End)
                self.output.setTextCursor(new_cursor)
                return True
            if key == Qt.Key.Key_Backspace:
                # prevent deleting prompt/output - allow only if not at prompt start
                # naive: allow
                pass
        return super().eventFilter(obj, event)

    def run_command(self, cmd: str):
        """Programmatically run a command in terminal."""
        if self.master_fd:
            try:
                os.write(self.master_fd, (cmd + "\n").encode())
                self._append(f"\n$ {cmd}\n", "#7aa2f7")
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
