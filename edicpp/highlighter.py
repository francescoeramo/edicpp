from PyQt6.QtGui import QSyntaxHighlighter, QTextCharFormat, QColor, QFont
from PyQt6.QtCore import QRegularExpression

class CppHighlighter(QSyntaxHighlighter):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.rules = []
        self._init_rules()

    def _fmt(self, color, bold=False, italic=False):
        fmt = QTextCharFormat()
        fmt.setForeground(QColor(color))
        if bold:
            fmt.setFontWeight(QFont.Weight.Bold)
        if italic:
            fmt.setFontItalic(True)
        return fmt

    def _init_rules(self):
        # Colors - Tokyo Night inspired
        kw_fmt   = self._fmt("#bb9af7", bold=True)   # keywords purple
        type_fmt = self._fmt("#2ac3de", bold=True)   # types cyan
        num_fmt  = self._fmt("#ff9e64")              # numbers orange
        str_fmt  = self._fmt("#9ece6a")              # strings green
        com_fmt  = self._fmt("#565f89", italic=True) # comments gray
        pre_fmt  = self._fmt("#7dcfff")              # preprocessor cyan light
        func_fmt = self._fmt("#7aa2f7")              # functions blue

        keywords = [
            "alignas","alignof","and","and_eq","asm","auto","bitand","bitor","bool","break","case","catch",
            "char","char8_t","char16_t","char32_t","class","compl","concept","const","consteval","constexpr",
            "constinit","const_cast","continue","co_await","co_return","co_yield","decltype","default","delete",
            "do","double","dynamic_cast","else","enum","explicit","export","extern","false","float","for",
            "friend","goto","if","inline","int","long","mutable","namespace","new","noexcept","not","not_eq",
            "nullptr","operator","or","or_eq","private","protected","public","register","reinterpret_cast",
            "requires","return","short","signed","sizeof","static","static_assert","static_cast","struct",
            "switch","template","this","thread_local","throw","true","try","typedef","typeid","typename",
            "union","unsigned","using","virtual","void","volatile","wchar_t","while","xor","xor_eq",
            "override","final","import","module"
        ]
        types = [
            "std","string","vector","map","unordered_map","set","list","queue","stack","array","pair",
            "unique_ptr","shared_ptr","weak_ptr","optional","variant","tuple","function","iostream","ostream",
            "istream","cin","cout","cerr","endl","auto"
        ]

        # Keyword rule
        self.rules.append((QRegularExpression(r"\b(" + "|".join(keywords) + r")\b"), kw_fmt))
        self.rules.append((QRegularExpression(r"\b(" + "|".join(types) + r")\b"), type_fmt))

        # Numbers
        self.rules.append((QRegularExpression(r"\b0x[0-9a-fA-F]+\b|\b0b[01]+\b|\b\d+\.?\d*(?:[eE][+-]?\d+)?[fFlL]?\b"), num_fmt))
        # Strings
        self.rules.append((QRegularExpression(r'"[^"\\]*(\\.[^"\\]*)*"'), str_fmt))
        self.rules.append((QRegularExpression(r"'[^'\\]*(\\.[^'\\]*)*'"), str_fmt))
        # Preprocessor
        self.rules.append((QRegularExpression(r"^\s*#\s*\w+.*"), pre_fmt))
        # Single line comment
        self.rules.append((QRegularExpression(r"//[^\n]*"), com_fmt))
        # Function call highlight
        self.rules.append((QRegularExpression(r"\b[A-Za-z_]\w*(?=\s*\()"), func_fmt))

        self.comment_start = QRegularExpression(r"/\*")
        self.comment_end = QRegularExpression(r"\*/")
        self.comment_fmt = com_fmt

    def highlightBlock(self, text):
        for pattern, fmt in self.rules:
            it = pattern.globalMatch(text)
            while it.hasNext():
                m = it.next()
                self.setFormat(m.capturedStart(), m.capturedLength(), fmt)

        # multi-line comments
        self.setCurrentBlockState(0)
        start_idx = 0
        if self.previousBlockState() != 1:
            m = self.comment_start.match(text)
            start_idx = m.capturedStart() if m.hasMatch() else -1
        else:
            start_idx = 0

        while start_idx >= 0:
            end_match = self.comment_end.match(text, start_idx)
            if end_match.hasMatch():
                length = end_match.capturedEnd() - start_idx
                self.setFormat(start_idx, length, self.comment_fmt)
                m = self.comment_start.match(text, end_match.capturedEnd())
                start_idx = m.capturedStart() if m.hasMatch() else -1
            else:
                self.setFormat(start_idx, len(text) - start_idx, self.comment_fmt)
                self.setCurrentBlockState(1)
                break
