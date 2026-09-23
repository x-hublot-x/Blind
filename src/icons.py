"""Vector icons and graphics generator using QPainter and SVG paths for high DPI displays."""

from PyQt6.QtGui import QIcon, QPixmap, QPainter, QColor, QPen, QBrush, QPainterPath
from PyQt6.QtCore import Qt, QRectF, QPointF


def create_app_icon(size: int = 64) -> QIcon:
    """Creates a modern gradient app icon."""
    pixmap = QPixmap(size, size)
    pixmap.fill(Qt.GlobalColor.transparent)
    
    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    
    # Outer rounded rectangle
    rect = QRectF(4, 4, size - 8, size - 8)
    painter.setPen(Qt.PenStyle.NoPen)
    painter.setBrush(QColor("#2563EB"))  # Royal blue
    painter.drawRoundedRect(rect, size * 0.28, size * 0.28)
    
    # Inner glowing pin / frame
    pen = QPen(QColor("#FFFFFF"), size * 0.08, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap, Qt.PenJoinStyle.RoundJoin)
    painter.setPen(pen)
    painter.setBrush(Qt.BrushStyle.NoBrush)
    
    # Screen frame
    screen_rect = QRectF(size * 0.24, size * 0.24, size * 0.52, size * 0.4)
    painter.drawRoundedRect(screen_rect, 4, 4)
    
    # Pin marker
    painter.setBrush(QColor("#38BDF8"))
    painter.setPen(Qt.PenStyle.NoPen)
    painter.drawEllipse(QPointF(size * 0.72, size * 0.28), size * 0.12, size * 0.12)
    
    painter.end()
    return QIcon(pixmap)


def draw_icon(name: str, color: str = "#FFFFFF", size: int = 24) -> QIcon:
    """Generates an icon on the fly with crisp vector shapes."""
    pixmap = QPixmap(size, size)
    pixmap.fill(Qt.GlobalColor.transparent)
    
    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    
    qcolor = QColor(color)
    pen = QPen(qcolor, 2, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap, Qt.PenJoinStyle.RoundJoin)
    painter.setPen(pen)
    
    if name == "snip":
        # Crop / snip corners icon
        s = size
        # Top-left corner
        painter.drawLine(int(s * 0.2), int(s * 0.35), int(s * 0.2), int(s * 0.2))
        painter.drawLine(int(s * 0.2), int(s * 0.2), int(s * 0.35), int(s * 0.2))
        # Top-right corner
        painter.drawLine(int(s * 0.8), int(s * 0.35), int(s * 0.8), int(s * 0.2))
        painter.drawLine(int(s * 0.8), int(s * 0.2), int(s * 0.65), int(s * 0.2))
        # Bottom-left corner
        painter.drawLine(int(s * 0.2), int(s * 0.65), int(s * 0.2), int(s * 0.8))
        painter.drawLine(int(s * 0.2), int(s * 0.8), int(s * 0.35), int(s * 0.8))
        # Bottom-right corner
        painter.drawLine(int(s * 0.8), int(s * 0.65), int(s * 0.8), int(s * 0.8))
        painter.drawLine(int(s * 0.8), int(s * 0.8), int(s * 0.65), int(s * 0.8))
        # Center plus
        painter.drawLine(int(s * 0.4), int(s * 0.5), int(s * 0.6), int(s * 0.5))
        painter.drawLine(int(s * 0.5), int(s * 0.4), int(s * 0.5), int(s * 0.6))
        
    elif name == "pin":
        # Pushpin icon
        painter.setBrush(qcolor)
        path = QPainterPath()
        s = size
        path.moveTo(s * 0.5, s * 0.15)
        path.lineTo(s * 0.65, s * 0.35)
        path.lineTo(s * 0.55, s * 0.4)
        path.lineTo(s * 0.6, s * 0.65)
        path.lineTo(s * 0.4, s * 0.65)
        path.lineTo(s * 0.45, s * 0.4)
        path.lineTo(s * 0.35, s * 0.35)
        path.closeSubpath()
        painter.drawPath(path)
        painter.drawLine(int(s * 0.5), int(s * 0.65), int(s * 0.5), int(s * 0.85))
        
    elif name == "close":
        s = size
        margin = s * 0.28
        painter.drawLine(int(margin), int(margin), int(s - margin), int(s - margin))
        painter.drawLine(int(s - margin), int(margin), int(margin), int(s - margin))
        
    elif name == "copy":
        s = size
        # Back rect
        painter.drawRoundedRect(QRectF(s * 0.32, s * 0.18, s * 0.48, s * 0.52), 2, 2)
        # Front rect
        painter.setBrush(QColor("#1E293B"))
        painter.drawRoundedRect(QRectF(s * 0.2, s * 0.32, s * 0.48, s * 0.52), 2, 2)
        
    elif name == "save":
        s = size
        painter.drawRoundedRect(QRectF(s * 0.2, s * 0.2, s * 0.6, s * 0.6), 3, 3)
        painter.drawLine(int(s * 0.35), int(s * 0.2), int(s * 0.35), int(s * 0.4))
        painter.drawLine(int(s * 0.65), int(s * 0.2), int(s * 0.65), int(s * 0.4))
        painter.drawRect(QRectF(s * 0.32, s * 0.52, s * 0.36, s * 0.28))
        
    elif name == "autostart":
        s = size
        # Power / launch rocket icon
        painter.drawArc(QRectF(s * 0.22, s * 0.25, s * 0.56, s * 0.56), int(-40 * 16), int(260 * 16))
        painter.drawLine(int(s * 0.5), int(s * 0.18), int(s * 0.5), int(s * 0.48))
        
    elif name == "reset":
        s = size
        painter.drawArc(QRectF(s * 0.2, s * 0.2, s * 0.6, s * 0.6), int(30 * 16), int(280 * 16))
        painter.drawLine(int(s * 0.65), int(s * 0.15), int(s * 0.8), int(s * 0.3))
        painter.drawLine(int(s * 0.8), int(s * 0.3), int(s * 0.65), int(s * 0.45))
        
    elif name == "opacity":
        s = size
        painter.drawEllipse(QRectF(s * 0.2, s * 0.2, s * 0.6, s * 0.6))
        painter.setBrush(qcolor)
        painter.drawPie(QRectF(s * 0.2, s * 0.2, s * 0.6, s * 0.6), int(90 * 16), int(180 * 16))
        
    elif name == "lock":
        s = size
        painter.drawRoundedRect(QRectF(s * 0.24, s * 0.45, s * 0.52, s * 0.4), 2, 2)
        painter.drawArc(QRectF(s * 0.34, s * 0.2, s * 0.32, s * 0.35), int(0), int(180 * 16))
        
    elif name == "trash":
        s = size
        painter.drawLine(int(s * 0.2), int(s * 0.3), int(s * 0.8), int(s * 0.3))
        painter.drawLine(int(s * 0.4), int(s * 0.2), int(s * 0.6), int(s * 0.2))
        painter.drawRoundedRect(QRectF(s * 0.28, s * 0.3, s * 0.44, s * 0.55), 2, 2)
        painter.drawLine(int(s * 0.42), int(s * 0.42), int(s * 0.42), int(s * 0.72))
        painter.drawLine(int(s * 0.58), int(s * 0.42), int(s * 0.58), int(s * 0.72))
        
    elif name == "expand":
        s = size
        # Arrow pointing left/right
        painter.drawLine(int(s * 0.65), int(s * 0.25), int(s * 0.35), int(s * 0.5))
        painter.drawLine(int(s * 0.35), int(s * 0.5), int(s * 0.65), int(s * 0.75))
        
    painter.end()
    return QIcon(pixmap)
