"""Vector icons and graphics generator using QPainter and high-DPI vector paths."""

from PyQt6.QtGui import QIcon, QPixmap, QPainter, QColor, QPen, QBrush, QPainterPath, QLinearGradient
from PyQt6.QtCore import Qt, QRectF, QPointF


def create_app_icon(size: int = 64) -> QIcon:
    """Creates a modern gradient app icon with clean vector geometry."""
    pixmap = QPixmap(size, size)
    pixmap.fill(Qt.GlobalColor.transparent)
    
    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    
    s = float(size)
    # Outer rounded rectangle with deep blue gradient
    rect = QRectF(s * 0.06, s * 0.06, s * 0.88, s * 0.88)
    grad = QLinearGradient(0, 0, s, s)
    grad.setColorAt(0.0, QColor("#3B82F6"))
    grad.setColorAt(1.0, QColor("#1D4ED8"))
    painter.setPen(Qt.PenStyle.NoPen)
    painter.setBrush(grad)
    painter.drawRoundedRect(rect, s * 0.26, s * 0.26)
    
    # Inner glowing frame
    pen = QPen(QColor("#FFFFFF"), max(1.5, s * 0.06), Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap, Qt.PenJoinStyle.RoundJoin)
    painter.setPen(pen)
    painter.setBrush(QColor(255, 255, 255, 30))
    screen_rect = QRectF(s * 0.22, s * 0.24, s * 0.56, s * 0.44)
    painter.drawRoundedRect(screen_rect, s * 0.08, s * 0.08)
    
    # Pin marker
    painter.setBrush(QColor("#F43F5E"))
    painter.setPen(QPen(QColor("#FFFFFF"), max(1.0, s * 0.04)))
    painter.drawEllipse(QPointF(s * 0.70, s * 0.26), s * 0.12, s * 0.12)
    
    painter.end()
    return QIcon(pixmap)


def draw_icon(name: str, color: str = None, size: int = 24) -> QIcon:
    """Generates a crisp, colorful vector icon with clean subpixel geometry."""
    # Render at 2x resolution for ultra-sharp high-DPI scaling
    render_size = size * 2
    pixmap = QPixmap(render_size, render_size)
    pixmap.fill(Qt.GlobalColor.transparent)
    
    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
    painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform, True)
    
    s = float(render_size)
    override_color = QColor(color) if color is not None and color != "colored" else None
    
    if name == "snip":
        # Multi-color Snip / Crop with Cyan/Blue brackets & white crosshair
        c_bracket = override_color or QColor("#38BDF8")
        c_cross = override_color or QColor("#FFFFFF")
        pen_b = QPen(c_bracket, max(2.0, s * 0.08), Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap, Qt.PenJoinStyle.RoundJoin)
        painter.setPen(pen_b)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        
        # 4 Corner brackets
        m = s * 0.18
        arm = s * 0.22
        # Top-Left
        p_tl = QPainterPath()
        p_tl.moveTo(m, m + arm)
        p_tl.lineTo(m, m)
        p_tl.lineTo(m + arm, m)
        painter.drawPath(p_tl)
        # Top-Right
        p_tr = QPainterPath()
        p_tr.moveTo(s - m - arm, m)
        p_tr.lineTo(s - m, m)
        p_tr.lineTo(s - m, m + arm)
        painter.drawPath(p_tr)
        # Bottom-Left
        p_bl = QPainterPath()
        p_bl.moveTo(m, s - m - arm)
        p_bl.lineTo(m, s - m)
        p_bl.lineTo(m + arm, s - m)
        painter.drawPath(p_bl)
        # Bottom-Right
        p_br = QPainterPath()
        p_br.moveTo(s - m - arm, s - m)
        p_br.lineTo(s - m, s - m)
        p_br.lineTo(s - m, s - m - arm)
        painter.drawPath(p_br)
        
        # Center Crosshair
        pen_c = QPen(c_cross, max(1.5, s * 0.07), Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap)
        painter.setPen(pen_c)
        ch = s * 0.12
        painter.drawLine(int(s * 0.5 - ch), int(s * 0.5), int(s * 0.5 + ch), int(s * 0.5))
        painter.drawLine(int(s * 0.5), int(s * 0.5 - ch), int(s * 0.5), int(s * 0.5 + ch))

    elif name == "pipette":
        # Precision eye-dropper with colored fluid & droplet
        c_bulb = override_color or QColor("#818CF8")
        c_glass = override_color or QColor("#E2E8F0")
        c_fluid = override_color or QColor("#06B6D4")
        
        # Eyedropper glass tube and bulb
        tube_path = QPainterPath()
        tube_path.moveTo(s * 0.68, s * 0.22)
        tube_path.lineTo(s * 0.78, s * 0.32)
        tube_path.lineTo(s * 0.60, s * 0.50)
        tube_path.lineTo(s * 0.38, s * 0.50)
        tube_path.lineTo(s * 0.24, s * 0.64)
        tube_path.lineTo(s * 0.20, s * 0.80)
        tube_path.lineTo(s * 0.36, s * 0.76)
        tube_path.lineTo(s * 0.50, s * 0.62)
        tube_path.lineTo(s * 0.50, s * 0.40)
        tube_path.closeSubpath()
        
        painter.setPen(QPen(c_glass, max(1.5, s * 0.06), Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap, Qt.PenJoinStyle.RoundJoin))
        painter.setBrush(c_fluid)
        painter.drawPath(tube_path)
        
        # Squeeze bulb cap
        bulb_path = QPainterPath()
        bulb_path.moveTo(s * 0.65, s * 0.25)
        bulb_path.lineTo(s * 0.75, s * 0.35)
        bulb_path.lineTo(s * 0.84, s * 0.26)
        bulb_path.lineTo(s * 0.74, s * 0.16)
        bulb_path.closeSubpath()
        painter.setPen(QPen(c_bulb, max(1.5, s * 0.05)))
        painter.setBrush(c_bulb)
        painter.drawPath(bulb_path)
        
        # Droplet at tip
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(c_fluid)
        painter.drawEllipse(QPointF(s * 0.14, s * 0.86), s * 0.05, s * 0.05)

    elif name == "pin":
        # 3D Pushpin with Crimson/Coral head & needle
        c_head = override_color or QColor("#F43F5E")
        c_neck = override_color or QColor("#FB7185")
        c_pin = override_color or QColor("#E2E8F0")
        
        # Steel needle
        painter.setPen(QPen(c_pin, max(2.0, s * 0.08), Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap))
        painter.drawLine(int(s * 0.5), int(s * 0.62), int(s * 0.5), int(s * 0.86))
        
        # Pin head body
        path = QPainterPath()
        path.moveTo(s * 0.32, s * 0.18)
        path.lineTo(s * 0.68, s * 0.18)
        path.lineTo(s * 0.60, s * 0.36)
        path.lineTo(s * 0.66, s * 0.62)
        path.lineTo(s * 0.34, s * 0.62)
        path.lineTo(s * 0.40, s * 0.36)
        path.closeSubpath()
        
        painter.setPen(QPen(c_head.darker(120), max(1.2, s * 0.05)))
        painter.setBrush(c_head)
        painter.drawPath(path)
        
        # Highlight rim
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(c_neck)
        painter.drawRoundedRect(QRectF(s * 0.30, s * 0.16, s * 0.40, s * 0.08), s * 0.04, s * 0.04)

    elif name == "ocr":
        # OCR Document + Emerald Green Scan Line
        c_card = override_color or QColor("#94A3B8")
        c_laser = override_color or QColor("#10B981")
        c_text = override_color or QColor("#E2E8F0")
        
        # Document sheet
        doc_rect = QRectF(s * 0.20, s * 0.16, s * 0.60, s * 0.68)
        painter.setPen(QPen(c_card, max(1.5, s * 0.06), Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap, Qt.PenJoinStyle.RoundJoin))
        painter.setBrush(QColor(30, 41, 59, 180))
        painter.drawRoundedRect(doc_rect, s * 0.08, s * 0.08)
        
        # Text lines
        painter.setPen(QPen(c_text, max(1.5, s * 0.06), Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap))
        painter.drawLine(int(s * 0.32), int(s * 0.34), int(s * 0.68), int(s * 0.34))
        painter.drawLine(int(s * 0.32), int(s * 0.50), int(s * 0.60), int(s * 0.50))
        painter.drawLine(int(s * 0.32), int(s * 0.66), int(s * 0.52), int(s * 0.66))
        
        # Glowing horizontal OCR laser scanner
        painter.setPen(QPen(c_laser, max(2.0, s * 0.08), Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap))
        painter.drawLine(int(s * 0.14), int(s * 0.50), int(s * 0.86), int(s * 0.50))

    elif name == "pen":
        # Drafting Pencil with golden body and graphite nib
        c_body = override_color or QColor("#F59E0B")
        c_tip = override_color or QColor("#334155")
        c_eraser = override_color or QColor("#F43F5E")
        
        body_path = QPainterPath()
        body_path.moveTo(s * 0.68, s * 0.18)
        body_path.lineTo(s * 0.82, s * 0.32)
        body_path.lineTo(s * 0.38, s * 0.76)
        body_path.lineTo(s * 0.24, s * 0.62)
        body_path.closeSubpath()
        painter.setPen(QPen(c_body.darker(120), max(1.2, s * 0.05)))
        painter.setBrush(c_body)
        painter.drawPath(body_path)
        
        # Nib
        nib_path = QPainterPath()
        nib_path.moveTo(s * 0.24, s * 0.62)
        nib_path.lineTo(s * 0.38, s * 0.76)
        nib_path.lineTo(s * 0.16, s * 0.84)
        nib_path.closeSubpath()
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(c_tip)
        painter.drawPath(nib_path)
        
        # Eraser top
        eraser_path = QPainterPath()
        eraser_path.moveTo(s * 0.68, s * 0.18)
        eraser_path.lineTo(s * 0.82, s * 0.32)
        eraser_path.lineTo(s * 0.86, s * 0.28)
        eraser_path.lineTo(s * 0.72, s * 0.14)
        eraser_path.closeSubpath()
        painter.setBrush(c_eraser)
        painter.drawPath(eraser_path)

    elif name == "arrow":
        # Indigo dynamic vector arrow
        c_arrow = override_color or QColor("#6366F1")
        painter.setPen(QPen(c_arrow, max(2.2, s * 0.10), Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap, Qt.PenJoinStyle.RoundJoin))
        painter.setBrush(c_arrow)
        
        # Shaft
        painter.drawLine(int(s * 0.22), int(s * 0.78), int(s * 0.72), int(s * 0.28))
        
        # Arrowhead
        head = QPainterPath()
        head.moveTo(s * 0.78, s * 0.22)
        head.lineTo(s * 0.44, s * 0.24)
        head.lineTo(s * 0.58, s * 0.38)
        head.closeSubpath()
        painter.drawPath(head)
        
        head2 = QPainterPath()
        head2.moveTo(s * 0.78, s * 0.22)
        head2.lineTo(s * 0.76, s * 0.56)
        head2.lineTo(s * 0.62, s * 0.42)
        head2.closeSubpath()
        painter.drawPath(head2)

    elif name == "rect":
        # Sky Blue rectangle tool frame with corner dots
        c_rect = override_color or QColor("#0EA5E9")
        painter.setPen(QPen(c_rect, max(2.0, s * 0.08), Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap, Qt.PenJoinStyle.RoundJoin))
        painter.setBrush(QColor(14, 165, 233, 35))
        painter.drawRoundedRect(QRectF(s * 0.20, s * 0.22, s * 0.60, s * 0.56), s * 0.06, s * 0.06)

    elif name == "highlighter":
        # Fluorescent Yellow/Lime Marker
        c_body = override_color or QColor("#64748B")
        c_tip = override_color or QColor("#FACC15")
        
        # Marker body
        body = QPainterPath()
        body.moveTo(s * 0.40, s * 0.24)
        body.lineTo(s * 0.76, s * 0.60)
        body.lineTo(s * 0.64, s * 0.72)
        body.lineTo(s * 0.28, s * 0.36)
        body.closeSubpath()
        painter.setPen(QPen(c_body.darker(120), max(1.2, s * 0.05)))
        painter.setBrush(c_body)
        painter.drawPath(body)
        
        # Chisel Tip
        tip = QPainterPath()
        tip.moveTo(s * 0.28, s * 0.36)
        tip.lineTo(s * 0.40, s * 0.24)
        tip.lineTo(s * 0.32, s * 0.16)
        tip.lineTo(s * 0.16, s * 0.24)
        tip.closeSubpath()
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(c_tip)
        painter.drawPath(tip)

    elif name == "palette":
        # Artist Palette with 4 vibrant paint drops
        c_pal = override_color or QColor("#94A3B8")
        pal_rect = QRectF(s * 0.16, s * 0.16, s * 0.68, s * 0.68)
        painter.setPen(QPen(c_pal, max(1.8, s * 0.07), Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap, Qt.PenJoinStyle.RoundJoin))
        painter.setBrush(QColor(30, 41, 59, 220))
        painter.drawRoundedRect(pal_rect, s * 0.24, s * 0.24)
        
        painter.setPen(Qt.PenStyle.NoPen)
        # 4 Colored dots
        dr = s * 0.07
        painter.setBrush(QColor("#EF4444"))  # Red
        painter.drawEllipse(QPointF(s * 0.36, s * 0.36), dr, dr)
        painter.setBrush(QColor("#F59E0B"))  # Yellow
        painter.drawEllipse(QPointF(s * 0.64, s * 0.36), dr, dr)
        painter.setBrush(QColor("#10B981"))  # Green
        painter.drawEllipse(QPointF(s * 0.36, s * 0.64), dr, dr)
        painter.setBrush(QColor("#3B82F6"))  # Blue
        painter.drawEllipse(QPointF(s * 0.64, s * 0.64), dr, dr)

    elif name == "undo":
        # Smooth circular undo return arrow
        c_undo = override_color or QColor("#818CF8")
        pen = QPen(c_undo, max(2.2, s * 0.09), Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap, Qt.PenJoinStyle.RoundJoin)
        painter.setPen(pen)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        
        # Arc
        painter.drawArc(QRectF(s * 0.24, s * 0.26, s * 0.52, s * 0.52), int(30 * 16), int(220 * 16))
        
        # Arrowhead pointing left
        painter.drawLine(int(s * 0.24), int(s * 0.52), int(s * 0.12), int(s * 0.38))
        painter.drawLine(int(s * 0.24), int(s * 0.52), int(s * 0.36), int(s * 0.52))

    elif name == "copy":
        # Double layered cards (Blue & Soft Slate)
        c_front = override_color or QColor("#38BDF8")
        c_back = override_color or QColor("#94A3B8")
        
        # Rear card
        painter.setPen(QPen(c_back, max(1.5, s * 0.06), Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap, Qt.PenJoinStyle.RoundJoin))
        painter.setBrush(QColor(30, 41, 59, 180))
        painter.drawRoundedRect(QRectF(s * 0.32, s * 0.16, s * 0.48, s * 0.52), s * 0.06, s * 0.06)
        
        # Front card
        painter.setPen(QPen(c_front, max(1.8, s * 0.07), Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap, Qt.PenJoinStyle.RoundJoin))
        painter.setBrush(QColor(15, 23, 42, 220))
        painter.drawRoundedRect(QRectF(s * 0.18, s * 0.30, s * 0.48, s * 0.52), s * 0.06, s * 0.06)

    elif name == "save":
        # Teal storage disk
        c_disk = override_color or QColor("#14B8A6")
        painter.setPen(QPen(c_disk, max(1.8, s * 0.07), Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap, Qt.PenJoinStyle.RoundJoin))
        painter.setBrush(QColor(20, 184, 166, 30))
        painter.drawRoundedRect(QRectF(s * 0.18, s * 0.18, s * 0.64, s * 0.64), s * 0.08, s * 0.08)
        
        # Shutter top
        painter.setBrush(QColor("#E2E8F0"))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRect(QRectF(s * 0.32, s * 0.18, s * 0.36, s * 0.22))
        
        # Bottom label box
        painter.setPen(QPen(c_disk, max(1.2, s * 0.05)))
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawRoundedRect(QRectF(s * 0.28, s * 0.50, s * 0.44, s * 0.24), s * 0.04, s * 0.04)

    elif name == "trash":
        # Rose/Crimson wastebin with lid accent
        c_trash = override_color or QColor("#FB7185")
        pen = QPen(c_trash, max(1.8, s * 0.07), Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap, Qt.PenJoinStyle.RoundJoin)
        painter.setPen(pen)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        
        # Bin body
        painter.drawRoundedRect(QRectF(s * 0.26, s * 0.32, s * 0.48, s * 0.52), s * 0.06, s * 0.06)
        # Lid & handle
        painter.drawLine(int(s * 0.18), int(s * 0.32), int(s * 0.82), int(s * 0.32))
        painter.drawLine(int(s * 0.40), int(s * 0.22), int(s * 0.60), int(s * 0.22))
        # Ribs
        painter.drawLine(int(s * 0.42), int(s * 0.44), int(s * 0.42), int(s * 0.70))
        painter.drawLine(int(s * 0.58), int(s * 0.44), int(s * 0.58), int(s * 0.70))

    elif name == "autostart":
        # Sky blue power / launch ring with accent
        c_auto = override_color or QColor("#38BDF8")
        pen = QPen(c_auto, max(2.0, s * 0.08), Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap)
        painter.setPen(pen)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawArc(QRectF(s * 0.20, s * 0.22, s * 0.60, s * 0.60), int(-45 * 16), int(270 * 16))
        painter.drawLine(int(s * 0.50), int(s * 0.14), int(s * 0.50), int(s * 0.46))

    elif name == "reset":
        # Lavender dual circular reload
        c_reset = override_color or QColor("#C084FC")
        pen = QPen(c_reset, max(2.0, s * 0.08), Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap, Qt.PenJoinStyle.RoundJoin)
        painter.setPen(pen)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawArc(QRectF(s * 0.20, s * 0.20, s * 0.60, s * 0.60), int(30 * 16), int(280 * 16))
        painter.drawLine(int(s * 0.64), int(s * 0.14), int(s * 0.82), int(s * 0.28))
        painter.drawLine(int(s * 0.82), int(s * 0.28), int(s * 0.64), int(s * 0.42))

    elif name == "close":
        # Coral Red smooth 'X'
        c_close = override_color or QColor("#F87171")
        pen = QPen(c_close, max(2.2, s * 0.09), Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap)
        painter.setPen(pen)
        m = s * 0.28
        painter.drawLine(int(m), int(m), int(s - m), int(s - m))
        painter.drawLine(int(s - m), int(m), int(m), int(s - m))

    elif name == "check":
        # Emerald checkmark
        c_check = override_color or QColor("#10B981")
        pen = QPen(c_check, max(2.4, s * 0.10), Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap, Qt.PenJoinStyle.RoundJoin)
        painter.setPen(pen)
        painter.drawLine(int(s * 0.22), int(s * 0.52), int(s * 0.42), int(s * 0.74))
        painter.drawLine(int(s * 0.42), int(s * 0.74), int(s * 0.78), int(s * 0.26))

    painter.end()
    return QIcon(pixmap)

