"""Fullscreen Screen Capture Overlay with resizable selection, OCR text grabber, and drawing annotation tools."""

import os
from enum import Enum, auto
import math

from PyQt6.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QPushButton, QLabel, QFileDialog
)
from PyQt6.QtCore import Qt, QRect, QPoint, QPointF, pyqtSignal, QTimer
from PyQt6.QtGui import (
    QPixmap, QPainter, QColor, QPen, QPainterPath, QMouseEvent,
    QKeyEvent, QGuiApplication, QCursor, QFont
)
from .icons import draw_icon
from .ocr import recognize_text_from_pixmap


class DragMode(Enum):
    NONE = auto()
    CREATE = auto()
    MOVE = auto()
    RESIZE_TOP = auto()
    RESIZE_BOTTOM = auto()
    RESIZE_LEFT = auto()
    RESIZE_RIGHT = auto()
    RESIZE_TOP_LEFT = auto()
    RESIZE_TOP_RIGHT = auto()
    RESIZE_BOTTOM_LEFT = auto()
    RESIZE_BOTTOM_RIGHT = auto()


class AnnotateTool(Enum):
    NONE = auto()
    PEN = auto()
    ARROW = auto()
    RECT = auto()
    HIGHLIGHTER = auto()


class AnnotationShape:
    """Represents a vector annotation element drawn on the screen."""
    def __init__(self, tool: AnnotateTool, color: QColor, width: int = 3):
        self.tool = tool
        self.color = color
        self.width = width
        self.points = []  # List of QPoints (relative to selection rect)
        self.start_pt = QPoint()
        self.end_pt = QPoint()


class SnipToastNotification(QWidget):
    """Floating pill notification for OCR or copy feedback."""
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
        
        self.message = ""
        self.timer = QTimer(self)
        self.timer.setSingleShot(True)
        self.timer.timeout.connect(self.hide)

    def show_message(self, text: str, global_center: QPoint, duration: int = 2200):
        self.message = text
        self.setFixedSize(300, 38)
        
        x = global_center.x() - self.width() // 2
        y = global_center.y() - self.height() // 2
        self.move(x, y)
        self.show()
        self.raise_()
        self.update()
        
        self.timer.start(duration)

    def paintEvent(self, event):
        if not self.message:
            return
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        painter.setRenderHint(QPainter.RenderHint.TextAntialiasing, True)

        rect = self.rect().adjusted(1, 1, -1, -1)
        path = QPainterPath()
        path.addRoundedRect(rect.toRectF(), 10.0, 10.0)

        # Background & stroke
        painter.fillPath(path, QColor(24, 28, 36, 245))
        painter.setPen(QPen(QColor(59, 130, 246, 200), 1.5))
        painter.drawPath(path)

        # Text
        painter.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        painter.setPen(QColor("#FFFFFF"))
        painter.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter, self.message)
        painter.end()


class SnippingOverlay(QWidget):
    """Fullscreen dim overlay for selecting, annotating, and OCR-recognizing screen regions."""

    snip_pinned = pyqtSignal(QPixmap, QPoint)  # Emits (pixmap, global_pos)
    snip_canceled = pyqtSignal()

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
        self._desktop_geometry = QRect()

        # Selection state
        self._drag_mode = DragMode.NONE
        self._start_pos = QPoint()
        self._initial_rect = QRect()
        self._selection_rect = QRect()
        self._selection_ready = False
        self._handle_margin = 10

        # Drawing & Annotation state
        self._current_tool = AnnotateTool.NONE
        self._current_color_idx = 0
        self._palette_colors = [
            QColor("#EF4444"),  # Red
            QColor("#3B82F6"),  # Blue
            QColor("#FBBF24"),  # Yellow
            QColor("#10B981")   # Green
        ]
        self._annotations = []  # List of AnnotationShape
        self._current_drawing_shape = None

        # Toast notification
        self.toast = SnipToastNotification()

        self._init_action_bar()

    def _init_action_bar(self):
        """Floating action bar with primary actions and drawing tools."""
        self.action_bar = QWidget(self)
        self.action_bar.setObjectName("SnipActionBar")
        self.action_bar.setCursor(Qt.CursorShape.ArrowCursor)
        
        main_layout = QVBoxLayout(self.action_bar)
        main_layout.setContentsMargins(6, 6, 6, 6)
        main_layout.setSpacing(6)

        # Top row: Primary actions (Pin, Copy, OCR, Save, Cancel)
        top_row = QHBoxLayout()
        top_row.setSpacing(6)

        self.lbl_size = QLabel(self.action_bar)
        self.lbl_size.setStyleSheet("color: #94A3B8; font-size: 11px; padding: 0 4px;")
        self.lbl_size.setCursor(Qt.CursorShape.ArrowCursor)
        top_row.addWidget(self.lbl_size)

        # Pin (Primary)
        self.btn_pin = QPushButton(" Закрепить", self.action_bar)
        self.btn_pin.setProperty("class", "primary-btn")
        self.btn_pin.setIcon(draw_icon("pin", "#FFFFFF", 16))
        self.btn_pin.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_pin.setToolTip("Закрепить поверх окон (Enter / Пробел)")
        self.btn_pin.clicked.connect(self._action_pin)
        top_row.addWidget(self.btn_pin)

        # OCR Text recognition
        self.btn_ocr = QPushButton(" 📝 Текст (OCR)", self.action_bar)
        self.btn_ocr.setProperty("class", "secondary-btn")
        self.btn_ocr.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_ocr.setToolTip("Распознать и скопировать текст с изображения")
        self.btn_ocr.clicked.connect(self._action_ocr)
        top_row.addWidget(self.btn_ocr)

        # Copy
        self.btn_copy = QPushButton(" Копировать", self.action_bar)
        self.btn_copy.setProperty("class", "secondary-btn")
        self.btn_copy.setIcon(draw_icon("copy", "#F1F5F9", 16))
        self.btn_copy.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_copy.setToolTip("Скопировать в буфер (Ctrl+C)")
        self.btn_copy.clicked.connect(self._action_copy)
        top_row.addWidget(self.btn_copy)

        # Save
        self.btn_save = QPushButton(" Сохранить", self.action_bar)
        self.btn_save.setProperty("class", "secondary-btn")
        self.btn_save.setIcon(draw_icon("save", "#F1F5F9", 16))
        self.btn_save.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_save.setToolTip("Сохранить файл (Ctrl+S)")
        self.btn_save.clicked.connect(self._action_save)
        top_row.addWidget(self.btn_save)

        # Cancel
        self.btn_cancel = QPushButton(self.action_bar)
        self.btn_cancel.setProperty("class", "danger-icon-btn")
        self.btn_cancel.setIcon(draw_icon("close", "#F87171", 16))
        self.btn_cancel.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_cancel.setToolTip("Отмена (Esc)")
        self.btn_cancel.clicked.connect(self._action_cancel)
        top_row.addWidget(self.btn_cancel)

        main_layout.addLayout(top_row)

        # Bottom row: Drawing tools (Pen, Arrow, Rect, Highlighter, Color Swatch, Undo)
        bot_row = QHBoxLayout()
        bot_row.setSpacing(6)

        # Drawing Tool Buttons
        self.btn_tool_pen = QPushButton(self.action_bar)
        self.btn_tool_pen.setProperty("class", "secondary-btn")
        self.btn_tool_pen.setIcon(draw_icon("pen", "#E2E8F0", 16))
        self.btn_tool_pen.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_tool_pen.setToolTip("Карандаш (Рисование)")
        self.btn_tool_pen.clicked.connect(lambda: self._set_tool(AnnotateTool.PEN))
        bot_row.addWidget(self.btn_tool_pen)

        self.btn_tool_arrow = QPushButton(self.action_bar)
        self.btn_tool_arrow.setProperty("class", "secondary-btn")
        self.btn_tool_arrow.setIcon(draw_icon("arrow", "#E2E8F0", 16))
        self.btn_tool_arrow.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_tool_arrow.setToolTip("Стрелочка")
        self.btn_tool_arrow.clicked.connect(lambda: self._set_tool(AnnotateTool.ARROW))
        bot_row.addWidget(self.btn_tool_arrow)

        self.btn_tool_rect = QPushButton(self.action_bar)
        self.btn_tool_rect.setProperty("class", "secondary-btn")
        self.btn_tool_rect.setIcon(draw_icon("rect", "#E2E8F0", 16))
        self.btn_tool_rect.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_tool_rect.setToolTip("Рамка / Прямоугольник")
        self.btn_tool_rect.clicked.connect(lambda: self._set_tool(AnnotateTool.RECT))
        bot_row.addWidget(self.btn_tool_rect)

        self.btn_tool_highlighter = QPushButton(self.action_bar)
        self.btn_tool_highlighter.setProperty("class", "secondary-btn")
        self.btn_tool_highlighter.setIcon(draw_icon("highlighter", "#E2E8F0", 16))
        self.btn_tool_highlighter.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_tool_highlighter.setToolTip("Маркер-хайлайтер")
        self.btn_tool_highlighter.clicked.connect(lambda: self._set_tool(AnnotateTool.HIGHLIGHTER))
        bot_row.addWidget(self.btn_tool_highlighter)

        # Color picker toggle
        self.btn_color_toggle = QPushButton(" 🎨 Цвет", self.action_bar)
        self.btn_color_toggle.setProperty("class", "secondary-btn")
        self.btn_color_toggle.setCursor(Qt.CursorShape.PointingHandCursor)
        self._update_color_button_style()
        self.btn_color_toggle.clicked.connect(self._cycle_color)
        bot_row.addWidget(self.btn_color_toggle)

        # Undo button
        self.btn_undo = QPushButton(self.action_bar)
        self.btn_undo.setProperty("class", "secondary-btn")
        self.btn_undo.setIcon(draw_icon("undo", "#E2E8F0", 16))
        self.btn_undo.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_undo.setToolTip("Отменить рисование (Ctrl+Z)")
        self.btn_undo.clicked.connect(self._undo_annotation)
        bot_row.addWidget(self.btn_undo)

        bot_row.addStretch()
        main_layout.addLayout(bot_row)

        self.action_bar.adjustSize()
        self.action_bar.hide()

    def _set_tool(self, tool: AnnotateTool):
        if self._current_tool == tool:
            self._current_tool = AnnotateTool.NONE  # Toggle off back to select
        else:
            self._current_tool = tool
        self._update_tool_buttons_style()
        self._update_cursor_for_pos(self.mapFromGlobal(QCursor.pos()))

    def _update_tool_buttons_style(self):
        self.btn_tool_pen.setStyleSheet("background-color: #2563EB;" if self._current_tool == AnnotateTool.PEN else "")
        self.btn_tool_arrow.setStyleSheet("background-color: #2563EB;" if self._current_tool == AnnotateTool.ARROW else "")
        self.btn_tool_rect.setStyleSheet("background-color: #2563EB;" if self._current_tool == AnnotateTool.RECT else "")
        self.btn_tool_highlighter.setStyleSheet("background-color: #2563EB;" if self._current_tool == AnnotateTool.HIGHLIGHTER else "")

    def _cycle_color(self):
        self._current_color_idx = (self._current_color_idx + 1) % len(self._palette_colors)
        self._update_color_button_style()

    def _update_color_button_style(self):
        cur_col = self._palette_colors[self._current_color_idx]
        self.btn_color_toggle.setStyleSheet(f"color: {cur_col.name()}; font-weight: bold; border-color: {cur_col.name()};")

    def _undo_annotation(self):
        if self._annotations:
            self._annotations.pop()
            self.update()

    def start_capture(self):
        """Captures entire virtual desktop across all connected monitors."""
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

        self._drag_mode = DragMode.NONE
        self._selection_ready = False
        self._selection_rect = QRect()
        self._annotations.clear()
        self._current_tool = AnnotateTool.NONE
        self._update_tool_buttons_style()
        self.action_bar.hide()

        self.setGeometry(self._desktop_geometry)
        self.showFullScreen()
        self.raise_()
        self.activateWindow()

    def _get_hit_test_mode(self, pos: QPoint) -> DragMode:
        """Determines if cursor is over a corner, edge, or interior of selection."""
        if not self._selection_ready or self._selection_rect.isEmpty():
            return DragMode.NONE

        r = self._selection_rect
        m = self._handle_margin

        # Corners
        tl = QRect(r.left() - m, r.top() - m, 2 * m, 2 * m)
        tr = QRect(r.right() - m, r.top() - m, 2 * m, 2 * m)
        bl = QRect(r.left() - m, r.bottom() - m, 2 * m, 2 * m)
        br = QRect(r.right() - m, r.bottom() - m, 2 * m, 2 * m)

        if tl.contains(pos):
            return DragMode.RESIZE_TOP_LEFT
        if tr.contains(pos):
            return DragMode.RESIZE_TOP_RIGHT
        if bl.contains(pos):
            return DragMode.RESIZE_BOTTOM_LEFT
        if br.contains(pos):
            return DragMode.RESIZE_BOTTOM_RIGHT

        # Edges
        top_edge = QRect(r.left() + m, r.top() - m, r.width() - 2 * m, 2 * m)
        bottom_edge = QRect(r.left() + m, r.bottom() - m, r.width() - 2 * m, 2 * m)
        left_edge = QRect(r.left() - m, r.top() + m, 2 * m, r.height() - 2 * m)
        right_edge = QRect(r.right() - m, r.top() + m, 2 * m, r.height() - 2 * m)

        if top_edge.contains(pos):
            return DragMode.RESIZE_TOP
        if bottom_edge.contains(pos):
            return DragMode.RESIZE_BOTTOM
        if left_edge.contains(pos):
            return DragMode.RESIZE_LEFT
        if right_edge.contains(pos):
            return DragMode.RESIZE_RIGHT

        # Interior
        if r.contains(pos):
            return DragMode.MOVE

        return DragMode.NONE

    def _update_cursor_for_pos(self, pos: QPoint):
        if self.action_bar.isVisible() and self.action_bar.geometry().contains(pos):
            self.setCursor(Qt.CursorShape.ArrowCursor)
            return

        # If drawing tool is active and cursor is inside selection, show standard arrow cursor
        if self._selection_ready and self._current_tool != AnnotateTool.NONE and self._selection_rect.contains(pos):
            self.setCursor(Qt.CursorShape.ArrowCursor)
            return

        mode = self._get_hit_test_mode(pos)
        if mode in (DragMode.RESIZE_TOP_LEFT, DragMode.RESIZE_BOTTOM_RIGHT):
            self.setCursor(Qt.CursorShape.SizeFDiagCursor)
        elif mode in (DragMode.RESIZE_TOP_RIGHT, DragMode.RESIZE_BOTTOM_LEFT):
            self.setCursor(Qt.CursorShape.SizeBDiagCursor)
        elif mode in (DragMode.RESIZE_TOP, DragMode.RESIZE_BOTTOM):
            self.setCursor(Qt.CursorShape.SizeVerCursor)
        elif mode in (DragMode.RESIZE_LEFT, DragMode.RESIZE_RIGHT):
            self.setCursor(Qt.CursorShape.SizeHorCursor)
        elif mode == DragMode.MOVE:
            self.setCursor(Qt.CursorShape.SizeAllCursor)
        else:
            self.setCursor(Qt.CursorShape.CrossCursor)

    def _get_rendered_snip_pixmap(self) -> QPixmap:
        """Returns the cropped pixmap with all vector annotations painted onto it."""
        if not self.background_pixmap or self._selection_rect.isEmpty():
            return QPixmap()
        
        dpr = self.devicePixelRatio()
        crop_rect = QRect(
            int(self._selection_rect.x() * dpr),
            int(self._selection_rect.y() * dpr),
            int(self._selection_rect.width() * dpr),
            int(self._selection_rect.height() * dpr)
        )
        base_pixmap = self.background_pixmap.copy(crop_rect)

        # If annotations exist, paint them onto base pixmap
        if self._annotations:
            painter = QPainter(base_pixmap)
            painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
            painter.scale(dpr, dpr)

            for shape in self._annotations:
                self._draw_shape(painter, shape)

            painter.end()

        return base_pixmap

    def _draw_shape(self, painter: QPainter, shape: AnnotationShape):
        """Draws a single annotation shape (relative to selection coordinates)."""
        color = shape.color
        if shape.tool == AnnotateTool.HIGHLIGHTER:
            hl_color = QColor(color.red(), color.green(), color.blue(), 100)
            pen = QPen(hl_color, 14, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap, Qt.PenJoinStyle.RoundJoin)
            painter.setPen(pen)
            painter.setBrush(Qt.BrushStyle.NoBrush)
            if len(shape.points) > 1:
                path = QPainterPath()
                path.moveTo(QPointF(shape.points[0]))
                for pt in shape.points[1:]:
                    path.lineTo(QPointF(pt))
                painter.drawPath(path)

        elif shape.tool == AnnotateTool.PEN:
            pen = QPen(color, shape.width, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap, Qt.PenJoinStyle.RoundJoin)
            painter.setPen(pen)
            painter.setBrush(Qt.BrushStyle.NoBrush)
            if len(shape.points) > 1:
                path = QPainterPath()
                path.moveTo(QPointF(shape.points[0]))
                for pt in shape.points[1:]:
                    path.lineTo(QPointF(pt))
                painter.drawPath(path)

        elif shape.tool == AnnotateTool.RECT:
            pen = QPen(color, shape.width, Qt.PenStyle.SolidLine)
            painter.setPen(pen)
            painter.setBrush(Qt.BrushStyle.NoBrush)
            rect = QRect(shape.start_pt, shape.end_pt).normalized()
            painter.drawRect(rect)

        elif shape.tool == AnnotateTool.ARROW:
            pen = QPen(color, shape.width, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap)
            painter.setPen(pen)
            painter.setBrush(color)

            p1 = QPointF(shape.start_pt)
            p2 = QPointF(shape.end_pt)
            painter.drawLine(p1.toPoint(), p2.toPoint())

            # Draw Arrowhead
            angle = math.atan2(p2.y() - p1.y(), p2.x() - p1.x())
            arrow_size = 14.0
            arrow_angle = math.pi / 6.0  # 30 deg

            p_arrow1 = QPointF(
                p2.x() - arrow_size * math.cos(angle - arrow_angle),
                p2.y() - arrow_size * math.sin(angle - arrow_angle)
            )
            p_arrow2 = QPointF(
                p2.x() - arrow_size * math.cos(angle + arrow_angle),
                p2.y() - arrow_size * math.sin(angle + arrow_angle)
            )

            head_path = QPainterPath()
            head_path.moveTo(p2)
            head_path.lineTo(p_arrow1)
            head_path.lineTo(p_arrow2)
            head_path.closeSubpath()
            painter.drawPath(head_path)

    def _action_pin(self):
        snip = self._get_rendered_snip_pixmap()
        if not snip.isNull() and snip.width() > 5 and snip.height() > 5:
            global_pos = self.mapToGlobal(self._selection_rect.topLeft())
            self.snip_pinned.emit(snip, global_pos)
        self.close()

    def _action_ocr(self):
        """Runs OCR on the current selection and copies recognized text to clipboard."""
        snip = self._get_rendered_snip_pixmap()
        if not snip.isNull():
            text = recognize_text_from_pixmap(snip)
            if text:
                clipboard = QGuiApplication.clipboard()
                clipboard.setText(text)
                preview = text.replace('\n', ' ')
                if len(preview) > 28:
                    preview = preview[:25] + "..."
                msg = f"✓ Текст скопирован: \"{preview}\""
            else:
                msg = "Текст не обнаружен на вырезке"

            # Display floating toast
            center = self.mapToGlobal(self._selection_rect.center())
            self.toast.show_message(msg, center)
            QTimer.singleShot(1400, self.close)

    def _action_copy(self):
        snip = self._get_rendered_snip_pixmap()
        if not snip.isNull():
            clipboard = QGuiApplication.clipboard()
            clipboard.setPixmap(snip)
        self.close()

    def _action_save(self):
        snip = self._get_rendered_snip_pixmap()
        if not snip.isNull():
            self.hide()
            filepath, _ = QFileDialog.getSaveFileName(
                None,
                "Сохранить скриншот",
                os.path.join(os.path.expanduser("~"), "Desktop", "snip.png"),
                "PNG Image (*.png);;JPEG Image (*.jpg);;BMP Image (*.bmp)"
            )
            if filepath:
                snip.save(filepath)
        self.close()

    def _action_cancel(self):
        self.snip_canceled.emit()
        self.close()

    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.LeftButton:
            pos = event.pos()
            
            # Click inside action bar
            if self.action_bar.isVisible() and self.action_bar.geometry().contains(pos):
                super().mousePressEvent(event)
                return

            # Drawing tool mode active inside selection
            if self._selection_ready and self._current_tool != AnnotateTool.NONE and self._selection_rect.contains(pos):
                self.setCursor(Qt.CursorShape.ArrowCursor)
                rel_pos = pos - self._selection_rect.topLeft()
                color = self._palette_colors[self._current_color_idx]
                width = 3 if self._current_tool != AnnotateTool.HIGHLIGHTER else 14
                
                self._current_drawing_shape = AnnotationShape(self._current_tool, color, width)
                self._current_drawing_shape.start_pt = rel_pos
                self._current_drawing_shape.end_pt = rel_pos
                self._current_drawing_shape.points.append(rel_pos)
                self._annotations.append(self._current_drawing_shape)
                self.update()
                return

            mode = self._get_hit_test_mode(pos)
            self._start_pos = pos
            self._initial_rect = QRect(self._selection_rect)

            if mode != DragMode.NONE:
                self._drag_mode = mode
                self.action_bar.hide()
            else:
                self._drag_mode = DragMode.CREATE
                self._selection_ready = False
                self._annotations.clear()
                self._current_tool = AnnotateTool.NONE
                self._update_tool_buttons_style()
                self.action_bar.hide()
                self._selection_rect = QRect(pos, pos)
                self.update()

        elif event.button() == Qt.MouseButton.RightButton:
            if self._selection_ready:
                self._selection_ready = False
                self._selection_rect = QRect()
                self._annotations.clear()
                self.action_bar.hide()
                self.setCursor(Qt.CursorShape.CrossCursor)
                self.update()
            else:
                self._action_cancel()

    def mouseMoveEvent(self, event: QMouseEvent):
        pos = event.pos()

        # If currently drawing a shape
        if self._current_drawing_shape is not None:
            self.setCursor(Qt.CursorShape.ArrowCursor)
            rel_pos = pos - self._selection_rect.topLeft()
            self._current_drawing_shape.end_pt = rel_pos
            if self._current_tool in (AnnotateTool.PEN, AnnotateTool.HIGHLIGHTER):
                self._current_drawing_shape.points.append(rel_pos)
            self.update()
            return

        if self._drag_mode == DragMode.NONE:
            self._update_cursor_for_pos(pos)
            return

        dx = pos.x() - self._start_pos.x()
        dy = pos.y() - self._start_pos.y()
        init = self._initial_rect

        if self._drag_mode == DragMode.CREATE:
            self._selection_rect = QRect(self._start_pos, pos).normalized()
            
        elif self._drag_mode == DragMode.MOVE:
            new_r = QRect(init)
            new_r.translate(dx, dy)
            self._selection_rect = new_r
            
        elif self._drag_mode == DragMode.RESIZE_LEFT:
            new_left = min(init.right() - 10, init.left() + dx)
            self._selection_rect = QRect(new_left, init.top(), init.right() - new_left, init.height())
            
        elif self._drag_mode == DragMode.RESIZE_RIGHT:
            new_right = max(init.left() + 10, init.right() + dx)
            self._selection_rect = QRect(init.left(), init.top(), new_right - init.left(), init.height())
            
        elif self._drag_mode == DragMode.RESIZE_TOP:
            new_top = min(init.bottom() - 10, init.top() + dy)
            self._selection_rect = QRect(init.left(), new_top, init.width(), init.bottom() - new_top)
            
        elif self._drag_mode == DragMode.RESIZE_BOTTOM:
            new_bottom = max(init.top() + 10, init.bottom() + dy)
            self._selection_rect = QRect(init.left(), init.top(), init.width(), new_bottom - init.top())
            
        elif self._drag_mode == DragMode.RESIZE_TOP_LEFT:
            new_left = min(init.right() - 10, init.left() + dx)
            new_top = min(init.bottom() - 10, init.top() + dy)
            self._selection_rect = QRect(new_left, new_top, init.right() - new_left, init.bottom() - new_top)
            
        elif self._drag_mode == DragMode.RESIZE_TOP_RIGHT:
            new_right = max(init.left() + 10, init.right() + dx)
            new_top = min(init.bottom() - 10, init.top() + dy)
            self._selection_rect = QRect(init.left(), new_top, new_right - init.left(), init.bottom() - new_top)
            
        elif self._drag_mode == DragMode.RESIZE_BOTTOM_LEFT:
            new_left = min(init.right() - 10, init.left() + dx)
            new_bottom = max(init.top() + 10, init.bottom() + dy)
            self._selection_rect = QRect(new_left, init.top(), init.right() - new_left, new_bottom - init.top())
            
        elif self._drag_mode == DragMode.RESIZE_BOTTOM_RIGHT:
            new_right = max(init.left() + 10, init.right() + dx)
            new_bottom = max(init.top() + 10, init.bottom() + dy)
            self._selection_rect = QRect(init.left(), init.top(), new_right - init.left(), new_bottom - init.top())

        self.update()

    def mouseReleaseEvent(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.LeftButton:
            if self._current_drawing_shape is not None:
                self._current_drawing_shape = None
                self.update()
                return

            self._drag_mode = DragMode.NONE
            
            if self._selection_rect.width() > 10 and self._selection_rect.height() > 10:
                self._selection_ready = True
                self._position_action_bar()
            else:
                self._selection_ready = False
                self.action_bar.hide()

            self._update_cursor_for_pos(event.pos())
            self.update()

    def _position_action_bar(self):
        """Positions action bar right below selection rect, or above if near screen bottom."""
        self.lbl_size.setText(f"{self._selection_rect.width()} × {self._selection_rect.height()} px")
        self.action_bar.adjustSize()
        
        bar_w = self.action_bar.width()
        bar_h = self.action_bar.height()
        
        x = self._selection_rect.x() + (self._selection_rect.width() - bar_w) // 2
        x = max(10, min(x, self.width() - bar_w - 10))
        
        y = self._selection_rect.bottom() + 12
        if y + bar_h > self.height() - 10:
            y = self._selection_rect.top() - bar_h - 12
            if y < 10:
                y = self._selection_rect.top() + 10
                
        self.action_bar.move(x, y)
        self.action_bar.show()
        self.action_bar.raise_()

    def paintEvent(self, event):
        if not self.background_pixmap:
            return

        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        
        # 1. Background capture
        painter.drawPixmap(0, 0, self.background_pixmap)
        
        # 2. Dim overlay
        painter.fillRect(self.rect(), QColor(0, 0, 0, 130))
        
        # 3. Bright selected region + Vector annotations
        if not self._selection_rect.isEmpty():
            dpr = self.devicePixelRatio()
            crop_rect = QRect(
                int(self._selection_rect.x() * dpr),
                int(self._selection_rect.y() * dpr),
                int(self._selection_rect.width() * dpr),
                int(self._selection_rect.height() * dpr)
            )
            sub_pix = self.background_pixmap.copy(crop_rect)
            painter.drawPixmap(self._selection_rect, sub_pix)

            # Draw annotations translated to selection position
            if self._annotations:
                painter.save()
                painter.translate(self._selection_rect.topLeft())
                painter.setClipRect(QRect(0, 0, self._selection_rect.width(), self._selection_rect.height()))
                for shape in self._annotations:
                    self._draw_shape(painter, shape)
                painter.restore()
            
            # Glowing blue border
            border_pen = QPen(QColor("#3B82F6"), 2, Qt.PenStyle.SolidLine)
            painter.setPen(border_pen)
            painter.setBrush(Qt.BrushStyle.NoBrush)
            painter.drawRect(self._selection_rect)
            
            # 8 Handle grips (when not currently drawing)
            if self._selection_ready and self._current_tool == AnnotateTool.NONE:
                r = self._selection_rect
                handle_color = QColor("#FFFFFF")
                handle_pen = QPen(QColor("#2563EB"), 1.5)
                painter.setPen(handle_pen)
                painter.setBrush(handle_color)

                h_size = 7
                points = [
                    QPoint(r.left(), r.top()),                            # TL
                    QPoint(r.center().x(), r.top()),                     # T
                    QPoint(r.right(), r.top()),                           # TR
                    QPoint(r.right(), r.center().y()),                   # R
                    QPoint(r.right(), r.bottom()),                        # BR
                    QPoint(r.center().x(), r.bottom()),                  # B
                    QPoint(r.left(), r.bottom()),                         # BL
                    QPoint(r.left(), r.center().y()),                    # L
                ]
                for p in points:
                    painter.drawEllipse(p, h_size // 2, h_size // 2)

        painter.end()

    def keyPressEvent(self, event: QKeyEvent):
        key = event.key()
        modifiers = event.modifiers()
        
        if key == Qt.Key.Key_Escape:
            self._action_cancel()
        elif key in (Qt.Key.Key_Return, Qt.Key.Key_Enter, Qt.Key.Key_Space):
            if self._selection_ready:
                self._action_pin()
        elif key == Qt.Key.Key_Z and (modifiers & Qt.KeyboardModifier.ControlModifier):
            self._undo_annotation()
        elif key == Qt.Key.Key_C and (modifiers & Qt.KeyboardModifier.ControlModifier):
            if self._selection_ready:
                self._action_copy()
        elif key == Qt.Key.Key_S and (modifiers & Qt.KeyboardModifier.ControlModifier):
            if self._selection_ready:
                self._action_save()
        else:
            super().keyPressEvent(event)
