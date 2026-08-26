#!/usr/bin/env python3
import os
import sys
import subprocess
import re
from pathlib import Path

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QSplitter,
    QTreeView, QTabWidget, QPlainTextEdit, QLabel, QPushButton, QFileDialog,
    QMessageBox, QDialog, QScrollArea, QFrame, QLineEdit, QStatusBar, QToolBar,
    QMenuBar, QSizePolicy, QInputDialog
)
from PyQt6.QtCore import Qt, QFileInfo, QDir, QSize, QTimer, pyqtSignal
from PyQt6.QtGui import (
    QAction, QFont, QColor, QPainter, QTextFormat, QTextCursor, QIcon, QKeySequence, QFontDatabase
)

from .theme import STYLESHEET
from .highlighter import CppHighlighter
from .terminal import EmbeddedTerminal

# ───────────────── Editor with line numbers ─────────────────

class LineNumberArea(QWidget):
    def __init__(self, editor):
        super().__init__(editor)
        self.editor = editor

    def sizeHint(self):
        return QSize(self.editor.lineNumberAreaWidth(), 0)

    def paintEvent(self, event):
        self.editor.lineNumberAreaPaintEvent(event)


class CodeEditor(QPlainTextEdit):
    def __init__(self, file_path=None, parent=None):
        super().__init__(parent)
        self.file_path = file_path
        self._line_number_area = LineNumberArea(self)
        font = QFont("JetBrains Mono")
        if not font.exactMatch():
            font = QFont("Fira Code")
            if not font.exactMatch():
                font = QFont("Cascadia Code")
                if not font.exactMatch():
                    font = QFontDatabase.systemFont(QFontDatabase.SystemFont.FixedFont)
        font.setPointSize(11)
        font.setStyleHint(QFont.StyleHint.Monospace)
        self.setFont(font)
        self.setLineWrapMode(QPlainTextEdit.LineWrapMode.NoWrap)
        self.setTabStopDistance(QFontMetricsF(font).horizontalAdvance(' ') * 4)

        self.highlighter = CppHighlighter(self.document())
        self.setStyleSheet("""
            QPlainTextEdit {
                background:#0a0e1a;
                color:#c0caf5;
                border:none;
                border-radius:0;
                selection-background-color:#364a82;
                padding-left:4px;
            }
        """)
        self.blockCountChanged.connect(self.updateLineNumberAreaWidth)
        self.updateRequest.connect(self.updateLineNumberArea)
        self.cursorPositionChanged.connect(self.highlightCurrentLine)
        self.updateLineNumberAreaWidth(0)
        self.highlightCurrentLine()
        # placeholder for empty editor
        self.setPlaceholderText("// Inizia a scrivere il tuo codice C++...")

    def lineNumberAreaWidth(self):
        digits = len(str(max(1, self.blockCount())))
        space = 14 + self._fm().horizontalAdvance('9') * digits
        return space

    def updateLineNumberAreaWidth(self, _):
        self.setViewportMargins(self.lineNumberAreaWidth(), 0, 0, 0)

    def updateLineNumberArea(self, rect, dy):
        if dy:
            self._line_number_area.scroll(0, dy)
        else:
            self._line_number_area.update(0, rect.y(), self._line_number_area.width(), rect.height())
        if rect.contains(self.viewport().rect()):
            self.updateLineNumberAreaWidth(0)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        cr = self.contentsRect()
        self._line_number_area.setGeometry(cr.left(), cr.top(), self.lineNumberAreaWidth(), cr.height())

    def lineNumberAreaPaintEvent(self, event):
        painter = QPainter(self._line_number_area)
        painter.fillRect(event.rect(), QColor("#0f1423"))
        block = self.firstVisibleBlock()
        block_number = block.blockNumber()
        top = self.blockBoundingGeometry(block).translated(self.contentOffset()).top()
        bottom = top + self.blockBoundingRect(block).height()
        while block.isValid() and top <= event.rect().bottom():
            if block.isVisible() and bottom >= event.rect().top():
                number = str(block_number + 1)
                painter.setPen(QColor("#565f89") if block_number != self.textCursor().blockNumber() else QColor("#7aa2f7"))
                # highlight current
                if block_number == self.textCursor().blockNumber():
                    painter.setPen(QColor("#c0caf5"))
                    f = painter.font()
                    f.setBold(True)
                    painter.setFont(f)
                painter.drawText(0, int(top), self._line_number_area.width() - 8, self._fm().height(),
                                 Qt.AlignmentFlag.AlignRight, number)
                # reset
                painter.setPen(QColor("#565f89"))
                f = painter.font()
                f.setBold(False)
                painter.setFont(f)
            block = block.next()
            top = bottom
            bottom = top + self.blockBoundingRect(block).height()
            block_number += 1

    def highlightCurrentLine(self):
        extra = []
        if not self.isReadOnly():
            sel = QTextEdit.ExtraSelection()
            sel.format.setBackground(QColor("#1a1e32"))
            sel.format.setProperty(QTextFormat.Property.FullWidthSelection, True)
            sel.cursor = self.textCursor()
            sel.cursor.clearSelection()
            extra.append(sel)
        self.setExtraSelections(extra)

    def keyPressEvent(self, event):
        # auto indent on Enter
        if event.key() in (Qt.Key.Key_Return, Qt.Key.Key_Enter):
            cursor = self.textCursor()
            block_text = cursor.block().text()
            indent = re.match(r"^\s*", block_text).group(0)
            # extra indent after {
            if block_text.rstrip().endswith("{"):
                indent += "    "
            super().keyPressEvent(event)
            self.insertPlainText(indent)
            return
        # auto close brackets/quotes
        pairs = {"(": ")", "[": "]", "{": "}", '"': '"', "'": "'"}
        if event.text() in pairs:
            cursor = self.textCursor()
            # if already has closing char next to cursor, just move over
            if cursor.block().text()[cursor.positionInBlock():cursor.positionInBlock()+1] == pairs[event.text()] and event.text() in ('"', "'", ")", "]", "}"):
                cursor.movePosition(QTextCursor.MoveOperation.Right)
                self.setTextCursor(cursor)
                return
            super().keyPressEvent(event)
            # insert closing only for opening chars
            if event.text() in "([{":
                cur = self.textCursor()
                pos = cur.position()
                cur.insertText(pairs[event.text()])
                cur.setPosition(pos)
                self.setTextCursor(cur)
            elif event.text() in ('"', "'"):
                # already handled above, but for completeness
                pass
            return
        # Tab -> 4 spaces
        if event.key() == Qt.Key.Key_Tab:
            self.insertPlainText("    ")
            return
        # Backtab unindent
        if event.key() == Qt.Key.Key_Backtab:
            cursor = self.textCursor()
            cursor.movePosition(QTextCursor.MoveOperation.StartOfLine)
            cursor.movePosition(QTextCursor.MoveOperation.Right, QTextCursor.MoveMode.KeepAnchor, 4)
            if cursor.selectedText() == "    ":
                cursor.removeSelectedText()
            return
        super().keyPressEvent(event)

    def toggle_comment(self):
        cursor = self.textCursor()
        start = cursor.selectionStart()
        end = cursor.selectionEnd()
        cursor.setPosition(start)
        start_block = cursor.blockNumber()
        cursor.setPosition(end)
        end_block = cursor.blockNumber()
        # for single line without selection, just that line
        if start == end:
            end_block = start_block
        cursor.beginEditBlock()
        for i in range(start_block, end_block + 1):
            block = self.document().findBlockByNumber(i)
            text = block.text()
            pos = block.position()
            cur = QTextCursor(block)
            # check if commented
            stripped = text.lstrip()
            indent_len = len(text) - len(stripped)
            if stripped.startswith("//"):
                # uncomment
                cur.setPosition(pos + indent_len)
                cur.setPosition(pos + indent_len + 2, QTextCursor.MoveMode.KeepAnchor)
                cur.removeSelectedText()
            else:
                cur.setPosition(pos + indent_len)
                cur.insertText("//")
        cursor.endEditBlock()

    def _fm(self):
        return super().fontMetrics()

# need QFontMetricsF import after define
from PyQt6.QtGui import QFontMetricsF
from PyQt6.QtWidgets import QTextEdit

# ───────────────── Search Bar ─────────────────

class SearchBar(QWidget):
    def __init__(self, editor_getter, parent=None):
        super().__init__(parent)
        self.editor_getter = editor_getter
        self.setStyleSheet("background:#16161e; border:1px solid #1e2030; border-radius:8px;")
        layout = QHBoxLayout(self)
        layout.setContentsMargins(8, 6, 8, 6)
        layout.setSpacing(6)
        lbl = QLabel("Cerca")
        lbl.setStyleSheet("color:#565f89; font-size:12px; border:none;")
        layout.addWidget(lbl)
        self.input = QLineEdit()
        self.input.setPlaceholderText("Cerca nel file…")
        self.input.setStyleSheet("background:#0a0e1a; border:1px solid #2a2e44; border-radius:6px; padding:6px 10px;")
        layout.addWidget(self.input, 1)
        self.prev_btn = QPushButton("↑")
        self.next_btn = QPushButton("↓")
        self.close_btn = QPushButton("✕")
        for b in (self.prev_btn, self.next_btn, self.close_btn):
            b.setFixedSize(28, 28)
            b.setStyleSheet("QPushButton{background:#1a1e32; border:1px solid #2a2e44; border-radius:6px;} QPushButton:hover{border-color:#7aa2f7; color:#7aa2f7;}")
        layout.addWidget(self.prev_btn)
        layout.addWidget(self.next_btn)
        layout.addWidget(self.close_btn)
        self.hide()
        self.input.returnPressed.connect(lambda: self.find_next())
        self.prev_btn.clicked.connect(lambda: self.find_prev())
        self.next_btn.clicked.connect(lambda: self.find_next())
        self.close_btn.clicked.connect(self.hide_bar)
        self.input.textChanged.connect(self.highlight_all)

    def show_bar(self):
        self.show()
        self.input.setFocus()
        self.input.selectAll()

    def hide_bar(self):
        self.hide()
        ed = self.editor_getter()
        if ed:
            ed.setFocus()

    def highlight_all(self):
        # simple: find occurrences are handled by find_next logic; we just not highlight all for now
        pass

    def find_next(self):
        ed = self.editor_getter()
        if not ed or not self.input.text():
            return
        ed.find(self.input.text())

    def find_prev(self):
        ed = self.editor_getter()
        if not ed or not self.input.text():
            return
        ed.find(self.input.text(), QTextDocument.FindFlag.FindBackward)

from PyQt6.QtGui import QTextDocument

# ───────────────── Guide Dialog ─────────────────

class GuideDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Guida — EdiCpp")
        self.setModal(True)
        self.setMinimumSize(720, 620)
        self.setStyleSheet(STYLESHEET + "QDialog{background:#0f1423;}")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(28, 24, 28, 24)
        layout.setSpacing(16)

        title = QLabel("EdiCpp — Guida rapida")
        title.setObjectName("Title")
        subtitle = QLabel("Editor leggero per C++ • Pensato per Fedora • Bello, veloce, essenziale")
        subtitle.setObjectName("Subtitle")
        layout.addWidget(title)
        layout.addWidget(subtitle)

        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.HLine)
        sep.setStyleSheet("color:#1e2030;")
        layout.addWidget(sep)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea{border:none; background:transparent;} QWidget{background:transparent;}")
        inner = QWidget()
        v = QVBoxLayout(inner)
        v.setSpacing(14)

        def section(heading, items):
            h = QLabel(heading)
            h.setObjectName("Heading")
            v.addWidget(h)
            for it in items:
                row = QHBoxLayout()
                dot = QLabel("•")
                dot.setStyleSheet("color:#7aa2f7; font-weight:bold;")
                dot.setFixedWidth(14)
                lbl = QLabel(it)
                lbl.setWordWrap(True)
                lbl.setStyleSheet("color:#a9b1d6; font-size:13px;")
                row.addWidget(dot)
                row.addWidget(lbl, 1)
                v.addLayout(row)
            v.addSpacing(6)

        section("✦  Scorciatoie da tastiera", [
            "<b>Ctrl + N</b> — Nuovo file &nbsp;&nbsp; <b>Ctrl + O</b> — Apri file &nbsp;&nbsp; <b>Ctrl + S</b> — Salva &nbsp;&nbsp; <b>Ctrl + Shift + S</b> — Salva con nome",
            "<b>Ctrl + F</b> — Cerca nel file &nbsp;&nbsp; <b>Ctrl + /</b> — Commenta / Decommenta riga &nbsp;&nbsp; <b>Ctrl + Z / Y</b> — Annulla / Ripeti",
            "<b>Ctrl + Q</b> — Esci &nbsp;&nbsp; <b>Ctrl + +/-</b> — Zoom &nbsp;&nbsp; <b>F5</b> — Compila & Esegui &nbsp;&nbsp; <b>Ctrl + B</b> — Solo compila",
            "<b>Ctrl + E</b> — Mostra/Nascondi explorer &nbsp;&nbsp; <b>Ctrl + J</b> — Mostra/Nascondi terminale",
        ])
        section("✦  Workflow C++", [
            "Scrivi il tuo <b>.cpp</b> con highlight completo (keyword, tipi STL, stringhe, commenti, preprocessore).",
            "Premi <b>F5</b>: EdiCpp compila con <code>g++ -std=c++17 -O2 -Wall</code> ed esegue nel terminale integrato.",
            "Se ci sono errori, li vedi direttamente nel terminale — clicca sul file nell'explorer per correggere.",
            "Il terminale è una vera <b>bash interattiva</b>: puoi lanciare <code>make</code>, <code>gdb</code>, <code>./a.out &lt; input.txt</code>, ecc.",
        ])
        section("✦  Terminale integrato (in basso)", [
            "È una shell completa, non un output finto: supporta input, <b>Ctrl+C</b> per interrompere, <b>Ctrl+L</b> per pulire.",
            "Fai <b>cd</b> nella cartella del progetto o usa il bottone <b>Apri cartella</b> per cambiare workspace.",
            "Comandi rapidi: <b>Esegui</b> lancia il binario compilato, <b>Pulisci</b> svuota il terminale.",
        ])
        section("✦  Tips estetici & produttività", [
            "Tema scuro <b>Tokyo Night</b> ottimizzato per lunghe sessioni — meno affaticamento, più focus.",
            "Indentazione automatica, chiusura parentesi, numeri di riga con riga corrente evidenziata.",
            "Explorer a sinistra: doppio click per aprire, tasto destro per rinominare/eliminare (via contest menu).",
            "Tutto è locale e leggero: zero Electron, solo Qt6 nativo — perfetto su Fedora.",
        ])
        section("✦  Requisiti", [
            "<b>g++</b> installato (<code>sudo dnf install gcc-c++</code>), <b>Python 3.10+</b> e <b>PyQt6</b>.",
        ])

        v.addStretch()
        scroll.setWidget(inner)
        layout.addWidget(scroll, 1)

        btn = QPushButton("Capito, iniziamo a codare →")
        btn.setObjectName("Accent")
        btn.clicked.connect(self.accept)
        layout.addWidget(btn, alignment=Qt.AlignmentFlag.AlignRight)

# ───────────────── Main Window ─────────────────

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("EdiCpp — Editor C++ leggero")
        self.resize(1280, 820)
        self.setMinimumSize(960, 600)
        self.current_folder = str(Path.home())
        self._setup_ui()
        self._apply_theme()
        self._connect_signals()
        self.statusBar().showMessage("Pronto • Premi F5 per compilare ed eseguire")
        self.new_file()

    def _apply_theme(self):
        self.setStyleSheet(STYLESHEET)

    def _setup_ui(self):
        # — Menu —
        menubar = self.menuBar()
        m_file = menubar.addMenu("File")
        m_edit = menubar.addMenu("Modifica")
        m_run  = menubar.addMenu("Esegui")
        m_view = menubar.addMenu("Vista")
        m_help = menubar.addMenu("Aiuto")

        def act(text, shortcut, slot, menu):
            a = QAction(text, self)
            if shortcut:
                a.setShortcut(QKeySequence(shortcut))
            a.triggered.connect(slot)
            menu.addAction(a)
            return a

        act("Nuovo file", "Ctrl+N", self.new_file, m_file)
        act("Apri file…", "Ctrl+O", self.open_file, m_file)
        act("Apri cartella…", "Ctrl+K", self.open_folder, m_file)
        m_file.addSeparator()
        act("Salva", "Ctrl+S", self.save_file, m_file)
        act("Salva con nome…", "Ctrl+Shift+S", self.save_file_as, m_file)
        m_file.addSeparator()
        act("Chiudi scheda", "Ctrl+W", self.close_current_tab, m_file)
        act("Esci", "Ctrl+Q", self.close, m_file)

        act("Annulla", "Ctrl+Z", lambda: self.current_editor() and self.current_editor().undo(), m_edit)
        act("Ripeti", "Ctrl+Y", lambda: self.current_editor() and self.current_editor().redo(), m_edit)
        m_edit.addSeparator()
        act("Cerca…", "Ctrl+F", self.show_search, m_edit)
        act("Commenta/Decommenta", "Ctrl+/", self.toggle_comment, m_edit)
        act("Aumenta zoom", "Ctrl+=", self.zoom_in, m_edit)
        act("Riduci zoom", "Ctrl+-", self.zoom_out, m_edit)

        act("Compila", "Ctrl+B", self.compile_only, m_run)
        act("Compila & Esegui", "F5", self.compile_run, m_run)

        self.act_toggle_explorer = QAction("Explorer", self)
        self.act_toggle_explorer.setShortcut("Ctrl+E")
        self.act_toggle_explorer.setCheckable(True)
        self.act_toggle_explorer.setChecked(True)
        self.act_toggle_explorer.triggered.connect(self.toggle_explorer)
        m_view.addAction(self.act_toggle_explorer)

        self.act_toggle_terminal = QAction("Terminale", self)
        self.act_toggle_terminal.setShortcut("Ctrl+J")
        self.act_toggle_terminal.setCheckable(True)
        self.act_toggle_terminal.setChecked(True)
        self.act_toggle_terminal.triggered.connect(self.toggle_terminal)
        m_view.addAction(self.act_toggle_terminal)

        act("Guida", "F1", self.show_guide, m_help)
        act("Informazioni", "", self.show_about, m_help)

        # — Toolbar —
        tb = QToolBar("Principale")
        tb.setMovable(False)
        tb.setIconSize(QSize(16, 16))
        self.addToolBar(tb)
        def tb_btn(text, slot, tooltip=""):
            a = QAction(text, self)
            a.triggered.connect(slot)
            if tooltip:
                a.setToolTip(tooltip)
            tb.addAction(a)
            return a
        tb_btn("＋ Nuovo", self.new_file, "Nuovo file (Ctrl+N)")
        tb_btn("📂 Apri", self.open_file, "Apri file")
        tb_btn("📁 Cartella", self.open_folder, "Apri cartella")
        tb.addSeparator()
        tb_btn("💾 Salva", self.save_file, "Salva")
        tb.addSeparator()
        tb_btn("🔨 Compila", self.compile_only, "Compila (Ctrl+B)")
        tb_btn("▶  Esegui", self.compile_run, "Compila & Esegui (F5)")
        tb.addSeparator()
        tb_btn("🔍 Guida", self.show_guide, "Guida (F1)")

        # — Central —
        central = QWidget()
        self.setCentralWidget(central)
        root_layout = QVBoxLayout(central)
        root_layout.setContentsMargins(10, 10, 10, 10)
        root_layout.setSpacing(8)

        # top splitter: explorer + editor area
        self.main_splitter = QSplitter(Qt.Orientation.Horizontal)

        # Explorer
        self.explorer_wrap = QWidget()
        self.explorer_wrap.setMinimumWidth(200)
        self.explorer_wrap.setMaximumWidth(420)
        exp_layout = QVBoxLayout(self.explorer_wrap)
        exp_layout.setContentsMargins(0, 0, 0, 0)
        exp_layout.setSpacing(0)
        exp_header = QWidget()
        exp_header.setStyleSheet("background:#0f1423; border-bottom:1px solid #1e2030;")
        eh = QHBoxLayout(exp_header)
        eh.setContentsMargins(12, 8, 8, 8)
        eh.addWidget(QLabel("▦  EXPLORER"))
        eh.itemAt(0).widget().setStyleSheet("color:#565f89; font-size:11px; font-weight:bold; letter-spacing:1px;")
        eh.addStretch()
        self.btn_open_folder = QPushButton("Apri")
        self.btn_open_folder.setFixedHeight(26)
        self.btn_open_folder.clicked.connect(self.open_folder)
        eh.addWidget(self.btn_open_folder)
        exp_layout.addWidget(exp_header)

        self.tree = QTreeView()
        self.model = None
        self._set_folder_model(self.current_folder)
        self.tree.setHeaderHidden(False)
        self.tree.setAnimated(True)
        self.tree.setIndentation(14)
        exp_layout.addWidget(self.tree, 1)

        self.main_splitter.addWidget(self.explorer_wrap)

        # Right side: search + tabs + terminal
        right = QWidget()
        right_layout = QVBoxLayout(right)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(6)

        self.search_bar = SearchBar(self.current_editor)
        right_layout.addWidget(self.search_bar)

        self.tabs = QTabWidget()
        self.tabs.setTabsClosable(True)
        self.tabs.setMovable(True)
        self.tabs.setDocumentMode(True)
        right_layout.addWidget(self.tabs, 3)

        # Terminal area (bottom)
        self.terminal = EmbeddedTerminal(workdir=self.current_folder)
        # wrap terminal with splitter for resizable height
        self.vertical_splitter = QSplitter(Qt.Orientation.Vertical)
        # We need to put tabs and terminal inside vertical splitter
        # Rebuild right_layout to use splitter
        # Clear right_layout
        while right_layout.count():
            item = right_layout.takeAt(0)
            w = item.widget()
            if w:
                w.setParent(None)
        # create container for tabs
        tabs_container = QWidget()
        tc_l = QVBoxLayout(tabs_container)
        tc_l.setContentsMargins(0, 0, 0, 0)
        tc_l.setSpacing(6)
        tc_l.addWidget(self.search_bar)
        tc_l.addWidget(self.tabs, 1)
        self.vertical_splitter.addWidget(tabs_container)
        self.vertical_splitter.addWidget(self.terminal)
        self.vertical_splitter.setSizes([520, 260])
        # style handle
        right_layout.addWidget(self.vertical_splitter, 1)

        self.main_splitter.addWidget(right)
        self.main_splitter.setSizes([260, 900])
        self.main_splitter.setStretchFactor(0, 0)
        self.main_splitter.setStretchFactor(1, 1)

        root_layout.addWidget(self.main_splitter, 1)

        # Status bar
        sb = QStatusBar()
        self.setStatusBar(sb)
        self.lbl_cursor = QLabel("Ln 1, Col 1")
        self.lbl_lang = QLabel("C++")
        self.lbl_lang.setStyleSheet("background:#1a1e32; border:1px solid #2a2e44; border-radius:6px; padding:2px 8px; color:#7aa2f7;")
        self.lbl_encoding = QLabel("UTF-8")
        sb.addPermanentWidget(self.lbl_cursor)
        sb.addPermanentWidget(self.lbl_encoding)
        sb.addPermanentWidget(self.lbl_lang)

    def _set_folder_model(self, path):
        from PyQt6.QtGui import QFileSystemModel
        self.current_folder = path
        self.model = QFileSystemModel()
        self.model.setRootPath(path)
        # filter to show relevant files but not too restrictive
        self.tree.setModel(self.model)
        self.tree.setRootIndex(self.model.index(path))
        for i in range(1, self.model.columnCount()):
            self.tree.hideColumn(i)
        self.tree.setColumnWidth(0, 220)
        if hasattr(self, 'terminal'):
            self.terminal.set_workdir(path)

    def _connect_signals(self):
        self.tree.doubleClicked.connect(self.on_tree_double_click)
        self.tabs.tabCloseRequested.connect(self.close_tab)
        self.tabs.currentChanged.connect(self.on_tab_changed)
        self.btn_open_folder.clicked.connect(self.open_folder)

    # — Helpers —
    def current_editor(self):
        w = self.tabs.currentWidget()
        return w if isinstance(w, CodeEditor) else None

    def on_tab_changed(self, idx):
        ed = self.current_editor()
        if ed:
            ed.cursorPositionChanged.connect(self.update_cursor_label)
            self.update_cursor_label()
            # update window title
            name = ed.file_path if ed.file_path else "Senza titolo"
            self.setWindowTitle(f"{Path(name).name} — EdiCpp")
        else:
            self.lbl_cursor.setText("Ln 1, Col 1")

    def update_cursor_label(self):
        ed = self.current_editor()
        if not ed:
            return
        cur = ed.textCursor()
        line = cur.blockNumber() + 1
        col = cur.columnNumber() + 1
        self.lbl_cursor.setText(f"Ln {line}, Col {col}")

    def on_tree_double_click(self, index):
        path = self.model.filePath(index)
        if os.path.isfile(path):
            self.open_file_path(path)

    # — File ops —
    def new_file(self):
        ed = CodeEditor()
        idx = self.tabs.addTab(ed, "Senza titolo •")
        self.tabs.setCurrentIndex(idx)
        ed.textChanged.connect(lambda: self.mark_dirty(ed))
        ed.cursorPositionChanged.connect(self.update_cursor_label)
        ed.setFocus()

    def mark_dirty(self, editor):
        idx = self.tabs.indexOf(editor)
        if idx == -1:
            return
        name = Path(editor.file_path).name if editor.file_path else "Senza titolo"
        # if document modified, add •
        is_mod = editor.document().isModified()
        title = f"{name}{' •' if is_mod else ''}"
        self.tabs.setTabText(idx, title)

    def open_file(self):
        path, _ = QFileDialog.getOpenFileName(self, "Apri file", self.current_folder, "C++ Files (*.cpp *.cc *.cxx *.h *.hpp);;All Files (*)")
        if path:
            self.open_file_path(path)

    def open_file_path(self, path):
        # check if already open
        for i in range(self.tabs.count()):
            w = self.tabs.widget(i)
            if isinstance(w, CodeEditor) and w.file_path == path:
                self.tabs.setCurrentIndex(i)
                return
        try:
            text = Path(path).read_text(encoding="utf-8", errors="replace")
        except Exception as e:
            QMessageBox.warning(self, "Errore", f"Impossibile aprire il file:\n{e}")
            return
        ed = CodeEditor(file_path=path)
        ed.setPlainText(text)
        ed.document().setModified(False)
        idx = self.tabs.addTab(ed, Path(path).name)
        self.tabs.setCurrentIndex(idx)
        ed.textChanged.connect(lambda: self.mark_dirty(ed))
        ed.cursorPositionChanged.connect(self.update_cursor_label)
        self.statusBar().showMessage(f"Aperto: {path}", 3000)

    def open_folder(self):
        path = QFileDialog.getExistingDirectory(self, "Apri cartella", self.current_folder)
        if path:
            self._set_folder_model(path)
            self.statusBar().showMessage(f"Workspace: {path}", 3000)

    def save_file(self):
        ed = self.current_editor()
        if not ed:
            return
        if not ed.file_path:
            return self.save_file_as()
        try:
            Path(ed.file_path).write_text(ed.toPlainText(), encoding="utf-8")
            ed.document().setModified(False)
            self.mark_dirty(ed)
            self.statusBar().showMessage(f"Salvato: {ed.file_path}", 2000)
            # update tab title without dot
            idx = self.tabs.indexOf(ed)
            self.tabs.setTabText(idx, Path(ed.file_path).name)
        except Exception as e:
            QMessageBox.warning(self, "Errore", f"Impossibile salvare:\n{e}")

    def save_file_as(self):
        ed = self.current_editor()
        if not ed:
            return
        start = self.current_folder + "/main.cpp" if not ed.file_path else ed.file_path
        path, _ = QFileDialog.getSaveFileName(self, "Salva con nome", start, "C++ Files (*.cpp *.h);;All Files (*)")
        if not path:
            return
        ed.file_path = path
        self.save_file()

    def close_tab(self, idx):
        w = self.tabs.widget(idx)
        if isinstance(w, CodeEditor) and w.document().isModified():
            resp = QMessageBox.question(self, "Salvare?", f"Salvare le modifiche a {w.file_path or 'Senza titolo'}?",
                                        QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No | QMessageBox.StandardButton.Cancel)
            if resp == QMessageBox.StandardButton.Cancel:
                return
            if resp == QMessageBox.StandardButton.Yes:
                self.tabs.setCurrentIndex(idx)
                self.save_file()
                if w.document().isModified():
                    return
        self.tabs.removeTab(idx)
        if self.tabs.count() == 0:
            self.new_file()

    def close_current_tab(self):
        self.close_tab(self.tabs.currentIndex())

    # — Edit —
    def show_search(self):
        self.search_bar.show_bar()

    def toggle_comment(self):
        ed = self.current_editor()
        if ed:
            ed.toggle_comment()

    def zoom_in(self):
        ed = self.current_editor()
        if ed:
            f = ed.font()
            f.setPointSize(min(28, f.pointSize() + 1))
            ed.setFont(f)
            ed.setTabStopDistance(QFontMetricsF(f).horizontalAdvance(' ') * 4)

    def zoom_out(self):
        ed = self.current_editor()
        if ed:
            f = ed.font()
            f.setPointSize(max(7, f.pointSize() - 1))
            ed.setFont(f)
            ed.setTabStopDistance(QFontMetricsF(f).horizontalAdvance(' ') * 4)

    def toggle_explorer(self):
        visible = self.act_toggle_explorer.isChecked()
        self.explorer_wrap.setVisible(visible)

    def toggle_terminal(self):
        visible = self.act_toggle_terminal.isChecked()
        self.terminal.setVisible(visible)

    # — Build & Run —
    def _ensure_saved(self):
        ed = self.current_editor()
        if not ed:
            QMessageBox.information(self, "Niente da compilare", "Apri o crea un file C++ prima.")
            return None
        if not ed.file_path:
            # ask save
            path, _ = QFileDialog.getSaveFileName(self, "Salva prima di compilare", self.current_folder + "/main.cpp", "C++ Files (*.cpp);;All Files (*)")
            if not path:
                return None
            ed.file_path = path
            idx = self.tabs.currentIndex()
            self.tabs.setTabText(idx, Path(path).name)
        # save
        try:
            Path(ed.file_path).write_text(ed.toPlainText(), encoding="utf-8")
            ed.document().setModified(False)
            self.mark_dirty(ed)
        except Exception as e:
            QMessageBox.warning(self, "Errore", f"Impossibile salvare:\n{e}")
            return None
        return ed.file_path

    def compile_only(self):
        src = self._ensure_saved()
        if not src:
            return
        out = str(Path(src).with_suffix(""))  # no .out, cleaner
        # fallback to /tmp if no write perms
        cmd = f'g++ -std=c++17 -O2 -Wall -Wextra -o "{out}" "{src}" && echo "✔ Compilazione riuscita → {out}"'
        self.terminal.setVisible(True)
        self.act_toggle_terminal.setChecked(True)
        self.vertical_splitter.setSizes([400, 300])
        self.terminal.run_command(cmd)

    def compile_run(self):
        src = self._ensure_saved()
        if not src:
            return
        out = str(Path(src).with_suffix(""))
        # compile and run, capturing input
        cmd = f'g++ -std=c++17 -O2 -Wall -Wextra -o "{out}" "{src}" && echo "✔ Compilato. Esecuzione..." && "{out}"'
        self.terminal.setVisible(True)
        self.act_toggle_terminal.setChecked(True)
        self.vertical_splitter.setSizes([380, 340])
        self.terminal.run_command(cmd)

    # — Dialogs —
    def show_guide(self):
        dlg = GuideDialog(self)
        dlg.exec()

    def show_about(self):
        QMessageBox.about(self, "EdiCpp",
            "<h3>EdiCpp</h3>"
            "<p>Editor C++ leggero, nativo per Linux (Fedora).</p>"
            "<p>Highlight C++, scorciatoie, terminale integrato, tema curato.</p>"
            "<p><b>Stack:</b> Python + PyQt6 (nativo Qt6, no Electron)</p>"
            "<p><small>Creato per francescoeramo • <a href='https://github.com/francescoeramo/edicpp'>github.com/francescoeramo/edicpp</a></small></p>"
        )

    def closeEvent(self, event):
        # check unsaved
        for i in range(self.tabs.count()):
            w = self.tabs.widget(i)
            if isinstance(w, CodeEditor) and w.document().isModified():
                resp = QMessageBox.question(self, "Uscire?", "Ci sono file non salvati. Uscire comunque?",
                                            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
                if resp != QMessageBox.StandardButton.Yes:
                    event.ignore()
                    return
                break
        # cleanup terminal
        try:
            self.terminal.timer.stop()
        except:
            pass
        event.accept()


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("EdiCpp")
    app.setOrganizationName("francescoeramo")
    # try to set icon if exists
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
