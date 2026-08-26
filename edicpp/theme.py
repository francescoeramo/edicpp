"""
Win98 retro — Windows 98 / Display Properties.
Teal desktop #008080, finestra grigia #C0C0C0, title bar navy #000080,
bordi 3D rialzati/incassati, font MS Sans Serif 8pt, non grassetto.
Come nello screenshot anni '90.
"""
STYLESHEET = """
* {
    font-family: 'MS Sans Serif', 'Microsoft Sans Serif', Tahoma, sans-serif;
}

/* ── Desktop ── */
QMainWindow {
    background: #008080;
}
QWidget { color: #000000; }

/* ── Title-like central panel is handled in code, but fallback ── */
QMainWindow > QWidget {
    background: #c0c0c0;
}

/* ── MenuBar — grigio rialzato ── */
QMenuBar {
    background: #c0c0c0;
    color: #000000;
    border-top: 1px solid #ffffff;
    border-left: 1px solid #ffffff;
    border-bottom: 1px solid #808080;
    border-right: 1px solid #404040;
    padding: 2px;
    font-size: 11px;
    font-weight: 400;
}
QMenuBar::item {
    padding: 4px 8px;
    background: transparent;
    border: 1px solid transparent;
}
QMenuBar::item:selected {
    background: #000080;
    color: #ffffff;
}
QMenu {
    background: #c0c0c0;
    color: #000000;
    border-top: 1px solid #ffffff;
    border-left: 1px solid #ffffff;
    border-bottom: 1px solid #404040;
    border-right: 1px solid #404040;
    padding: 2px;
}
QMenu::item {
    padding: 4px 24px 4px 8px;
    font-size: 11px;
    font-weight: 400;
}
QMenu::item:selected {
    background: #000080;
    color: #ffffff;
}
QMenu::separator {
    height: 1px;
    background: #808080;
    border-bottom: 1px solid #ffffff;
    margin: 3px 4px;
}

/* ── ToolBar — barra grigia Win98 ── */
QToolBar {
    background: #c0c0c0;
    border-top: 1px solid #ffffff;
    border-left: 1px solid #ffffff;
    border-bottom: 1px solid #808080;
    border-right: 1px solid #808080;
    spacing: 2px;
    padding: 3px 4px;
}
QToolBar::separator {
    background: #808080;
    width: 1px;
    border-right: 1px solid #ffffff;
    margin: 4px 6px;
}
QToolButton {
    background: #c0c0c0;
    color: #000000;
    border-top: 1px solid #ffffff;
    border-left: 1px solid #ffffff;
    border-bottom: 1px solid #404040;
    border-right: 1px solid #404040;
    padding: 5px 12px;
    margin: 1px;
    font-size: 12px;
    font-weight: 400;
    letter-spacing: 0.2px;
}
QToolButton:hover {
    background: #c0c0c0;
    border-top: 1px solid #ffffff;
    border-left: 1px solid #ffffff;
    border-bottom: 1px solid #404040;
    border-right: 1px solid #404040;
}
QToolButton:pressed {
    border-top: 1px solid #404040;
    border-left: 1px solid #404040;
    border-bottom: 1px solid #ffffff;
    border-right: 1px solid #ffffff;
    background: #c0c0c0;
    padding-top: 5px;
    padding-left: 11px;
}

/* ── Tree / Explorer — bianco incassato ── */
QTreeView {
    background: #ffffff;
    color: #000000;
    border-top: 2px solid #404040;
    border-left: 2px solid #404040;
    border-bottom: 1px solid #ffffff;
    border-right: 1px solid #ffffff;
    /* inner white edge */
    outline: none;
    font-size: 11px;
    font-weight: 400;
    show-decoration-selected: 1;
}
QTreeView::item {
    padding: 2px 4px;
    border: 1px solid transparent;
}
QTreeView::item:hover {
    background: #c0c0c0;
}
QTreeView::item:selected {
    background: #000080;
    color: #ffffff;
}
QHeaderView::section {
    background: #c0c0c0;
    color: #000000;
    border-top: 1px solid #ffffff;
    border-left: 1px solid #ffffff;
    border-bottom: 1px solid #404040;
    border-right: 1px solid #404040;
    padding: 3px 6px;
    font-size: 11px;
    font-weight: 400;
}

/* ── Tabs — Win98 property sheet ── */
QTabWidget::pane {
    background: #c0c0c0;
    border-top: 1px solid #ffffff;
    border-left: 1px solid #ffffff;
    border-bottom: 1px solid #404040;
    border-right: 1px solid #404040;
    top: -1px;
    padding: 6px;
}
QTabBar::tab {
    background: #c0c0c0;
    color: #000000;
    border-top: 1px solid #ffffff;
    border-left: 1px solid #ffffff;
    border-bottom: 1px solid #c0c0c0;
    border-right: 1px solid #404040;
    padding: 4px 12px;
    margin-right: 2px;
    font-size: 11px;
    font-weight: 400;
    min-width: 70px;
}
QTabBar::tab:selected {
    background: #c0c0c0;
    border-bottom: 1px solid #c0c0c0;
    margin-bottom: -1px;
    padding-bottom: 5px;
}
QTabBar::tab:!selected {
    margin-top: 3px;
}
QTabBar::close-button {
    image: none;
    background: transparent;
}

/* ── Splitter — grigio ── */
QSplitter::handle {
    background: #c0c0c0;
}
QSplitter::handle:horizontal { width: 4px; }
QSplitter::handle:vertical { height: 4px; }

/* ── Scrollbars — Win98 grigio con frecce 3D ── */
QScrollBar:vertical {
    background: #c0c0c0;
    width: 16px;
    border-top: 1px solid #ffffff;
    border-left: 1px solid #ffffff;
    border-bottom: 1px solid #404040;
    border-right: 1px solid #404040;
    margin: 16px 0 16px 0;
}
QScrollBar::handle:vertical {
    background: #c0c0c0;
    border-top: 1px solid #ffffff;
    border-left: 1px solid #ffffff;
    border-bottom: 1px solid #404040;
    border-right: 1px solid #404040;
    min-height: 20px;
    margin: 0px;
}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    background: #c0c0c0;
    border-top: 1px solid #ffffff;
    border-left: 1px solid #ffffff;
    border-bottom: 1px solid #404040;
    border-right: 1px solid #404040;
    height: 16px;
}
QScrollBar:horizontal {
    background: #c0c0c0;
    height: 16px;
    border-top: 1px solid #ffffff;
    border-left: 1px solid #ffffff;
    border-bottom: 1px solid #404040;
    border-right: 1px solid #404040;
    margin: 0 16px 0 16px;
}
QScrollBar::handle:horizontal {
    background: #c0c0c0;
    border-top: 1px solid #ffffff;
    border-left: 1px solid #ffffff;
    border-bottom: 1px solid #404040;
    border-right: 1px solid #404040;
    min-width: 20px;
}
QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
    background: #c0c0c0;
    border-top: 1px solid #ffffff;
    border-left: 1px solid #ffffff;
    border-bottom: 1px solid #404040;
    border-right: 1px solid #404040;
    width: 16px;
}

/* ── StatusBar — footer Win98 con pannelli incassati, NO sovrapposizione ── */
QStatusBar {
    background: #c0c0c0;
    border-top: 1px solid #ffffff;
    font-size: 11px;
    font-weight: 400;
    padding: 2px 2px;
}
QStatusBar::item { border: none; }
QStatusBar QLabel {
    background: #c0c0c0;
    color: #000000;
    font-size: 11px;
    font-weight: 400;
    padding: 2px 6px;
    margin: 1px;
    border-top: 1px solid #808080;
    border-left: 1px solid #808080;
    border-bottom: 1px solid #ffffff;
    border-right: 1px solid #ffffff;
}
QStatusBar QLabel#Lang {
    background: #c0c0c0;
    color: #000000;
    border-top: 1px solid #808080;
    border-left: 1px solid #808080;
    border-bottom: 1px solid #ffffff;
    border-right: 1px solid #ffffff;
    padding: 2px 8px;
    font-weight: 400;
}
QStatusBar QLabel#Time {
    background: #c0c0c0;
    border-top: 1px solid #808080;
    border-left: 1px solid #808080;
    border-bottom: 1px solid #ffffff;
    border-right: 1px solid #ffffff;
}

/* ── Buttons — 3D Win98, più leggibili ── */
QPushButton {
    background: #c0c0c0;
    color: #000000;
    border-top: 1px solid #ffffff;
    border-left: 1px solid #ffffff;
    border-bottom: 1px solid #404040;
    border-right: 1px solid #404040;
    padding: 6px 16px;
    font-size: 12px;
    font-weight: 400;
    letter-spacing: 0.2px;
}
QPushButton:hover { background: #c0c0c0; }
QPushButton:pressed {
    border-top: 1px solid #404040;
    border-left: 1px solid #404040;
    border-bottom: 1px solid #ffffff;
    border-right: 1px solid #ffffff;
    padding-top: 6px;
    padding-left: 15px;
}
QPushButton#Accent {
    background: #c0c0c0;
    color: #000000;
    border-top: 2px solid #ffffff;
    border-left: 2px solid #ffffff;
    border-bottom: 2px solid #404040;
    border-right: 2px solid #404040;
    font-weight: 400;
}
QPushButton:disabled {
    color: #808080;
    border-top: 1px solid #ffffff;
    border-left: 1px solid #ffffff;
    border-bottom: 1px solid #808080;
    border-right: 1px solid #808080;
}

/* ── Inputs — incassati bianchi ── */
QLineEdit {
    background: #ffffff;
    color: #000000;
    border-top: 2px solid #404040;
    border-left: 2px solid #404040;
    border-bottom: 1px solid #ffffff;
    border-right: 1px solid #ffffff;
    padding: 3px 4px;
    font-size: 11px;
    font-weight: 400;
    selection-background-color: #000080;
    selection-color: #ffffff;
}
QPlainTextEdit, QTextEdit {
    background: #ffffff;
    color: #000000;
    border-top: 2px solid #404040;
    border-left: 2px solid #404040;
    border-bottom: 1px solid #ffffff;
    border-right: 1px solid #ffffff;
    selection-background-color: #000080;
    selection-color: #ffffff;
}

/* ── Dialogs — finestra grigia 3D ── */
QDialog {
    background: #c0c0c0;
    border-top: 1px solid #ffffff;
    border-left: 1px solid #ffffff;
    border-bottom: 1px solid #404040;
    border-right: 1px solid #404040;
}
QLabel#Title {
    background: #000080;
    color: #ffffff;
    font-size: 11px;
    font-weight: 700;
    padding: 3px 6px;
}
QLabel#Subtitle {
    color: #000000;
    font-size: 11px;
    font-weight: 400;
    background: transparent;
}
QLabel#Heading {
    color: #000000;
    font-size: 11px;
    font-weight: 700;
    border-bottom: 1px solid #808080;
    padding-bottom: 3px;
    background: transparent;
}
QFrame[frameShape="4"] { color: #808080; }
QScrollArea { border: none; background: #c0c0c0; }
QScrollArea QWidget { background: #c0c0c0; }
"""
