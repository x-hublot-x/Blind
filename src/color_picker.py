"""Interactive Screen Color Picker (Eye-Dropper) with live 8x pixel magnifier."""

from PyQt6.QtWidgets import QWidget
from PyQt6.QtCore import Qt, QRect, QPoint, QPointF, QRectF, pyqtSignal, QTimer
from PyQt6.QtGui import (
    QPixmap, QPainter, QColor, QPen, QPainterPath,
    QMouseEvent, QKeyEvent, QGuiApplication, QCursor, QFont, QFontMetrics, QImage
)

_ACTIVE_TOASTS = []


class ColorToastNotification(QWidget):
    """Floating pill notification showing that the color was copied."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowFlags(
            Qt.WindowType.ToolTip |
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.NoDropShadowWindowHint
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)
        self.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating, True)
        
        self.text = ""
        self.color = QColor()
        self.timer = QTimer(self)
        self.timer.setSingleShot(True)
        self.timer.timeout.connect(self._on_timeout)

    def _on_timeout(self):
        self.close()
        if self in _ACTIVE_TOASTS:
            _ACTIVE_TOASTS.remove(self)

    def show_toast(self, hex_code: str, color: QColor, global_pos: QPoint, duration: int = 1600):
        self.text = f"{hex_code} скопирован"
        self.color = color
        
        font = QFont("Segoe UI", 10, QFont.Weight.Bold)
        fm = QFontMetrics(font)
        w = fm.horizontalAdvance(self.text) + 48
        h = 36
        self.setFixedSize(w, h)
        
        screen = QGuiApplication.primaryScreen().geometry()
        x = max(10, min(global_pos.x() - w // 2, screen.right() - w - 10))
        y = global_pos.y() - h - 20
        if y < 10:
            y = global_pos.y() + 25

        self.move(x, y)
        self.show()
        self.raise_()
        self.update()
        self.timer.start(duration)

    def paintEvent(self, event):
        if not self.text:
            return
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        painter.setRenderHint(QPainter.RenderHint.TextAntialiasing, True)

        rect = QRectF(1.0, 1.0, float(self.width()) - 2.0, float(self.height()) - 2.0)
        path = QPainterPath()
        path.addRoundedRect(rect, 8.0, 8.0)

        # Background
        painter.fillPath(path, QColor(24, 28, 36, 245))

        # Vector border
        painter.setPen(QPen(QColor(255, 255, 255, 80), 1.2))
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawPath(path)

        # Color dot
        dot_r = 6.0
        dot_center = QPointF(18.0, float(self.height()) / 2.0)
        painter.setPen(QPen(QColor(255, 255, 255, 180), 1.0))
        painter.setBrush(self.color)
        painter.drawEllipse(dot_center, dot_r, dot_r)

        # Text
        font = QFont("Segoe UI", 10, QFont.Weight.Bold)
        painter.setFont(font)
        painter.setPen(QColor("#FFFFFF"))
        text_rect = QRectF(32.0, 0.0, float(self.width()) - 36.0, float(self.height()))
        painter.drawText(text_rect, Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft, self.text)
        painter.end()


class ScreenColorPickerOverlay(QWidget):
    """Fullscreen color picker overlay with an 8x magnifier following the cursor."""

    color_picked = pyqtSignal(str, QColor)  # Emits (hex_string, qcolor)
    canceled = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, False)
        self.setMouseTracking(True)
        self.setCursor(Qt.CursorShape.CrossCursor)

        self.background_pixmap = None
        self._background_image = None
        self._desktop_geometry = QRect()
        self._current_pos = QPoint()
        self._current_color = QColor(255, 255, 255)

    def start_picker(self):
        """Captures all screens and launches interactive eye-dropper."""
        screens = QGuiApplication.screens()
        if not screens:
            return

        left = min(s.geometry().left() for s in screens)
        top = min(s.geometry().top() for s in screens)
        right = max(s.geometry().right() for s in screens)
        bottom = max(s.geometry().bottom() for s in screens)
        self._desktop_geometry = QRect(left, top, right - left + 1, bottom - top + 1)

        primary = QGuiApplication.primaryScreen()
        self.background_pixmap = primary.grabWindow(
            0,
            self._desktop_geometry.x(),
            self._desktop_geometry.y(),
            self._desktop_geometry.width(),
            self._desktop_geometry.height()
        )
        self._background_image = self.background_pixmap.toImage()

        self._current_pos = QCursor.pos()
        self._update_color_at_pos(self._current_pos)

        self.setGeometry(self._desktop_geometry)
        self.showFullScreen()
        self.raise_()
        self.activateWindow()

    def _update_color_at_pos(self, pos: QPoint):
        if not self._background_image:
            return
        
        dpr = self.devicePixelRatio()
        rel_x = int((pos.x() - self._desktop_geometry.x()) * dpr)
        rel_y = int((pos.y() - self._desktop_geometry.y()) * dpr)

        if 0 <= rel_x < self._background_image.width() and 0 <= rel_y < self._background_image.height():
            self._current_color = self._background_image.pixelColor(rel_x, rel_y)

    def _pick_current_color(self):
        hex_code = self._current_color.name(QColor.NameFormat.HexRgb).upper()
        clipboard = QGuiApplication.clipboard()
        clipboard.setText(hex_code)
        
        pos = QCursor.pos()
        toast = ColorToastNotification()
        toast.show_toast(hex_code, self._current_color, pos)
        _ACTIVE_TOASTS.append(toast)
        
        self.color_picked.emit(hex_code, self._current_color)
        self.close()

    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.LeftButton:
            self._pick_current_color()
            event.accept()
        elif event.button() == Qt.MouseButton.RightButton:
            self.canceled.emit()
            self.close()
            event.accept()

    def mouseMoveEvent(self, event: QMouseEvent):
        self._current_pos = event.pos()
        self._update_color_at_pos(self.mapToGlobal(event.pos()))
        self.update()

    def keyPressEvent(self, event: QKeyEvent):
        if event.key() == Qt.Key.Key_Escape:
            self.canceled.emit()
            self.close()
        elif event.key() in (Qt.Key.Key_Return, Qt.Key.Key_Enter, Qt.Key.Key_Space):
            self._pick_current_color()
        else:
            super().keyPressEvent(event)

    def paintEvent(self, event):
        if not self.background_pixmap:
            return

        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        painter.setRenderHint(QPainter.RenderHint.TextAntialiasing, True)

        # 1. Background image
        painter.drawPixmap(0, 0, self.background_pixmap)

        # 2. Draw Magnifier Loupe around current cursor
        pos = self._current_pos
        dpr = self.devicePixelRatio()

        loupe_radius = 54.0
        loupe_diameter = loupe_radius * 2
        
        # Position magnifier offset from cursor
        offset_x = 35
        offset_y = 35
        if pos.x() + offset_x + loupe_diameter > self.width():
            offset_x = -int(loupe_diameter) - 35
        if pos.y() + offset_y + loupe_diameter + 50 > self.height():
            offset_y = -int(loupe_diameter) - 50

        center = QPointF(pos.x() + offset_x + loupe_radius, pos.y() + offset_y + loupe_radius)
        loupe_rect = QRectF(center.x() - loupe_radius, center.y() - loupe_radius, loupe_diameter, loupe_diameter)

        # Magnifier shadow
        shadow_path = QPainterPath()
        shadow_path.addEllipse(loupe_rect.translated(0, 4))
        painter.fillPath(shadow_path, QColor(0, 0, 0, 100))

        # Magnifier circular crop
        clip_path = QPainterPath()
        clip_path.addEllipse(loupe_rect)

        painter.save()
        painter.setClipPath(clip_path)

        # Extract 15x15 pixel region around cursor
        grid_count = 15
        grid_half = grid_count // 2
        px = int(pos.x() * dpr)
        py = int(pos.y() * dpr)

        src_rect = QRect(px - grid_half, py - grid_half, grid_count, grid_count)
        cropped = self.background_pixmap.copy(src_rect)
        
        # Scaled up inside loupe
        painter.drawPixmap(loupe_rect.toRect(), cropped)

        # Grid lines
        grid_step = loupe_diameter / grid_count
        painter.setPen(QPen(QColor(255, 255, 255, 40), 1))
        for i in range(1, grid_count):
            # Vertical
            lx = loupe_rect.left() + i * grid_step
            painter.drawLine(int(lx), int(loupe_rect.top()), int(lx), int(loupe_rect.bottom()))
            # Horizontal
            ly = loupe_rect.top() + i * grid_step
            painter.drawLine(int(loupe_rect.left()), int(ly), int(loupe_rect.right()), int(ly))

        # Central target pixel frame
        center_box = QRectF(
            loupe_rect.left() + grid_half * grid_step,
            loupe_rect.top() + grid_half * grid_step,
            grid_step,
            grid_step
        )
        painter.setPen(QPen(QColor(255, 255, 255, 240), 1.5))
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawRect(center_box)

        painter.restore()

        # Loupe outer border
        border_pen = QPen(QColor(255, 255, 255, 200), 2.5)
        painter.setPen(border_pen)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawEllipse(loupe_rect)

        # 3. Information badge below the loupe
        badge_w = 140.0
        badge_h = 48.0
        badge_x = center.x() - badge_w / 2.0
        badge_y = loupe_rect.bottom() + 10.0

        badge_rect = QRectF(badge_x, badge_y, badge_w, badge_h)
        badge_path = QPainterPath()
        badge_path.addRoundedRect(badge_rect, 8.0, 8.0)

        # Badge shadow & background
        painter.fillPath(badge_path.translated(0, 2), QColor(0, 0, 0, 90))
        painter.fillPath(badge_path, QColor(24, 28, 36, 240))
        painter.setPen(QPen(QColor(255, 255, 255, 60), 1.2))
        painter.drawPath(badge_path)

        # Color preview circle inside badge
        c_preview_rect = QRectF(badge_x + 10, badge_y + (badge_h - 22) / 2, 22, 22)
        painter.setPen(QPen(QColor(255, 255, 255, 180), 1.2))
        painter.setBrush(self._current_color)
        painter.drawEllipse(c_preview_rect)

        # HEX Code and RGB strings
        hex_code = self._current_color.name(QColor.NameFormat.HexRgb).upper()
        rgb_str = f"RGB: {self._current_color.red()}, {self._current_color.green()}, {self._current_color.blue()}"

        font_hex = QFont("Segoe UI", 10, QFont.Weight.Bold)
        font_rgb = QFont("Segoe UI", 8)

        painter.setFont(font_hex)
        painter.setPen(QColor("#FFFFFF"))
        painter.drawText(int(badge_x + 40), int(badge_y + 19), hex_code)

        painter.setFont(font_rgb)
        painter.setPen(QColor("#94A3B8"))
        painter.drawText(int(badge_x + 40), int(badge_y + 36), rgb_str)

        painter.end()
