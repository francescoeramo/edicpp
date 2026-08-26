"""
Retro theme — Amber CRT / Beige chassis.
Ispired by VT220, Commodore, IBM 5150: warm dark amber on deep brown,
beige panels, chunky 2px borders, no rounded slop, pixel-sharp.
"""
STYLESHEET = """
* {
    font-family: 'IBM Plex Mono', 'JetBrains Mono', 'Courier New', monospace;
}

/* ── Window ── */
QMainWindow {
    background: #0d0a05;
    color: #f4e8c1;
}
QWidget {
    color: #f4e8c1;
}

/* ── MenuBar — beige chassis ── */
QMenuBar {
    background: #f4e8c1;
    color: #1a1207;
    border-bottom: 3px solid #1a1207;
    padding: 2px 6px;
    font-size: 12px;
    font-weight: bold;
    letter-spacing: 0.5px;
}
QMenuBar::item {
    padding: 5px 12px;
    background: transparent;
    border: 1px solid transparent;
}
QMenuBar::item:selected {
    background: #1a1207;
    color: #ffb000;
    border: 1px solid #1a1207;
}
QMenu {
    background: #f4e8c1;
    color: #1a1207;
    border: 2px solid #1a1207;
    padding: 4px;
}
QMenu::item {
    padding: 6px 24px 6px 16px;
    border: 1px solid transparent;
}
QMenu::item:selected {
    background: #1a1207;
    color: #ffb000;
}
QMenu::separator {
    height: 2px;
    background: #c9b896;
    margin: 4px 8px;
}

/* ── Toolbar — beige with chunky separators ── */
QToolBar {
    background: #f4e8c1;
    border-bottom: 3px solid #1a1207;
    spacing: 0px;
    padding: 4px 6px;
}
QToolBar::separator {
    background: #8a7a5a;
    width: 2px;
    margin: 6px 6px;
}
QToolButton {
    background: #f4e8c1;
    color: #1a1207;
    border: 2px solid #1a1207;
    padding: 5px 14px;
    margin: 2px 3px;
    font-size: 11px;
    font-weight: bold;
    letter-spacing: 0.3px;
}
QToolButton:hover {
    background: #1a1207;
    color: #ffb000;
    border-color: #1a1207;
}
QToolButton:pressed {
    background: #2b1d0e;
    color: #ff7a00;
    border: 2px inset #3d2810;
    padding-top: 6px;
    padding-left: 15px;
}

/* ── Explorer ── */
QTreeView {
    background: #14100a;
    color: #e8dcc0;
    border: 2px solid #3d2810;
    border-top: none;
    outline: none;
    font-size: 12px;
    show-decoration-selected: 1;
}
QTreeView::item {
    padding: 4px 8px;
    border: 1px solid transparent;
    margin: 1px 2px;
}
QTreeView::item:hover {
    background: #2b1d0e;
    color: #ffb000;
    border-color: #ffb000;
}
QTreeView::item:selected {
    background: #ffb000;
    color: #0d0a05;
    border-color: #ff7a00;
}
QHeaderView::section {
    background: #1a1207;
    color: #ffb000;
    padding: 5px 8px;
    border: 1px solid #3d2810;
    border-bottom: 2px solid #3d2810;
    font-size: 10px;
    font-weight: bold;
    letter-spacing: 1px;
}

/* ── Tabs — retro block tabs ── */
QTabWidget::pane {
    border: 2px solid #3d2810;
    background: #0a0804;
    top: -2px;
}
QTabBar::tab {
    background: #2b1d0e;
    color: #8a7a5a;
    border: 2px solid #3d2810;
    border-bottom: none;
    padding: 7px 16px;
    margin-right: 2px;
    font-size: 11px;
    font-weight: bold;
    min-width: 90px;
}
QTabBar::tab:selected {
    background: #ffb000;
    color: #0d0a05;
    border-color: #ff7a00;
    border-bottom: 2px solid #ffb000;
    margin-bottom: -2px;
}
QTabBar::tab:hover:!selected {
    background: #3d2810;
    color: #ffb000;
    border-color: #ffb000;
}
QTabBar::close-button {
    image: none;
    background: transparent;
    subcontrol-position: right;
}
QTabBar::tab:selected .close-button {
    color: #0d0a05;
}
QTabWidget::tab-bar { alignment: left; }

/* ── Splitter handles — visible retro grip ── */
QSplitter::handle {
    background: #1a1207;
    border: 1px solid #3d2810;
}
QSplitter::handle:horizontal {
    width: 8px;
    image: none;
}
QSplitter::handle:vertical {
    height: 8px;
}
QSplitter::handle:hover {
    background: #ffb000;
}

/* ── Scrollbars — chunky retro ── */
QScrollBar:vertical {
    background: #1a1207;
    width: 14px;
    border-left: 2px solid #3d2810;
    margin: 0;
}
QScrollBar::handle:vertical {
    background: #3d2810;
    border: 2px solid #ffb000;
    min-height: 24px;
    margin: 1px;
}
QScrollBar::handle:vertical:hover { background: #ffb000; }
QScrollBar::add-line, QScrollBar::sub-line {
    background: #1a1207;
    border: 1px solid #3d2810;
    height: 14px;
    subcontrol-origin: margin;
}
QScrollBar:horizontal {
    background: #1a1207;
    height: 14px;
    border-top: 2px solid #3d2810;
}
QScrollBar::handle:horizontal {
    background: #3d2810;
    border: 2px solid #ffb000;
    min-width: 24px;
    margin: 1px;
}
QScrollBar::handle:horizontal:hover { background: #ffb000; }

/* ── StatusBar — beige footer ── */
QStatusBar {
    background: #f4e8c1;
    color: #1a1207;
    border-top: 3px solid #1a1207;
    font-size: 11px;
    font-weight: bold;
    padding: 2px;
}
QStatusBar QLabel {
    color: #1a1207;
    padding: 2px 10px;
    border: 1px solid transparent;
}
QStatusBar QLabel#Lang {
    background: #1a1207;
    color: #ffb000;
    border: 2px solid #1a1207;
    padding: 1px 10px;
}

/* ── Buttons — beveled retro ── */
QPushButton {
    background: #f4e8c1;
    color: #1a1207;
    border: 2px solid #1a1207;
    border-top-color: #fff8e0;
    border-left-color: #fff8e0;
    padding: 6px 16px;
    font-size: 11px;
    font-weight: bold;
    letter-spacing: 0.3px;
}
QPushButton:hover {
    background: #ffb000;
    color: #0d0a05;
    border-color: #1a1207;
    border-top-color: #1a1207;
    border-left-color: #1a1207;
}
QPushButton:pressed {
    border-top-color: #1a1207;
    border-left-color: #1a1207;
    border-bottom-color: #fff8e0;
    border-right-color: #fff8e0;
    padding-top: 7px;
    padding-left: 17px;
    background: #ff7a00;
}
QPushButton#Accent {
    background: #ffb000;
    color: #0d0a05;
    border: 2px solid #1a1207;
    border-top-color: #ffd23f;
    border-left-color: #ffd23f;
}
QPushButton#Accent:hover {
    background: #ffd23f;
}
QPushButton#Accent:pressed {
    background: #ff7a00;
}

/* ── Inputs ── */
QLineEdit {
    background: #0a0804;
    color: #ffb000;
    border: 2px solid #3d2810;
    border-top-color: #1a1207;
    border-left-color: #1a1207;
    padding: 6px 10px;
    selection-background-color: #ffb000;
    selection-color: #0d0a05;
}
QLineEdit:focus {
    border-color: #ffb000;
}

/* ── Editors ── */
QPlainTextEdit, QTextEdit {
    background: #0a0804;
    color: #ffb000;
    border: 2px solid #3d2810;
    selection-background-color: #ffb000;
    selection-color: #0d0a05;
}

/* ── Dialogs ── */
QDialog {
    background: #14100a;
    border: 3px solid #1a1207;
}
QLabel#Title {
    color: #ffb000;
    font-size: 18px;
    font-weight: bold;
    letter-spacing: 1px;
}
QLabel#Subtitle {
    color: #8a7a5a;
    font-size: 11px;
    letter-spacing: 0.5px;
}
QLabel#Heading {
    color: #ffb000;
    font-size: 11px;
    font-weight: bold;
    letter-spacing: 1px;
    border-bottom: 2px solid #3d2810;
    padding-bottom: 4px;
}
QFrame[frameShape="4"] { /* HLine */
    color: #3d2810;
}

/* ── ScrollArea transparent ── */
QScrollArea { border: none; background: transparent; }

"""
