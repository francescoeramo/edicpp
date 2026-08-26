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
    QSizePolicy
)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import (
    QAction, QFont, QColor, QPainter, QTextFormat, QTextCursor, QKeySequence, QFontDatabase,
    QTextDocument
)
from PyQt6.QtGui import QFontMetricsF
from PyQt6.QtWidgets import QTextEdit

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
        font = QFont("IBM Plex Mono")
        if not font.exactMatch():
            font = QFont("JetBrains Mono")
            if not font.exactMatch():
                font = QFont("Courier New")
                if not font.exactMatch():
                    font = QFontDatabase.systemFont(QFontDatabase.SystemFont.FixedFont)
        font.setPointSize(11)
        font.setStyleHint(QFont.StyleHint.Monospace)
        self.setFont(font)
        self.setLineWrapMode(QPlainTextEdit.LineWrapMode.NoWrap)
        self.setTabStopDistance(QFontMetricsF(font).horizontalAdvance(' ') * 4)
        self.highlighter = CppHighlighter(self.document())
        # retro amber editor
        self.setStyleSheet("""
            QPlainTextEdit {
                background:#0a0804;
                color:#ffb000;
                border:none;
                selection-background-color:#ffb000;
                selection-color:#0d0a05;
                padding-left:4px;
            }
        """)
        self.blockCountChanged.connect(self.updateLineNumberAreaWidth)
        self.updateRequest.connect(self.updateLineNumberArea)
        self.cursorPositionChanged.connect(self.highlightCurrentLine)
        self.updateLineNumberAreaWidth(0)
        self.highlightCurrentLine()
        self.setPlaceholderText("// VT220 READY_  — inizia a scrivere C++...")

    def lineNumberAreaWidth(self):
        digits = len(str(max(1, self.blockCount())))
        space = 10 + self._fm().horizontalAdvance('9') * digits + 10
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
        painter.fillRect(event.rect(), QColor("#1a1207"))
        # right border
        painter.setPen(QColor("#3d2810"))
        painter.drawLine(self._line_number_area.width()-1, event.rect().top(), self._line_number_area.width()-1, event.rect().bottom())
        block = self.firstVisibleBlock()
        block_number = block.blockNumber()
        top = self.blockBoundingGeometry(block).translated(self.contentOffset()).top()
        bottom = top + self.blockBoundingRect(block).height()
        while block.isValid() and top <= event.rect().bottom():
            if block.isVisible() and bottom >= event.rect().top():
                number = str(block_number + 1)
                is_current = (block_number == self.textCursor().blockNumber())
                painter.setPen(QColor("#ffb000") if is_current else QColor("#8a7a5a"))
                f = painter.font()
                f.setBold(is_current)
                f.setPointSize(10)
                painter.setFont(f)
                painter.drawText(0, int(top), self._line_number_area.width() - 12, self._fm().height(),
                                 Qt.AlignmentFlag.AlignRight, number)
            block = block.next()
            top = bottom
            bottom = top + self.blockBoundingRect(block).height()
            block_number += 1

    def highlightCurrentLine(self):
        extra = []
        if not self.isReadOnly():
            sel = QTextEdit.ExtraSelection()
            sel.format.setBackground(QColor("#1f1608"))
            sel.format.setProperty(QTextFormat.Property.FullWidthSelection, True)
            sel.cursor = self.textCursor()
            sel.cursor.clearSelection()
            extra.append(sel)
        self.setExtraSelections(extra)

    def keyPressEvent(self, event):
        if event.key() in (Qt.Key.Key_Return, Qt.Key.Key_Enter):
            cursor = self.textCursor()
            block_text = cursor.block().text()
            indent = re.match(r"^\s*", block_text).group(0)
            if block_text.rstrip().endswith("{"):
                indent += "    "
            super().keyPressEvent(event)
            self.insertPlainText(indent)
            return
        pairs = {"(": ")", "[": "]", "{": "}", '"': '"', "'": "'"}
        if event.text() in pairs:
            cursor = self.textCursor()
            nxt = cursor.block().text()[cursor.positionInBlock():cursor.positionInBlock()+1] if cursor.positionInBlock() < len(cursor.block().text()) else ""
            if nxt == pairs[event.text()] and event.text() in ('"', "'", ")", "]", "}"):
                cursor.movePosition(QTextCursor.MoveOperation.Right)
                self.setTextCursor(cursor)
                return
            super().keyPressEvent(event)
            if event.text() in "([{":
                cur = self.textCursor()
                pos = cur.position()
                cur.insertText(pairs[event.text()])
                cur.setPosition(pos)
                self.setTextCursor(cur)
            return
        if event.key() == Qt.Key.Key_Tab:
            self.insertPlainText("    ")
            return
        if event.key() == Qt.Key.Key_Backtab:
            cursor = self.textCursor()
            cursor.movePosition(QTextCursor.MoveOperation.StartOfLine)
            cursor.movePosition(QTextCursor.MoveOperation.Right, QTextCursor.MoveMode.KeepAnchor, 4)
            if cursor.selectedText() == "    ":
                cursor.removeSelectedText()
            return
        super().keyPressEvent(event)

    # ── line move ──
    def move_line(self, direction: int):
        """Move current line up (-1) or down (+1). Preserves cursor column."""
        cursor = self.textCursor()
        block = cursor.block()
        target = block.previous() if direction == -1 else block.next()
        if not target.isValid():
            return
        col = cursor.positionInBlock()
        cur_text = block.text()
        tgt_text = target.text()

        # Use document block numbers to swap
        doc = self.document()
        cur_bn = block.blockNumber()
        tgt_bn = target.blockNumber()

        # Ensure we edit in correct order to keep positions valid
        cursor.beginEditBlock()
        # Replace texts
        # First replace the block that is later in document
        first_bn = max(cur_bn, tgt_bn)
        second_bn = min(cur_bn, tgt_bn)
        # Determine which text goes where
        # If moving up: prev gets cur_text, cur gets tgt_text
        # If moving down: cur gets tgt_text, next gets cur_text
        for bn, new_text in [(cur_bn, tgt_text), (tgt_bn, cur_text)]:
            b = doc.findBlockByNumber(bn)
            c = QTextCursor(b)
            # select whole line without newline
            c.movePosition(QTextCursor.MoveOperation.StartOfLine)
            c.movePosition(QTextCursor.MoveOperation.EndOfLine, QTextCursor.MoveMode.KeepAnchor)
            c.insertText(new_text)
        cursor.endEditBlock()

        # Restore cursor on moved line
        new_bn = tgt_bn
        new_block = doc.findBlockByNumber(new_bn)
        new_cursor = QTextCursor(new_block)
        pos = min(col, len(new_block.text()))
        new_cursor.setPosition(new_block.position() + pos)
        self.setTextCursor(new_cursor)

    def toggle_comment(self):
        cursor = self.textCursor()
        start = cursor.selectionStart()
        end = cursor.selectionEnd()
        cursor.setPosition(start)
        start_block = cursor.blockNumber()
        cursor.setPosition(end)
        end_block = cursor.blockNumber()
        if start == end:
            end_block = start_block
        cursor.beginEditBlock()
        for i in range(start_block, end_block + 1):
            block = self.document().findBlockByNumber(i)
            text = block.text()
            pos = block.position()
            cur = QTextCursor(block)
            stripped = text.lstrip()
            indent_len = len(text) - len(stripped)
            if stripped.startswith("//"):
                cur.setPosition(pos + indent_len)
                cur.setPosition(pos + indent_len + 2, QTextCursor.MoveMode.KeepAnchor)
                cur.removeSelectedText()
            else:
                cur.setPosition(pos + indent_len)
                cur.insertText("//")
        cursor.endEditBlock()

    def _fm(self):
        return super().fontMetrics()


# ───────────────── Search Bar ─────────────────

class SearchBar(QWidget):
    def __init__(self, editor_getter, parent=None):
        super().__init__(parent)
        self.editor_getter = editor_getter
        self.setFixedHeight(44)
        self.setStyleSheet("background:#f4e8c1; border:2px solid #1a1207; border-bottom:none;")
        layout = QHBoxLayout(self)
        layout.setContentsMargins(8, 6, 8, 6)
        layout.setSpacing(6)
        lbl = QLabel(" CERCA ▶")
        lbl.setStyleSheet("color:#1a1207; font-size:10px; font-weight:bold; letter-spacing:0.5px; border:none;")
        layout.addWidget(lbl)
        self.input = QLineEdit()
        self.input.setPlaceholderText("cerca nel file…")
        self.input.setFixedHeight(28)
        layout.addWidget(self.input, 1)
        self.prev_btn = QPushButton("▲")
        self.next_btn = QPushButton("▼")
        self.close_btn = QPushButton("✕")
        for b in (self.prev_btn, self.next_btn, self.close_btn):
            b.setFixedSize(30, 28)
        layout.addWidget(self.prev_btn)
        layout.addWidget(self.next_btn)
        layout.addWidget(self.close_btn)
        self.hide()
        self.input.returnPressed.connect(lambda: self.find_next())
        self.prev_btn.clicked.connect(lambda: self.find_prev())
        self.next_btn.clicked.connect(lambda: self.find_next())
        self.close_btn.clicked.connect(self.hide_bar)

    def show_bar(self):
        self.show()
        self.input.setFocus()
        self.input.selectAll()

    def hide_bar(self):
        self.hide()
        ed = self.editor_getter()
        if ed:
            ed.setFocus()

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


# ───────────────── Guide Dialog ─────────────────

class GuideDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Guida — EdiCpp RETRO")
        self.setModal(True)
        self.setMinimumSize(740, 640)
        self.setStyleSheet(STYLESHEET + "QDialog{background:#14100a; border:3px solid #1a1207;}")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(12)

        title = QLabel("▓ EDICPP — GUIDA RAPIDA [RETRO]")
        title.setObjectName("Title")
        subtitle = QLabel("VT220 EDITION  •  Amber phosphor  •  Fedora nativo  •  C++17")
        subtitle.setObjectName("Subtitle")
        layout.addWidget(title)
        layout.addWidget(subtitle)

        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.HLine)
        sep.setStyleSheet("color:#3d2810;")
        layout.addWidget(sep)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea{border:none; background:transparent;} QWidget{background:transparent;}")
        inner = QWidget()
        v = QVBoxLayout(inner)
        v.setSpacing(12)

        def section(heading, items):
            h = QLabel(heading)
            h.setObjectName("Heading")
            v.addWidget(h)
            for it in items:
                row = QHBoxLayout()
                dot = QLabel("▶")
                dot.setStyleSheet("color:#ffb000; font-weight:bold; font-size:10px;")
                dot.setFixedWidth(18)
                lbl = QLabel(it)
                lbl.setWordWrap(True)
                lbl.setStyleSheet("color:#e8dcc0; font-size:12px;")
                lbl.setTextFormat(Qt.TextFormat.RichText)
                row.addWidget(dot, alignment=Qt.AlignmentFlag.AlignTop)
                row.addWidget(lbl, 1)
                v.addLayout(row)
            v.addSpacing(4)

        section("■  SCORCIATOIE", [
            "<b>Ctrl + N</b> — Nuovo &nbsp; <b>Ctrl + O</b> — Apri &nbsp; <b>Ctrl + S</b> — Salva &nbsp; <b>Ctrl + Shift + S</b> — Salva con nome",
            "<b>Ctrl + F</b> — Cerca &nbsp; <b>Ctrl + /</b> — Commenta &nbsp; <b>Ctrl + Z / Y</b> — Annulla/Ripeti",
            "<b>Alt + ↑ / ↓</b> — Sposta riga sopra/sotto  <i>(nuovo!)</i> &nbsp; <b>Shift + Alt + ↑/↓</b> — identico",
            "<b>Ctrl + Q</b> — Esci &nbsp; <b>Ctrl + +/-</b> — Zoom &nbsp; <b>F5</b> — Compila &amp; Esegui &nbsp; <b>Ctrl + B</b> — Compila",
            "<b>Ctrl + E</b> — Explorer &nbsp; <b>Ctrl + J</b> — Terminale",
        ])
        section("■  WORKFLOW C++", [
            "Highlight amber: keyword <b style='color:#ff7a00'>arancio</b>, tipi <b style='color:#ffd23f'>giallo</b>, stringhe <b style='color:#7ec869'>verde phosphor</b>.",
            "Premi <b>F5</b>: compila con <code>g++ -std=c++17 -O2 -Wall -Wextra</code> ed esegue nel terminale retrò.",
            "Errori nel terminale amber — doppio click sull'explorer per correggere.",
        ])
        section("■  TERMINALE (IN BASSO)", [
            "Bash vera via <b>pty</b>: supporta input, <b>Ctrl+C</b>, <b>Ctrl+L</b>, <code>make</code>, <code>gdb</code>, <code>./a.out &lt; input.txt</code>.",
            "Pulsante <b>[ PULISCI ]</b> per svuotare. Prompt <b>▶</b> amber.",
        ])
        section("■  RETRO TIPS", [
            "Tema <b>Amber CRT</b> con chassis beige, bordi 2px solidi, niente slop arrotondato.",
            "Line numbers su pannello #1a1207, riga corrente #1f1608 con glow amber.",
            "Sposta righe con <b>Alt+↑/↓</b> — utile per riordinare include/flow senza taglia/incolla.",
            "Tutto nativo Qt6 — leggero su Fedora, zero webview.",
        ])
        section("■  REQUISITI", [
            "<b>g++</b> (<code>sudo dnf install gcc-c++</code>), <b>Python 3.10+</b>, <b>PyQt6</b>.",
        ])

        v.addStretch()
        scroll.setWidget(inner)
        layout.addWidget(scroll, 1)

        btn = QPushButton(" [ ESEGUI ]  CAPITO, AVVIA CRT → ")
        btn.setObjectName("Accent")
        btn.clicked.connect(self.accept)
        layout.addWidget(btn, alignment=Qt.AlignmentFlag.AlignRight)


# ───────────────── Main Window ─────────────────

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("EdiCpp RETRO — VT220 // C++")
        self.resize(1280, 820)
        self.setMinimumSize(960, 600)
        self.current_folder = str(Path.home())
        self._setup_ui()
        self._apply_theme()
        self._connect_signals()
        self.statusBar().showMessage(" CRT READY_  •  Alt+↑/↓ sposta riga  •  F5 compila & esegui ")
        self.new_file()

    def _apply_theme(self):
        self.setStyleSheet(STYLESHEET)

    def _setup_ui(self):
        menubar = self.menuBar()
        m_file = menubar.addMenu(" FILE ")
        m_edit = menubar.addMenu(" EDIT ")
        m_run  = menubar.addMenu(" RUN ")
        m_view = menubar.addMenu(" VIEW ")
        m_help = menubar.addMenu(" HELP ")

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
        m_edit.addSeparator()
        act("Sposta riga su", "Alt+Up", self.move_line_up, m_edit)
        act("Sposta riga giù", "Alt+Down", self.move_line_down, m_edit)
        # duplicate for Shift+Alt
        a_up2 = QAction("Sposta riga su (alt)", self)
        a_up2.setShortcut(QKeySequence("Shift+Alt+Up"))
        a_up2.triggered.connect(self.move_line_up)
        m_edit.addAction(a_up2)
        a_down2 = QAction("Sposta riga giù (alt)", self)
        a_down2.setShortcut(QKeySequence("Shift+Alt+Down"))
        a_down2.triggered.connect(self.move_line_down)
        m_edit.addAction(a_down2)
        m_edit.addSeparator()
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

        # — Toolbar — fixed, no wrap, no overlap
        tb = QToolBar("MAIN")
        tb.setMovable(False)
        tb.setFloatable(False)
        tb.setAllowedAreas(Qt.ToolBarArea.TopToolBarArea)
        tb.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextOnly)
        tb.setIconSize(QSize(0, 0))
        self.addToolBar(Qt.ToolBarArea.TopToolBarArea, tb)
        def tb_btn(text, slot, tooltip=""):
            a = QAction(text, self)
            a.triggered.connect(slot)
            if tooltip:
                a.setToolTip(tooltip)
            tb.addAction(a)
            return a
        tb_btn(" [ NUOVO ] ", self.new_file, "Nuovo (Ctrl+N)")
        tb_btn(" [ APRI ] ", self.open_file, "Apri file")
        tb_btn(" [ CARTELLA ] ", self.open_folder, "Apri cartella")
        tb.addSeparator()
        tb_btn(" [ SALVA ] ", self.save_file, "Salva")
        tb.addSeparator()
        tb_btn(" [ COMPILA ] ", self.compile_only, "Compila (Ctrl+B)")
        tb_btn(" [ ▶ ESEGUI ] ", self.compile_run, "Compila & Esegui (F5)")
        tb.addSeparator()
        tb_btn(" [ GUIDA ] ", self.show_guide, "Guida (F1)")

        # — Central —
        central = QWidget()
        self.setCentralWidget(central)
        root_layout = QVBoxLayout(central)
        root_layout.setContentsMargins(6, 6, 6, 6)
        root_layout.setSpacing(0)

        self.main_splitter = QSplitter(Qt.Orientation.Horizontal)
        self.main_splitter.setHandleWidth(8)
        self.main_splitter.setChildrenCollapsible(False)

        # Explorer — retro header fixed height
        self.explorer_wrap = QWidget()
        self.explorer_wrap.setMinimumWidth(210)
        self.explorer_wrap.setMaximumWidth(420)
        exp_layout = QVBoxLayout(self.explorer_wrap)
        exp_layout.setContentsMargins(0, 0, 0, 0)
        exp_layout.setSpacing(0)
        exp_header = QWidget()
        exp_header.setFixedHeight(36)
        exp_header.setStyleSheet("background:#f4e8c1; border:2px solid #1a1207; border-bottom:3px solid #1a1207;")
        eh = QHBoxLayout(exp_header)
        eh.setContentsMargins(8, 4, 6, 4)
        eh.setSpacing(6)
        title = QLabel("▦ EXPLORER")
        title.setStyleSheet("color:#1a1207; font-size:10px; font-weight:bold; letter-spacing:1px; border:none;")
        eh.addWidget(title)
        eh.addStretch()
        self.btn_open_folder = QPushButton("[ APRI ]")
        self.btn_open_folder.setFixedHeight(24)
        self.btn_open_folder.setFixedWidth(72)
        eh.addWidget(self.btn_open_folder)
        exp_layout.addWidget(exp_header)

        self.tree = QTreeView()
        self.model = None
        self._set_folder_model(self.current_folder)
        self.tree.setHeaderHidden(False)
        self.tree.setAnimated(True)
        self.tree.setIndentation(14)
        self.tree.setExpandsOnDoubleClick(True)
        exp_layout.addWidget(self.tree, 1)

        self.main_splitter.addWidget(self.explorer_wrap)

        # Right side
        right = QWidget()
        right_layout = QVBoxLayout(right)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(0)

        self.search_bar = SearchBar(self.current_editor)
        # tabs + terminal inside vertical splitter
        self.vertical_splitter = QSplitter(Qt.Orientation.Vertical)
        self.vertical_splitter.setHandleWidth(8)
        self.vertical_splitter.setChildrenCollapsible(False)

        tabs_container = QWidget()
        tc_l = QVBoxLayout(tabs_container)
        tc_l.setContentsMargins(0, 0, 0, 0)
        tc_l.setSpacing(0)
        tc_l.addWidget(self.search_bar)
        self.tabs = QTabWidget()
        self.tabs.setTabsClosable(True)
        self.tabs.setMovable(True)
        self.tabs.setDocumentMode(True)
        self.tabs.setElideMode(Qt.TextElideMode.ElideRight)
        self.tabs.setUsesScrollButtons(True)
        tc_l.addWidget(self.tabs, 1)

        self.terminal = EmbeddedTerminal(workdir=self.current_folder)
        self.terminal.setMinimumHeight(120)

        self.vertical_splitter.addWidget(tabs_container)
        self.vertical_splitter.addWidget(self.terminal)
        self.vertical_splitter.setSizes([520, 220])
        self.vertical_splitter.setStretchFactor(0, 3)
        self.vertical_splitter.setStretchFactor(1, 1)

        right_layout.addWidget(self.vertical_splitter, 1)

        self.main_splitter.addWidget(right)
        self.main_splitter.setSizes([250, 900])
        self.main_splitter.setStretchFactor(0, 0)
        self.main_splitter.setStretchFactor(1, 1)

        root_layout.addWidget(self.main_splitter, 1)

        sb = QStatusBar()
        self.setStatusBar(sb)
        self.lbl_cursor = QLabel(" Ln 1, Col 1 ")
        self.lbl_lang = QLabel(" C++17 ")
        self.lbl_lang.setObjectName("Lang")
        self.lbl_encoding = QLabel(" UTF-8 ")
        self.lbl_move_hint = QLabel(" Alt+↑/↓ sposta riga ")
        self.lbl_move_hint.setStyleSheet("color:#8a7a5a; font-size:10px; border:1px solid #3d2810; padding:1px 6px;")
        sb.addWidget(self.lbl_move_hint)
        sb.addPermanentWidget(self.lbl_cursor)
        sb.addPermanentWidget(self.lbl_encoding)
        sb.addPermanentWidget(self.lbl_lang)

    def _set_folder_model(self, path):
        from PyQt6.QtGui import QFileSystemModel
        self.current_folder = path
        self.model = QFileSystemModel()
        self.model.setRootPath(path)
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

    def current_editor(self):
        w = self.tabs.currentWidget()
        return w if isinstance(w, CodeEditor) else None

    def on_tab_changed(self, idx):
        ed = self.current_editor()
        if ed:
            try:
                ed.cursorPositionChanged.disconnect(self.update_cursor_label)
            except:
                pass
            ed.cursorPositionChanged.connect(self.update_cursor_label)
            self.update_cursor_label()
            name = ed.file_path if ed.file_path else "Senza titolo"
            self.setWindowTitle(f"{Path(name).name} — EdiCpp RETRO [VT220]")
        else:
            self.lbl_cursor.setText(" Ln 1, Col 1 ")

    def update_cursor_label(self):
        ed = self.current_editor()
        if not ed:
            return
        cur = ed.textCursor()
        line = cur.blockNumber() + 1
        col = cur.columnNumber() + 1
        self.lbl_cursor.setText(f" Ln {line}, Col {col} ")

    def on_tree_double_click(self, index):
        path = self.model.filePath(index)
        if os.path.isfile(path):
            self.open_file_path(path)

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
        is_mod = editor.document().isModified()
        title = f"{name}{' •' if is_mod else ''}"
        self.tabs.setTabText(idx, title)

    def open_file(self):
        path, _ = QFileDialog.getOpenFileName(self, "Apri file", self.current_folder, "C++ Files (*.cpp *.cc *.cxx *.h *.hpp);;All Files (*)")
        if path:
            self.open_file_path(path)

    def open_file_path(self, path):
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

    def show_search(self):
        self.search_bar.show_bar()

    def toggle_comment(self):
        ed = self.current_editor()
        if ed:
            ed.toggle_comment()

    def move_line_up(self):
        ed = self.current_editor()
        if ed:
            ed.move_line(-1)

    def move_line_down(self):
        ed = self.current_editor()
        if ed:
            ed.move_line(1)

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

    def _ensure_saved(self):
        ed = self.current_editor()
        if not ed:
            QMessageBox.information(self, "Niente da compilare", "Apri o crea un file C++ prima.")
            return None
        if not ed.file_path:
            path, _ = QFileDialog.getSaveFileName(self, "Salva prima di compilare", self.current_folder + "/main.cpp", "C++ Files (*.cpp);;All Files (*)")
            if not path:
                return None
            ed.file_path = path
            idx = self.tabs.currentIndex()
            self.tabs.setTabText(idx, Path(path).name)
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
        out = str(Path(src).with_suffix(""))
        cmd = f'g++ -std=c++17 -O2 -Wall -Wextra -o "{out}" "{src}" && echo "■ COMPILATO → {out}"'
        self.terminal.setVisible(True)
        self.act_toggle_terminal.setChecked(True)
        self.vertical_splitter.setSizes([400, 300])
        self.terminal.run_command(cmd)

    def compile_run(self):
        src = self._ensure_saved()
        if not src:
            return
        out = str(Path(src).with_suffix(""))
        cmd = f'g++ -std=c++17 -O2 -Wall -Wextra -o "{out}" "{src}" && echo "■ COMPILATO. ESECUZIONE..." && "{out}"'
        self.terminal.setVisible(True)
        self.act_toggle_terminal.setChecked(True)
        self.vertical_splitter.setSizes([380, 340])
        self.terminal.run_command(cmd)

    def show_guide(self):
        dlg = GuideDialog(self)
        dlg.exec()

    def show_about(self):
        QMessageBox.about(self, "EdiCpp RETRO",
            "<h3>▓ EdiCpp RETRO — VT220</h3>"
            "<p>Editor C++ leggero, nativo Fedora.<br>Amber CRT, chassis beige, bordi solidi — zero slop.</p>"
            "<p><b>Novità:</b> Alt+↑/↓ sposta la riga.</p>"
            "<p><b>Stack:</b> Python + PyQt6</p>"
            "<p><small>github.com/francescoeramo/edicpp</small></p>"
        )

    def closeEvent(self, event):
        for i in range(self.tabs.count()):
            w = self.tabs.widget(i)
            if isinstance(w, CodeEditor) and w.document().isModified():
                resp = QMessageBox.question(self, "Uscire?", "Ci sono file non salvati. Uscire comunque?",
                                            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
                if resp != QMessageBox.StandardButton.Yes:
                    event.ignore()
                    return
                break
        try:
            self.terminal.timer.stop()
        except:
            pass
        event.accept()


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("EdiCpp RETRO")
    app.setOrganizationName("francescoeramo")
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
