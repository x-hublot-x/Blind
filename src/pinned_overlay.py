"""Floating Always-on-Top Pinned Image Widget with smooth zoom, drag, resize handles, and clean antialiased rendering."""

import os
from enum import Enum, auto

from PyQt6.QtWidgets import (
    QWidget, QHBoxLayout, QPushButton,
    QFileDialog, QMenu, QToolTip
)
from PyQt6.QtCore import Qt, QPoint, pyqtSignal, QRect, QRectF
from PyQt6.QtGui import (
    QPixmap, QPainter, QColor, QPen, QPainterPath,
    QMouseEvent, QWheelEvent, QGuiApplication, QAction, QCursor
)
from .icons import draw_icon
from .ocr import recognize_text_from_pixmap


class ResizeZone(Enum):
    NONE = auto()
    MOVE = auto()
    TOP = auto()
    BOTTOM = auto()
    LEFT = auto()
    RIGHT = auto()
    TOP_LEFT = auto()
    TOP_RIGHT = auto()
    BOTTOM_LEFT = auto()
    BOTTOM_RIGHT = auto()


class PinnedImageWidget(QWidget):
    """Floating frameless window that stays on top of all applications with smooth corners, zoom, and edge resizing."""

    closed = pyqtSignal(object)

    def __init__(self, pixmap: QPixmap, initial_pos: QPoint = None, parent=None):
        super().__init__(parent)
        
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.setAttribute(Qt.WidgetAttribute.WA_Hover, True)
        self.setMouseTracking(True)
        
        self.original_pixmap = pixmap
        self.current_scale = 1.0
        self.min_scale = 0.15
        self.max_scale = 6.0
        
        self._resize_zone = ResizeZone.NONE
        self._drag_start_pos = QPoint()
        self._drag_start_geo = QRect()
        
        self._opacity = 1.0
        self._border_radius = 10.0
        self._padding = 6
        self._margin = 8  # Edge handle hit margin

        self._init_ui()
        
        if initial_pos:
            self.move(initial_pos)
        else:
            cursor_pos = QCursor.pos()
            self.move(max(40, cursor_pos.x() - self.width() // 2), max(40, cursor_pos.y() - self.height() // 2))

    def _init_ui(self):
        # Micro toolbar
        self.toolbar = QWidget(self)
        self.toolbar.setObjectName("PinnedToolbar")
        
        tb_layout = QHBoxLayout(self.toolbar)
        tb_layout.setContentsMargins(4, 2, 4, 2)
        tb_layout.setSpacing(3)

        # Micro buttons
        self.btn_copy = QPushButton(self.toolbar)
        self.btn_copy.setProperty("class", "micro-btn")
        self.btn_copy.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_copy.setIcon(draw_icon("copy", "#E2E8F0", 12))
        self.btn_copy.setToolTip("Копировать (Ctrl+C)")
        self.btn_copy.clicked.connect(self.copy_to_clipboard)

        self.btn_ocr = QPushButton(self.toolbar)
        self.btn_ocr.setProperty("class", "micro-btn")
        self.btn_ocr.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_ocr.setIcon(draw_icon("ocr", "#E2E8F0", 12))
        self.btn_ocr.setToolTip("Распознать текст OCR (Ctrl+T)")
        self.btn_ocr.clicked.connect(self.recognize_ocr)

        self.btn_save = QPushButton(self.toolbar)
        self.btn_save.setProperty("class", "micro-btn")
        self.btn_save.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_save.setIcon(draw_icon("save", "#E2E8F0", 12))
        self.btn_save.setToolTip("Сохранить (Ctrl+S)")
        self.btn_save.clicked.connect(self.save_to_file)

        self.btn_reset = QPushButton(self.toolbar)
        self.btn_reset.setProperty("class", "micro-btn")
        self.btn_reset.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_reset.setIcon(draw_icon("reset", "#E2E8F0", 12))
        self.btn_reset.setToolTip("Сброс масштаба 100% (2x клик)")
        self.btn_reset.clicked.connect(self.reset_scale)

        self.btn_close = QPushButton(self.toolbar)
        self.btn_close.setProperty("class", "micro-danger-btn")
        self.btn_close.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_close.setIcon(draw_icon("close", "#F87171", 12))
        self.btn_close.setToolTip("Закрыть (Del / Esc)")
        self.btn_close.clicked.connect(self.close)

        tb_layout.addWidget(self.btn_copy)
        tb_layout.addWidget(self.btn_ocr)
        tb_layout.addWidget(self.btn_save)
        tb_layout.addWidget(self.btn_reset)
        tb_layout.addWidget(self.btn_close)

        self.toolbar.adjustSize()
        self.toolbar.hide()

        # Set initial dimensions based on original image
        w = self.original_pixmap.width() + self._padding * 2
        h = self.original_pixmap.height() + self._padding * 2
        self.resize(w, h)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform, True)

        p = float(self._padding)
        card_rect = QRectF(p, p, float(self.width()) - 2.0 * p, float(self.height()) - 2.0 * p)

        # 1. Main smooth rounded path
        path = QPainterPath()
        path.addRoundedRect(card_rect, self._border_radius, self._border_radius)

        # 2. Draw card background & image
        painter.save()
        painter.setClipPath(path)
        
        # Dark acrylic glass background
        painter.fillRect(card_rect, QColor(28, 32, 40, 240))

        # Smooth image scale & center
        scaled_pixmap = self.original_pixmap.scaled(
            int(card_rect.width()),
            int(card_rect.height()),
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation
        )
        img_x = card_rect.x() + (card_rect.width() - scaled_pixmap.width()) / 2.0
        img_y = card_rect.y() + (card_rect.height() - scaled_pixmap.height()) / 2.0
        painter.drawPixmap(int(img_x), int(img_y), scaled_pixmap)

        painter.restore()

        # 3. Clean Anti-aliased border (no pixel dots)
        border_pen = QPen(QColor(255, 255, 255, 65), 1.2, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap, Qt.PenJoinStyle.RoundJoin)
        painter.setPen(border_pen)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawPath(path)

        # 4. Toolbar background
        if self.toolbar.isVisible():
            tb_rect = QRectF(self.toolbar.geometry())
            tb_path = QPainterPath()
            tb_path.addRoundedRect(tb_rect, 7.0, 7.0)
            painter.fillPath(tb_path, QColor(22, 26, 32, 235))
            tb_pen = QPen(QColor(255, 255, 255, 50), 1.0)
            painter.setPen(tb_pen)
            painter.drawPath(tb_path)

        painter.end()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.toolbar.move(
            self.width() - self._padding - self.toolbar.width() - 4,
            self._padding + 4
        )

    def enterEvent(self, event):
        self.toolbar.show()
        self.toolbar.raise_()
        self.update()
        super().enterEvent(event)

    def leaveEvent(self, event):
        self.toolbar.hide()
        self.update()
        super().leaveEvent(event)

    def _get_resize_zone(self, pos: QPoint) -> ResizeZone:
        m = self._margin
        w = self.width()
        h = self.height()
        
        # Don't resize if hovering over toolbar
        if self.toolbar.isVisible() and self.toolbar.geometry().contains(pos):
            return ResizeZone.NONE

        x = pos.x()
        y = pos.y()

        # Corners
        if x < m and y < m:
            return ResizeZone.TOP_LEFT
        if x > w - m and y < m:
            return ResizeZone.TOP_RIGHT
        if x < m and y > h - m:
            return ResizeZone.BOTTOM_LEFT
        if x > w - m and y > h - m:
            return ResizeZone.BOTTOM_RIGHT

        # Edges
        if x < m:
            return ResizeZone.LEFT
        if x > w - m:
            return ResizeZone.RIGHT
        if y < m:
            return ResizeZone.TOP
        if y > h - m:
            return ResizeZone.BOTTOM

        return ResizeZone.MOVE

    def _update_cursor(self, zone: ResizeZone):
        if zone in (ResizeZone.TOP_LEFT, ResizeZone.BOTTOM_RIGHT):
            self.setCursor(Qt.CursorShape.SizeFDiagCursor)
        elif zone in (ResizeZone.TOP_RIGHT, ResizeZone.BOTTOM_LEFT):
            self.setCursor(Qt.CursorShape.SizeBDiagCursor)
        elif zone in (ResizeZone.TOP, ResizeZone.BOTTOM):
            self.setCursor(Qt.CursorShape.SizeVerCursor)
        elif zone in (ResizeZone.LEFT, ResizeZone.RIGHT):
            self.setCursor(Qt.CursorShape.SizeHorCursor)
        elif zone == ResizeZone.MOVE:
            self.setCursor(Qt.CursorShape.SizeAllCursor)
        else:
            self.setCursor(Qt.CursorShape.ArrowCursor)

    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.LeftButton:
            pos = event.pos()
            if self.toolbar.isVisible() and self.toolbar.geometry().contains(pos):
                super().mousePressEvent(event)
                return

            self._resize_zone = self._get_resize_zone(pos)
            self._drag_start_pos = event.globalPosition().toPoint()
            self._drag_start_geo = QRect(self.geometry())
            event.accept()
        elif event.button() == Qt.MouseButton.RightButton:
            self._show_context_menu(event.globalPosition().toPoint())
            event.accept()
        else:
            super().mousePressEvent(event)

    def mouseMoveEvent(self, event: QMouseEvent):
        if self._resize_zone == ResizeZone.NONE:
            zone = self._get_resize_zone(event.pos())
            self._update_cursor(zone)
            return

        cur_glob = event.globalPosition().toPoint()
        dx = cur_glob.x() - self._drag_start_pos.x()
        dy = cur_glob.y() - self._drag_start_pos.y()
        init = self._drag_start_geo

        if self._resize_zone == ResizeZone.MOVE:
            self.move(init.topLeft() + QPoint(dx, dy))
            event.accept()
            return

        # Interactive edge/corner resize maintaining aspect ratio
        aspect = self.original_pixmap.width() / max(1, self.original_pixmap.height())
        new_w = init.width()
        new_h = init.height()
        new_x = init.x()
        new_y = init.y()

        if self._resize_zone in (ResizeZone.RIGHT, ResizeZone.BOTTOM_RIGHT, ResizeZone.TOP_RIGHT):
            new_w = max(60, init.width() + dx)
            new_h = int(new_w / aspect)
        elif self._resize_zone in (ResizeZone.LEFT, ResizeZone.BOTTOM_LEFT, ResizeZone.TOP_LEFT):
            new_w = max(60, init.width() - dx)
            new_h = int(new_w / aspect)
            new_x = init.right() - new_w
        elif self._resize_zone in (ResizeZone.BOTTOM, ResizeZone.TOP):
            new_h = max(40, init.height() + (dy if self._resize_zone == ResizeZone.BOTTOM else -dy))
            new_w = int(new_h * aspect)
            if self._resize_zone == ResizeZone.TOP:
                new_y = init.bottom() - new_h

        self.setGeometry(new_x, new_y, new_w, new_h)
        self.current_scale = (new_w - self._padding * 2) / float(self.original_pixmap.width())
        self.update()
        event.accept()

    def mouseReleaseEvent(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.LeftButton:
            self._resize_zone = ResizeZone.NONE
            self._update_cursor(self._get_resize_zone(event.pos()))
            event.accept()
        else:
            super().mouseReleaseEvent(event)

    def mouseDoubleClickEvent(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.LeftButton:
            self.reset_scale()
            event.accept()
        else:
            super().mouseDoubleClickEvent(event)

    def wheelEvent(self, event: QWheelEvent):
        modifiers = event.modifiers()
        
        # Check angleDelta, pixelDelta, or horizontal delta
        delta = event.angleDelta().y()
        if delta == 0:
            delta = event.pixelDelta().y()
        if delta == 0:
            delta = event.angleDelta().x()

        # Ctrl + Wheel: Adjust opacity
        if modifiers & Qt.KeyboardModifier.ControlModifier:
            step = 0.06 if delta > 0 else -0.06
            self._opacity = max(0.2, min(1.0, self._opacity + step))
            self.setWindowOpacity(self._opacity)
            event.accept()
            return

        if delta == 0:
            return

        # Zoom In / Zoom Out smoothly
        zoom_factor = 1.15 if delta > 0 else 0.87
        new_scale = self.current_scale * zoom_factor
        new_scale = max(self.min_scale, min(self.max_scale, new_scale))

        if abs(new_scale - self.current_scale) > 0.001:
            old_w = self.width()
            old_h = self.height()
            
            self.current_scale = new_scale
            new_w = max(50, int(self.original_pixmap.width() * self.current_scale)) + self._padding * 2
            new_h = max(50, int(self.original_pixmap.height() * self.current_scale)) + self._padding * 2
            
            cursor_glob = QCursor.pos()
            current_pos = self.pos()
            
            # Zoom centered around cursor position
            rel_x = (cursor_glob.x() - current_pos.x()) / float(max(1, old_w))
            rel_y = (cursor_glob.y() - current_pos.y()) / float(max(1, old_h))
            rel_x = max(0.0, min(1.0, rel_x))
            rel_y = max(0.0, min(1.0, rel_y))
            
            delta_w = new_w - old_w
            delta_h = new_h - old_h
            
            self.resize(new_w, new_h)
            self.move(int(current_pos.x() - delta_w * rel_x), int(current_pos.y() - delta_h * rel_y))
            self.update()
            
        event.accept()

    def reset_scale(self):
        """Resets scale back to 100% original size."""
        self.current_scale = 1.0
        old_center = self.geometry().center()
        
        new_w = self.original_pixmap.width() + self._padding * 2
        new_h = self.original_pixmap.height() + self._padding * 2
        
        self.resize(new_w, new_h)
        self.move(old_center.x() - new_w // 2, old_center.y() - new_h // 2)
        self.update()

    def copy_to_clipboard(self):
        """Copies the original high-quality pixmap to Windows clipboard."""
        clipboard = QGuiApplication.clipboard()
        clipboard.setPixmap(self.original_pixmap)

    def save_to_file(self):
        """Opens file dialog to save the pinned image to disk."""
        filepath, _ = QFileDialog.getSaveFileName(
            self,
            "Сохранить скриншот",
            os.path.join(os.path.expanduser("~"), "Desktop", "pinned_snip.png"),
            "PNG Image (*.png);;JPEG Image (*.jpg);;BMP Image (*.bmp)"
        )
        if filepath:
            self.original_pixmap.save(filepath)

    def recognize_ocr(self):
        """Recognizes text from pinned image and copies to clipboard."""
        text = recognize_text_from_pixmap(self.original_pixmap)
        if text:
            clipboard = QGuiApplication.clipboard()
            clipboard.setText(text)
            preview = text.replace('\n', ' ')
            if len(preview) > 28:
                preview = preview[:25] + "..."
            msg = f"✓ Текст скопирован: \"{preview}\""
        else:
            msg = "Текст не обнаружен"
        QToolTip.showText(QCursor.pos(), msg, self, QRect(), 2000)

    def keyPressEvent(self, event):
        if event.key() in (Qt.Key.Key_Escape, Qt.Key.Key_Delete):
            self.close()
        elif event.key() == Qt.Key.Key_C and (event.modifiers() & Qt.KeyboardModifier.ControlModifier):
            self.copy_to_clipboard()
        elif event.key() == Qt.Key.Key_T and (event.modifiers() & Qt.KeyboardModifier.ControlModifier):
            self.recognize_ocr()
        elif event.key() == Qt.Key.Key_S and (event.modifiers() & Qt.KeyboardModifier.ControlModifier):
            self.save_to_file()
        else:
            super().keyPressEvent(event)

    def _show_context_menu(self, pos: QPoint):
        menu = QMenu(self)
        
        act_copy = QAction(draw_icon("copy", "#FFFFFF", 14), "Копировать (Ctrl+C)", self)
        act_copy.triggered.connect(self.copy_to_clipboard)

        act_ocr = QAction(draw_icon("ocr", "#FFFFFF", 14), "Распознать текст OCR (Ctrl+T)", self)
        act_ocr.triggered.connect(self.recognize_ocr)
        
        act_save = QAction(draw_icon("save", "#FFFFFF", 14), "Сохранить... (Ctrl+S)", self)
        act_save.triggered.connect(self.save_to_file)
        
        act_reset = QAction(draw_icon("reset", "#FFFFFF", 14), "Сброс масштаба 100% (2x клик)", self)
        act_reset.triggered.connect(self.reset_scale)
        
        menu.addAction(act_copy)
        menu.addAction(act_ocr)
        menu.addAction(act_save)
        menu.addAction(act_reset)
        menu.addSeparator()
        
        act_close = QAction(draw_icon("close", "#F87171", 14), "Закрыть (Del / Esc)", self)
        act_close.triggered.connect(self.close)
        menu.addAction(act_close)
        
        menu.exec(pos)

    def closeEvent(self, event):
        self.closed.emit(self)
        super().closeEvent(event)
