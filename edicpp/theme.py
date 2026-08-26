STYLESHEET = """
* {
    font-family: 'JetBrains Mono', 'Fira Code', 'Cascadia Code', monospace;
}

QMainWindow {
    background: #0a0e1a;
}

QWidget {
    color: #c0caf5;
}

/* MenuBar */
QMenuBar {
    background: #0f1423;
    color: #c0caf5;
    border-bottom: 1px solid #1e2030;
    padding: 4px;
    font-size: 13px;
}
QMenuBar::item:selected {
    background: #1e2030;
    border-radius: 6px;
}
QMenu {
    background: #16161e;
    border: 1px solid #2a2e44;
    border-radius: 8px;
    padding: 6px;
}
QMenu::item {
    padding: 7px 28px 7px 20px;
    border-radius: 6px;
}
QMenu::item:selected {
    background: #2a2e44;
    color: #7aa2f7;
}

/* Toolbar */
QToolBar {
    background: #0f1423;
    border-bottom: 1px solid #1e2030;
    spacing: 4px;
    padding: 6px 10px;
}
QToolButton {
    background: transparent;
    border-radius: 6px;
    padding: 6px 12px;
    color: #a9b1d6;
    font-size: 13px;
}
QToolButton:hover {
    background: #1e2030;
    color: #7aa2f7;
}

/* TreeView / File explorer */
QTreeView {
    background: #0f1423;
    border: none;
    border-right: 1px solid #1e2030;
    outline: none;
    font-size: 13px;
    show-decoration-selected: 1;
}
QTreeView::item {
    padding: 5px 8px;
    border-radius: 6px;
}
QTreeView::item:hover {
    background: #1a1e32;
}
QTreeView::item:selected {
    background: #24283b;
    color: #7aa2f7;
}
QHeaderView::section {
    background: #0f1423;
    color: #565f89;
    padding: 6px;
    border: none;
    font-size: 11px;
    letter-spacing: 1px;
}

/* Tabs */
QTabWidget::pane {
    border: 1px solid #1e2030;
    background: #0a0e1a;
    border-radius: 8px;
    top: -1px;
}
QTabBar::tab {
    background: #151a2e;
    color: #565f89;
    padding: 9px 18px;
    margin-right: 2px;
    border-top-left-radius: 8px;
    border-top-right-radius: 8px;
    border: 1px solid #1e2030;
    border-bottom: none;
    font-size: 13px;
}
QTabBar::tab:selected {
    background: #1a1e32;
    color: #c0caf5;
    border-bottom: 2px solid #7aa2f7;
}
QTabBar::tab:hover:!selected {
    background: #1c2240;
    color: #a9b1d6;
}
QTabBar::close-button {
    image: none;
    background: transparent;
}
QTabWidget::tab-bar { alignment: left; }

/* Splitter */
QSplitter::handle {
    background: #1e2030;
}
QSplitter::handle:horizontal { width: 1px; }
QSplitter::handle:vertical { height: 1px; }

/* Scrollbars */
QScrollBar:vertical {
    background: transparent;
    width: 8px;
    margin: 0;
}
QScrollBar::handle:vertical {
    background: #2a2e44;
    border-radius: 4px;
    min-height: 30px;
}
QScrollBar::handle:vertical:hover { background: #3b4261; }
QScrollBar::add-line, QScrollBar::sub-line { height: 0; }
QScrollBar:horizontal {
    background: transparent;
    height: 8px;
}
QScrollBar::handle:horizontal {
    background: #2a2e44;
    border-radius: 4px;
}

/* StatusBar */
QStatusBar {
    background: #0f1423;
    border-top: 1px solid #1e2030;
    color: #565f89;
    font-size: 12px;
}
QStatusBar QLabel {
    color: #565f89;
    padding: 2px 8px;
}

/* Buttons */
QPushButton {
    background: #24283b;
    color: #c0caf5;
    border: 1px solid #2a2e44;
    border-radius: 8px;
    padding: 8px 18px;
    font-size: 13px;
}
QPushButton:hover {
    background: #2a2e44;
    border-color: #7aa2f7;
    color: #7aa2f7;
}
QPushButton#Accent {
    background: #7aa2f7;
    color: #0a0e1a;
    border: none;
    font-weight: bold;
}
QPushButton#Accent:hover {
    background: #89b4fa;
}

/* LineEdit / Input */
QLineEdit {
    background: #16161e;
    border: 1px solid #2a2e44;
    border-radius: 8px;
    padding: 8px 12px;
    color: #c0caf5;
    selection-background-color: #364a82;
}
QLineEdit:focus { border-color: #7aa2f7; }

/* PlainTextEdit general */
QPlainTextEdit, QTextEdit {
    background: #0a0e1a;
    border: 1px solid #1e2030;
    border-radius: 8px;
    selection-background-color: #364a82;
}

/* Dialog */
QDialog {
    background: #0f1423;
    border: 1px solid #2a2e44;
    border-radius: 12px;
}
QLabel#Title {
    color: #c0caf5;
    font-size: 18px;
    font-weight: bold;
}
QLabel#Subtitle {
    color: #565f89;
    font-size: 12px;
}
QLabel#Heading {
    color: #7aa2f7;
    font-size: 13px;
    font-weight: bold;
    letter-spacing: 0.5px;
}
"""
