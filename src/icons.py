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
    s = float(size)
    
    if name == "snip":
        # Crop / snip corners icon
        painter.drawLine(int(s * 0.2), int(s * 0.35), int(s * 0.2), int(s * 0.2))
        painter.drawLine(int(s * 0.2), int(s * 0.2), int(s * 0.35), int(s * 0.2))
        painter.drawLine(int(s * 0.8), int(s * 0.35), int(s * 0.8), int(s * 0.2))
        painter.drawLine(int(s * 0.8), int(s * 0.2), int(s * 0.65), int(s * 0.2))
        painter.drawLine(int(s * 0.2), int(s * 0.65), int(s * 0.2), int(s * 0.8))
        painter.drawLine(int(s * 0.2), int(s * 0.8), int(s * 0.35), int(s * 0.8))
        painter.drawLine(int(s * 0.8), int(s * 0.65), int(s * 0.8), int(s * 0.8))
        painter.drawLine(int(s * 0.8), int(s * 0.8), int(s * 0.65), int(s * 0.8))
        painter.drawLine(int(s * 0.4), int(s * 0.5), int(s * 0.6), int(s * 0.5))
        painter.drawLine(int(s * 0.5), int(s * 0.4), int(s * 0.5), int(s * 0.6))
        
    elif name == "pin":
        painter.setBrush(qcolor)
        path = QPainterPath()
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
        margin = s * 0.28
        painter.drawLine(int(margin), int(margin), int(s - margin), int(s - margin))
        painter.drawLine(int(s - margin), int(margin), int(margin), int(s - margin))
        
    elif name == "copy":
        painter.drawRoundedRect(QRectF(s * 0.32, s * 0.18, s * 0.48, s * 0.52), 2, 2)
        painter.setBrush(QColor("#1E293B"))
        painter.drawRoundedRect(QRectF(s * 0.2, s * 0.32, s * 0.48, s * 0.52), 2, 2)
        
    elif name == "save":
        painter.drawRoundedRect(QRectF(s * 0.2, s * 0.2, s * 0.6, s * 0.6), 3, 3)
        painter.drawLine(int(s * 0.35), int(s * 0.2), int(s * 0.35), int(s * 0.4))
        painter.drawLine(int(s * 0.65), int(s * 0.2), int(s * 0.65), int(s * 0.4))
        painter.drawRect(QRectF(s * 0.32, s * 0.52, s * 0.36, s * 0.28))
        
    elif name == "autostart":
        painter.drawArc(QRectF(s * 0.22, s * 0.25, s * 0.56, s * 0.56), int(-40 * 16), int(260 * 16))
        painter.drawLine(int(s * 0.5), int(s * 0.18), int(s * 0.5), int(s * 0.48))
        
    elif name == "reset":
        painter.drawArc(QRectF(s * 0.2, s * 0.2, s * 0.6, s * 0.6), int(30 * 16), int(280 * 16))
        painter.drawLine(int(s * 0.65), int(s * 0.15), int(s * 0.8), int(s * 0.3))
        painter.drawLine(int(s * 0.8), int(s * 0.3), int(s * 0.65), int(s * 0.45))
        
    elif name == "pipette":
        # Eye-dropper / pipette icon
        path = QPainterPath()
        path.moveTo(s * 0.72, s * 0.18)
        path.lineTo(s * 0.82, s * 0.28)
        path.lineTo(s * 0.68, s * 0.42)
        path.lineTo(s * 0.42, s * 0.42)
        path.lineTo(s * 0.22, s * 0.62)
        path.lineTo(s * 0.18, s * 0.82)
        path.lineTo(s * 0.38, s * 0.78)
        path.lineTo(s * 0.58, s * 0.58)
        path.lineTo(s * 0.58, s * 0.32)
        path.closeSubpath()
        painter.setBrush(qcolor)
        painter.drawPath(path)
        painter.drawLine(int(s * 0.18), int(s * 0.82), int(s * 0.12), int(s * 0.88))
        
    elif name == "ocr":
        # OCR Text scan icon
        painter.drawRoundedRect(QRectF(s * 0.18, s * 0.2, s * 0.64, s * 0.6), 2, 2)
        # Letter 'T' or text lines
        painter.drawLine(int(s * 0.32), int(s * 0.38), int(s * 0.68), int(s * 0.38))
        painter.drawLine(int(s * 0.5), int(s * 0.38), int(s * 0.5), int(s * 0.68))
        
    elif name == "pen":
        # Freehand pencil icon
        path = QPainterPath()
        path.moveTo(s * 0.7, s * 0.18)
        path.lineTo(s * 0.82, s * 0.3)
        path.lineTo(s * 0.35, s * 0.77)
        path.lineTo(s * 0.2, s * 0.8)
        path.lineTo(s * 0.23, s * 0.65)
        path.closeSubpath()
        painter.setBrush(qcolor)
        painter.drawPath(path)
        
    elif name == "arrow":
        # Diagonal arrow icon
        painter.drawLine(int(s * 0.25), int(s * 0.75), int(s * 0.75), int(s * 0.25))
        painter.drawLine(int(s * 0.75), int(s * 0.25), int(s * 0.45), int(s * 0.25))
        painter.drawLine(int(s * 0.75), int(s * 0.25), int(s * 0.75), int(s * 0.55))
        
    elif name == "rect":
        # Rectangle tool icon
        painter.drawRect(QRectF(s * 0.22, s * 0.25, s * 0.56, s * 0.5))
        
    elif name == "highlighter":
        # Marker / highlighter icon
        painter.drawLine(int(s * 0.25), int(s * 0.75), int(s * 0.75), int(s * 0.25))
        painter.drawLine(int(s * 0.35), int(s * 0.85), int(s * 0.85), int(s * 0.35))
        painter.drawLine(int(s * 0.25), int(s * 0.75), int(s * 0.35), int(s * 0.85))
        painter.drawLine(int(s * 0.75), int(s * 0.25), int(s * 0.85), int(s * 0.35))
        
    elif name == "undo":
        # Undo curved back arrow
        painter.drawArc(QRectF(s * 0.25, s * 0.3, s * 0.5, s * 0.5), int(0), int(180 * 16))
        painter.drawLine(int(s * 0.25), int(s * 0.55), int(s * 0.15), int(s * 0.38))
        painter.drawLine(int(s * 0.25), int(s * 0.55), int(s * 0.38), int(s * 0.55))
        
    elif name == "trash":
        painter.drawLine(int(s * 0.2), int(s * 0.3), int(s * 0.8), int(s * 0.3))
        painter.drawLine(int(s * 0.4), int(s * 0.2), int(s * 0.6), int(s * 0.2))
        painter.drawRoundedRect(QRectF(s * 0.28, s * 0.3, s * 0.44, s * 0.55), 2, 2)
        painter.drawLine(int(s * 0.42), int(s * 0.42), int(s * 0.42), int(s * 0.72))
        painter.drawLine(int(s * 0.58), int(s * 0.42), int(s * 0.58), int(s * 0.72))
        
    painter.end()
    return QIcon(pixmap)
