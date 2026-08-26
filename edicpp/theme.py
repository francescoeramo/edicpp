"""
Arcade retro — cabinato anni '80: nero profondo, neon cyan/magenta/yellow,
scanline soft, griglia, font pulito non grassetto. Leggibile, non slop.
"""
STYLESHEET = """
* {
    font-family: 'JetBrains Mono', 'IBM Plex Mono', 'Courier New', monospace;
}

/* ── Window ── */
QMainWindow {
    background: #06080f;
    color: #dbe2ff;
}
QWidget { color: #dbe2ff; }

/* ── MenuBar — nero + neon underline ── */
QMenuBar {
    background: #0a0c1e;
    color: #dbe2ff;
    border-bottom: 1px solid #1e2348;
    padding: 2px 8px;
    font-size: 12px;
    font-weight: 400;
    letter-spacing: 0.3px;
}
QMenuBar::item {
    padding: 6px 14px;
    background: transparent;
    border-radius: 6px;
}
QMenuBar::item:selected {
    background: #1a1f3d;
    color: #00e5ff;
}
QMenu {
    background: #0e1126;
    color: #dbe2ff;
    border: 1px solid #1e2348;
    border-radius: 10px;
    padding: 6px;
}
QMenu::item {
    padding: 7px 22px 7px 14px;
    border-radius: 6px;
    font-weight: 400;
}
QMenu::item:selected {
    background: #1a1f3d;
    color: #00e5ff;
}
QMenu::separator {
    height: 1px;
    background: #1e2348;
    margin: 6px 8px;
}

/* ── Toolbar — barra arcade sopra, pulita senza sovrapposizioni ── */
QToolBar {
    background: #0a0c1e;
    border-bottom: 1px solid #1e2348;
    spacing: 2px;
    padding: 6px 10px;
}
QToolBar::separator {
    background: #1e2348;
    width: 1px;
    margin: 8px 8px;
}
QToolButton {
    background: #12142d;
    color: #dbe2ff;
    border: 1px solid #1e2348;
    border-radius: 8px;
    padding: 6px 14px;
    margin: 2px 2px;
    font-size: 12px;
    font-weight: 450;
    letter-spacing: 0.2px;
}
QToolButton:hover {
    background: #1a1f3d;
    color: #00e5ff;
    border-color: #00e5ff;
}
QToolButton:pressed {
    background: #0e1126;
    color: #00e5ff;
    border-color: #00e5ff;
    padding-top: 7px;
}

/* ── Explorer ── */
QTreeView {
    background: #080a18;
    color: #dbe2ff;
    border: 1px solid #1e2348;
    border-top: none;
    outline: none;
    font-size: 12px;
    font-weight: 400;
    show-decoration-selected: 1;
}
QTreeView::item {
    padding: 5px 8px;
    border-radius: 6px;
    margin: 1px 4px;
    border: 1px solid transparent;
}
QTreeView::item:hover {
    background: #12142d;
    color: #00e5ff;
    border-color: #1e2348;
}
QTreeView::item:selected {
    background: #1a1f3d;
    color: #00e5ff;
    border-color: #00e5ff;
}
QHeaderView::section {
    background: #0a0c1e;
    color: #6b73a3;
    padding: 6px 8px;
    border: none;
    border-bottom: 1px solid #1e2348;
    font-size: 10px;
    font-weight: 500;
    letter-spacing: 0.8px;
}

/* ── Tabs — arcade neon ── */
QTabWidget::pane {
    border: 1px solid #1e2348;
    background: #06080f;
    border-radius: 10px;
    top: -1px;
}
QTabBar::tab {
    background: #0e1126;
    color: #6b73a3;
    border: 1px solid #1e2348;
    border-bottom: none;
    border-top-left-radius: 8px;
    border-top-right-radius: 8px;
    padding: 8px 16px;
    margin-right: 3px;
    font-size: 12px;
    font-weight: 400;
    min-width: 110px;
}
QTabBar::tab:selected {
    background: #12142d;
    color: #00e5ff;
    border-color: #00e5ff;
    border-bottom: 1px solid #12142d;
    margin-bottom: -1px;
}
QTabBar::tab:hover:!selected {
    background: #12142d;
    color: #dbe2ff;
    border-color: #2a3060;
}
QTabBar::close-button { image: none; background: transparent; }
QTabWidget::tab-bar { alignment: left; }

/* ── Splitter handles ── */
QSplitter::handle {
    background: #0a0c1e;
    border: none;
}
QSplitter::handle:horizontal { width: 6px; }
QSplitter::handle:vertical { height: 6px; }
QSplitter::handle:hover { background: #1a1f3d; }

/* ── Scrollbars — sottili neon ── */
QScrollBar:vertical {
    background: #080a18;
    width: 10px;
    margin: 0;
    border-left: 1px solid #0e1126;
}
QScrollBar::handle:vertical {
    background: #1e2348;
    border-radius: 5px;
    min-height: 28px;
    margin: 2px;
}
QScrollBar::handle:vertical:hover { background: #00e5ff; }
QScrollBar::add-line, QScrollBar::sub-line { height: 0; border: none; }
QScrollBar:horizontal {
    background: #080a18;
    height: 10px;
    border-top: 1px solid #0e1126;
}
QScrollBar::handle:horizontal {
    background: #1e2348;
    border-radius: 5px;
    min-width: 28px;
    margin: 2px;
}
QScrollBar::handle:horizontal:hover { background: #00e5ff; }

/* ── StatusBar — pulita, niente sovrapposizioni ── */
QStatusBar {
    background: #0a0c1e;
    border-top: 1px solid #1e2348;
    color: #6b73a3;
    font-size: 11px;
    font-weight: 400;
    padding: 2px 4px;
}
QStatusBar::item { border: none; }
QStatusBar QLabel {
    color: #6b73a3;
    padding: 3px 10px;
    font-weight: 400;
}
QStatusBar QLabel#Lang {
    background: #12142d;
    color: #00e5ff;
    border: 1px solid #1e2348;
    border-radius: 6px;
    padding: 2px 10px;
    font-weight: 500;
}

/* ── Buttons — arcade, leggibili, MAI grassetto esagerato ── */
QPushButton {
    background: #12142d;
    color: #dbe2ff;
    border: 1px solid #1e2348;
    border-radius: 8px;
    padding: 7px 16px;
    font-size: 12px;
    font-weight: 450;
    letter-spacing: 0.2px;
}
QPushButton:hover {
    background: #1a1f3d;
    color: #00e5ff;
    border-color: #00e5ff;
}
QPushButton:pressed {
    background: #0e1126;
    border-color: #00e5ff;
    padding-top: 8px;
}
QPushButton#Accent {
    background: #00e5ff;
    color: #06080f;
    border: 1px solid #00e5ff;
    font-weight: 500;
    padding: 8px 18px;
}
QPushButton#Accent:hover {
    background: #4df0ff;
    border-color: #4df0ff;
}
QPushButton#Accent:pressed {
    background: #00c8e0;
}

/* ── Inputs ── */
QLineEdit {
    background: #080a18;
    color: #dbe2ff;
    border: 1px solid #1e2348;
    border-radius: 8px;
    padding: 7px 12px;
    font-weight: 400;
    selection-background-color: #00e5ff;
    selection-color: #06080f;
}
QLineEdit:focus { border-color: #00e5ff; }

/* ── Editors ── */
QPlainTextEdit, QTextEdit {
    background: #06080f;
    color: #dbe2ff;
    border: 1px solid #1e2348;
    border-radius: 10px;
    selection-background-color: #1a1f3d;
    selection-color: #00e5ff;
}

/* ── Dialogs ── */
QDialog {
    background: #0a0c1e;
    border: 1px solid #1e2348;
    border-radius: 14px;
}
QLabel#Title {
    color: #dbe2ff;
    font-size: 17px;
    font-weight: 500;
    letter-spacing: 0.3px;
}
QLabel#Subtitle {
    color: #6b73a3;
    font-size: 11px;
    font-weight: 400;
    letter-spacing: 0.2px;
}
QLabel#Heading {
    color: #00e5ff;
    font-size: 11px;
    font-weight: 500;
    letter-spacing: 0.6px;
    border-bottom: 1px solid #1e2348;
    padding-bottom: 5px;
}
QFrame[frameShape="4"] { color: #1e2348; }
QScrollArea { border: none; background: transparent; }
"""
