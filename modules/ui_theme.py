"""Design system for the LiveFaceCam desktop UI.

Warm neutral surfaces, white hairline cards, one indigo accent, compact 32px
controls, Plus Jakarta Sans + Lucide icons, light/dark following the OS.
"""
import os
import tempfile
from typing import Dict, List, Optional, Tuple

from PySide6.QtCore import QByteArray, QPointF, QRectF, QSize, Qt, Signal
from PySide6.QtGui import (
    QColor,
    QFont,
    QFontDatabase,
    QGuiApplication,
    QIcon,
    QPainter,
    QPixmap,
)
from PySide6.QtSvg import QSvgRenderer
from PySide6.QtWidgets import (
    QAbstractButton,
    QApplication,
    QHBoxLayout,
    QLabel,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

ASSETS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "assets")
FONT_FAMILY = "Plus Jakarta Sans"
FALLBACK_FONTS = '"Plus Jakarta Sans", "Segoe UI Variable Text", "Segoe UI", sans-serif'

LIGHT: Dict[str, str] = {
    "bg": "#f7f5f1", "card": "#ffffff", "fg": "#1c1a1b",
    "muted": "#efece7", "muted_fg": "#6b6466", "border": "#ddd8d1",
    "input": "#c9c3bb", "sidebar": "#f0ede8", "sidebar_active": "#e4dfd8",
    "primary": "#3730a3", "primary_hover": "#4338ca", "primary_fg": "#ffffff",
    "accent": "#e8e7fb", "accent_fg": "#2a2580",
    "success": "#1a6b3f", "warning": "#8a4b00", "destructive": "#b3261e",
    "thumb": "#ffffff",
}
DARK: Dict[str, str] = {
    "bg": "#151314", "card": "#1d1b1c", "fg": "#ece8e4",
    "muted": "#2a2728", "muted_fg": "#a8a1a3", "border": "#3b3738",
    "input": "#4a4547", "sidebar": "#111010", "sidebar_active": "#242122",
    "primary": "#a5b4fc", "primary_hover": "#c7d2fe", "primary_fg": "#151314",
    "accent": "#26244a", "accent_fg": "#c7cbfd",
    "success": "#5cc48a", "warning": "#e0a458", "destructive": "#f28b82",
    "thumb": "#ffffff",
}

THEME_MODES = ("system", "light", "dark")
_current: Dict[str, str] = dict(LIGHT)
_icon_bindings: List[Tuple[object, str, str, int]] = []
_fonts_loaded = False


def tokens() -> Dict[str, str]:
    return _current


def load_fonts() -> str:
    global _fonts_loaded
    if not _fonts_loaded:
        font_dir = os.path.join(ASSETS_DIR, "fonts")
        if os.path.isdir(font_dir):
            for name in os.listdir(font_dir):
                if name.lower().endswith(".ttf"):
                    QFontDatabase.addApplicationFont(os.path.join(font_dir, name))
        _fonts_loaded = True
    return FONT_FAMILY if FONT_FAMILY in QFontDatabase.families() else "Segoe UI"


def system_is_dark() -> bool:
    try:
        return QGuiApplication.styleHints().colorScheme() == Qt.ColorScheme.Dark
    except Exception:
        return False


def resolve_dark(mode: str) -> bool:
    if mode == "dark":
        return True
    if mode == "light":
        return False
    return system_is_dark()


def build_qss(t: Dict[str, str]) -> str:
    return f"""
* {{ font-family: {FALLBACK_FONTS}; font-size: 13px; color: {t['fg']}; }}
QMainWindow, QDialog, QWidget#content, QStackedWidget, QScrollArea, QWidget#page {{
    background: {t['bg']}; border: none;
}}
QToolTip {{ background: {t['fg']}; color: {t['bg']}; border: none; padding: 5px 8px; border-radius: 6px; }}

/* sidebar */
QFrame#sidebar {{ background: {t['sidebar']}; border-right: 1px solid {t['border']}; }}
QLabel#brand {{ font-size: 15px; font-weight: 600; }}
QLabel#brandVersion {{ color: {t['muted_fg']}; font-size: 11px; }}
QLabel#logoChip {{ background: {t['primary']}; border-radius: 8px; }}
QPushButton#navItem {{
    background: transparent; border: none; border-radius: 6px;
    min-height: 36px; padding: 0 12px; text-align: left;
    color: {t['muted_fg']}; font-size: 13.5px; font-weight: 500;
}}
QPushButton#navItem:hover {{ background: {t['sidebar_active']}; color: {t['fg']}; }}
QPushButton#navItem:checked {{ background: {t['sidebar_active']}; color: {t['fg']}; }}
QFrame#sidebarRule {{ background: {t['border']}; max-height: 1px; min-height: 1px; border: none; }}

/* page header */
QLabel#eyebrow {{ color: {t['muted_fg']}; font-size: 11px; font-weight: 500; }}
QLabel#pageTitle {{ font-size: 24px; font-weight: 500; }}
QLabel#pageDesc {{ color: {t['muted_fg']}; font-size: 14px; }}

/* cards */
QFrame#card {{ background: {t['card']}; border: 1px solid {t['border']}; border-radius: 12px; }}
QFrame#card QLabel, QWidget#switchRow {{ background: transparent; border: none; }}
QLabel#cardTitle {{ font-size: 14px; font-weight: 500; }}
QLabel#cardDesc, QLabel#hint {{ color: {t['muted_fg']}; font-size: 12px; }}
QLabel#fieldLabel {{ color: {t['muted_fg']}; font-size: 12px; font-weight: 500; }}
QFrame#rule {{ background: {t['border']}; max-height: 1px; min-height: 1px; border: none; }}
QFrame#card QLabel#imageDrop {{
    background: {t['muted']}; border: 1px dashed {t['input']}; border-radius: 10px;
    color: {t['muted_fg']}; font-size: 12px;
}}
QLabel#sliderValue {{ color: {t['muted_fg']}; font-size: 12px; }}

/* buttons */
QPushButton {{
    min-height: 32px; padding: 0 12px; border-radius: 8px; font-weight: 500;
    background: {t['card']}; color: {t['fg']}; border: 1px solid {t['border']};
}}
QPushButton:hover {{ background: {t['muted']}; }}
QPushButton:pressed {{ padding-top: 1px; }}
QPushButton:disabled {{ color: {t['muted_fg']}; background: {t['muted']}; border-color: {t['muted']}; }}
QPushButton[variant="primary"] {{ background: {t['primary']}; color: {t['primary_fg']}; border: 1px solid {t['primary']}; }}
QPushButton[variant="primary"]:hover {{ background: {t['primary_hover']}; border-color: {t['primary_hover']}; }}
QPushButton[variant="primary"]:disabled {{ background: {t['muted']}; color: {t['muted_fg']}; border-color: {t['muted']}; }}
QPushButton[variant="ghost"] {{ background: transparent; border: 1px solid transparent; color: {t['muted_fg']}; }}
QPushButton[variant="ghost"]:hover {{ background: {t['muted']}; color: {t['fg']}; }}
QPushButton[variant="danger"] {{ background: transparent; border: 1px solid transparent; color: {t['destructive']}; }}
QPushButton[variant="danger"]:hover {{ background: {t['muted']}; }}
QPushButton[size="lg"] {{ min-height: 40px; font-size: 14px; border-radius: 10px; }}

/* inputs */
QComboBox {{
    min-height: 32px; padding: 0 10px; border-radius: 8px;
    border: 1px solid {t['input']}; background: {t['card']};
}}
QComboBox:hover {{ border-color: {t['muted_fg']}; }}
QComboBox:focus {{ border-color: {t['primary']}; }}
QComboBox::drop-down {{ border: none; width: 24px; }}
QComboBox QAbstractItemView {{
    background: {t['card']}; border: 1px solid {t['border']}; border-radius: 8px;
    padding: 4px; outline: none; selection-background-color: {t['accent']}; selection-color: {t['accent_fg']};
}}
QSlider {{ min-height: 20px; background: transparent; }}
QSlider::groove:horizontal {{ height: 4px; background: {t['muted']}; border-radius: 2px; }}
QSlider::sub-page:horizontal {{ background: {t['primary']}; border-radius: 2px; }}
QSlider::handle:horizontal {{
    background: {t['thumb']}; width: 14px; height: 14px; margin: -6px 0;
    border-radius: 8px; border: 1px solid {t['primary']};
}}

/* status bar */
QFrame#statusBar {{ background: {t['bg']}; border-top: 1px solid {t['border']}; }}
QLabel#statusLabel {{ color: {t['muted_fg']}; font-size: 12px; }}
QLabel#pill {{ max-height: 20px;
    background: {t['accent']}; color: {t['accent_fg']}; border-radius: 9px;
    padding: 1px 8px; font-size: 11px; font-weight: 500;
}}

QScrollBar:vertical {{ background: transparent; width: 10px; margin: 2px; }}
QScrollBar::handle:vertical {{ background: {t['border']}; border-radius: 4px; min-height: 30px; }}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ height: 0; }}
QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {{ background: transparent; }}
QGroupBox {{ background: {t['card']}; border: 1px solid {t['border']}; border-radius: 12px; margin-top: 14px; padding-top: 18px; }}
QGroupBox::title {{ subcontrol-origin: margin; left: 10px; padding: 0 6px; color: {t['muted_fg']}; }}
QCheckBox {{ spacing: 8px; }}
"""


# ── icons ────────────────────────────────────────────────────────────────


def icon(name: str, role: str = "fg", size: int = 16) -> QIcon:
    path = os.path.join(ASSETS_DIR, "icons", f"{name}.svg")
    try:
        with open(path, encoding="utf-8") as f:
            svg = f.read()
    except OSError:
        return QIcon()
    svg = svg.replace("currentColor", _current.get(role, role))
    renderer = QSvgRenderer(QByteArray(svg.encode("utf-8")))
    scale = 2
    pm = QPixmap(size * scale, size * scale)
    pm.fill(Qt.GlobalColor.transparent)
    painter = QPainter(pm)
    renderer.render(painter, QRectF(0, 0, size * scale, size * scale))
    painter.end()
    pm.setDevicePixelRatio(scale)
    return QIcon(pm)


def bind_icon(widget, name: str, role: str = "fg", size: int = 16) -> None:
    """Set an icon and re-tint it automatically when the theme changes."""
    _icon_bindings[:] = [b for b in _icon_bindings if b[0] is not widget]
    _icon_bindings.append((widget, name, role, size))
    _apply_icon(widget, name, role, size)


def _apply_icon(widget, name: str, role: str, size: int) -> None:
    ic = icon(name, role, size)
    if isinstance(widget, QLabel):
        widget.setPixmap(ic.pixmap(QSize(size, size)))
    else:
        widget.setIcon(ic)
        widget.setIconSize(QSize(size, size))


def _combo_arrow_qss() -> str:
    # QSS image urls can't recolor SVGs, so write a tinted copy per theme.
    src = os.path.join(ASSETS_DIR, "icons", "chevron-down.svg")
    try:
        with open(src, encoding="utf-8") as f:
            svg = f.read().replace("currentColor", _current["muted_fg"])
        dest = os.path.join(tempfile.gettempdir(), f"lfc-chevron-{_current['muted_fg'][1:]}.svg")
        with open(dest, "w", encoding="utf-8") as f:
            f.write(svg)
    except OSError:
        return ""
    url = dest.replace("\\", "/")
    return f"\nQComboBox::down-arrow {{ image: url({url}); width: 14px; height: 14px; }}\n"


def apply_theme(app: QApplication, mode: str) -> bool:
    """Apply light/dark tokens. Returns True if dark."""
    global _current
    load_fonts()
    dark = resolve_dark(mode)
    _current = dict(DARK if dark else LIGHT)
    app.setStyle("Fusion")
    app.setStyleSheet(build_qss(_current) + _combo_arrow_qss())
    alive = []
    for binding in _icon_bindings:
        widget = binding[0]
        try:
            _apply_icon(*binding)
            alive.append(binding)
        except RuntimeError:  # widget was deleted
            pass
    _icon_bindings[:] = alive
    for w in app.allWidgets():
        if isinstance(w, ToggleSwitch):
            w.update()
    return dark


# ── widgets ──────────────────────────────────────────────────────────────


class ToggleSwitch(QAbstractButton):
    """32×18 pill switch (shadcn-style)."""

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.setCheckable(True)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setFixedSize(34, 20)

    def sizeHint(self) -> QSize:
        return QSize(34, 20)

    def paintEvent(self, _event) -> None:
        t = _current
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        track = QColor(t["primary"] if self.isChecked() else t["input"])
        if not self.isEnabled():
            track.setAlphaF(0.4)
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(track)
        p.drawRoundedRect(QRectF(1, 1, 32, 18), 9, 9)
        p.setBrush(QColor(t["thumb"]))
        x = 24 if self.isChecked() else 10
        p.drawEllipse(QPointF(x, 10), 7, 7)
        p.end()


class SwitchRow(QWidget):
    """Label (+ optional description) on the left, switch on the right."""

    toggled = Signal(bool)

    def __init__(self, text: str, initial: bool, tooltip: str = "", description: str = ""):
        super().__init__()
        self.setObjectName("switchRow")
        row = QHBoxLayout(self)
        row.setContentsMargins(0, 2, 0, 2)
        row.setSpacing(12)
        col = QVBoxLayout()
        col.setSpacing(1)
        self._label = QLabel(text)
        col.addWidget(self._label)
        if description:
            desc = QLabel(description)
            desc.setObjectName("hint")
            desc.setWordWrap(True)
            col.addWidget(desc)
        row.addLayout(col, 1)
        self._switch = ToggleSwitch()
        self._switch.setChecked(initial)
        self._switch.toggled.connect(self.toggled.emit)
        row.addWidget(self._switch, 0, Qt.AlignmentFlag.AlignVCenter)
        if tooltip:
            self.setToolTip(tooltip)
        self.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)

    def mouseReleaseEvent(self, event) -> None:
        if event.button() == Qt.MouseButton.LeftButton:
            self._switch.toggle()
        super().mouseReleaseEvent(event)

    def isChecked(self) -> bool:
        return self._switch.isChecked()

    def setChecked(self, value: bool) -> None:
        self._switch.setChecked(value)


def eyebrow(text: str) -> QLabel:
    label = QLabel(text.upper())
    label.setObjectName("eyebrow")
    f = label.font()
    f.setLetterSpacing(QFont.SpacingType.AbsoluteSpacing, 0.9)
    label.setFont(f)
    return label
