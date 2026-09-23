"""Fullscreen Screen Capture Overlay with resizable selection handles and intuitive cursors."""

import os
from enum import Enum, auto

from PyQt6.QtWidgets import (
    QWidget, QHBoxLayout, QPushButton, QLabel, QFileDialog
)
from PyQt6.QtCore import Qt, QRect, QPoint, pyqtSignal
from PyQt6.QtGui import (
    QPixmap, QPainter, QColor, QPen, QMouseEvent,
    QKeyEvent, QGuiApplication, QCursor
)
from .icons import draw_icon


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


class SnippingOverlay(QWidget):
    """Fullscreen dim overlay for selecting and adjusting a screen region."""

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
        
        self._handle_margin = 10  # Hitbox radius for resizing edges/corners

        self._init_action_bar()

    def _init_action_bar(self):
        """Floating action bar that appears once a selection is made."""
        self.action_bar = QWidget(self)
        self.action_bar.setObjectName("SnipActionBar")
        self.action_bar.setCursor(Qt.CursorShape.ArrowCursor)  # Normal arrow cursor over bar
        
        layout = QHBoxLayout(self.action_bar)
        layout.setContentsMargins(8, 6, 8, 6)
        layout.setSpacing(8)

        # Size label
        self.lbl_size = QLabel(self.action_bar)
        self.lbl_size.setStyleSheet("color: #94A3B8; font-size: 11px; padding: 0 4px;")
        self.lbl_size.setCursor(Qt.CursorShape.ArrowCursor)
        layout.addWidget(self.lbl_size)

        # Pin button (Primary)
        self.btn_pin = QPushButton(" Закрепить", self.action_bar)
        self.btn_pin.setProperty("class", "primary-btn")
        self.btn_pin.setIcon(draw_icon("pin", "#FFFFFF", 16))
        self.btn_pin.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_pin.setToolTip("Закрепить вырезку поверх окон (Enter / Пробел)")
        self.btn_pin.clicked.connect(self._action_pin)
        layout.addWidget(self.btn_pin)

        # Copy button
        self.btn_copy = QPushButton(" Копировать", self.action_bar)
        self.btn_copy.setProperty("class", "secondary-btn")
        self.btn_copy.setIcon(draw_icon("copy", "#F1F5F9", 16))
        self.btn_copy.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_copy.setToolTip("Скопировать в буфер (Ctrl+C)")
        self.btn_copy.clicked.connect(self._action_copy)
        layout.addWidget(self.btn_copy)

        # Save button
        self.btn_save = QPushButton(" Сохранить", self.action_bar)
        self.btn_save.setProperty("class", "secondary-btn")
        self.btn_save.setIcon(draw_icon("save", "#F1F5F9", 16))
        self.btn_save.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_save.setToolTip("Сохранить в файл (Ctrl+S)")
        self.btn_save.clicked.connect(self._action_save)
        layout.addWidget(self.btn_save)

        # Cancel button
        self.btn_cancel = QPushButton(self.action_bar)
        self.btn_cancel.setProperty("class", "danger-icon-btn")
        self.btn_cancel.setIcon(draw_icon("close", "#F87171", 16))
        self.btn_cancel.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_cancel.setToolTip("Отмена (Esc)")
        self.btn_cancel.clicked.connect(self._action_cancel)
        layout.addWidget(self.btn_cancel)

        self.action_bar.adjustSize()
        self.action_bar.hide()

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
        """Sets intuitive cursor depending on mouse position."""
        if self.action_bar.isVisible() and self.action_bar.geometry().contains(pos):
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

    def _get_current_snip_pixmap(self) -> QPixmap:
        """Crops the selected region from background pixmap."""
        if not self.background_pixmap or self._selection_rect.isEmpty():
            return QPixmap()
        
        dpr = self.devicePixelRatio()
        crop_rect = QRect(
            int(self._selection_rect.x() * dpr),
            int(self._selection_rect.y() * dpr),
            int(self._selection_rect.width() * dpr),
            int(self._selection_rect.height() * dpr)
        )
        return self.background_pixmap.copy(crop_rect)

    def _action_pin(self):
        snip = self._get_current_snip_pixmap()
        if not snip.isNull() and snip.width() > 5 and snip.height() > 5:
            global_pos = self.mapToGlobal(self._selection_rect.topLeft())
            self.snip_pinned.emit(snip, global_pos)
        self.close()

    def _action_copy(self):
        snip = self._get_current_snip_pixmap()
        if not snip.isNull():
            clipboard = QGuiApplication.clipboard()
            clipboard.setPixmap(snip)
        self.close()

    def _action_save(self):
        snip = self._get_current_snip_pixmap()
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
            
            # Check if clicked on action bar
            if self.action_bar.isVisible() and self.action_bar.geometry().contains(pos):
                super().mousePressEvent(event)
                return

            mode = self._get_hit_test_mode(pos)
            self._start_pos = pos
            self._initial_rect = QRect(self._selection_rect)

            if mode != DragMode.NONE:
                self._drag_mode = mode
                self.action_bar.hide()
            else:
                # Start fresh selection
                self._drag_mode = DragMode.CREATE
                self._selection_ready = False
                self.action_bar.hide()
                self._selection_rect = QRect(pos, pos)
                self.update()

        elif event.button() == Qt.MouseButton.RightButton:
            if self._selection_ready:
                self._selection_ready = False
                self._selection_rect = QRect()
                self.action_bar.hide()
                self.setCursor(Qt.CursorShape.CrossCursor)
                self.update()
            else:
                self._action_cancel()

    def mouseMoveEvent(self, event: QMouseEvent):
        pos = event.pos()
        
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
        
        # Center horizontally
        x = self._selection_rect.x() + (self._selection_rect.width() - bar_w) // 2
        x = max(10, min(x, self.width() - bar_w - 10))
        
        # Below selection if fits
        y = self._selection_rect.bottom() + 12
        if y + bar_h > self.height() - 10:
            # Place above selection
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
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # 1. Draw desktop capture
        painter.drawPixmap(0, 0, self.background_pixmap)
        
        # 2. Draw dark translucent overlay
        painter.fillRect(self.rect(), QColor(0, 0, 0, 130))
        
        # 3. If area selected, restore bright original pixels inside rect
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
            
            # Glowing blue border
            border_pen = QPen(QColor("#3B82F6"), 2, Qt.PenStyle.SolidLine)
            painter.setPen(border_pen)
            painter.setBrush(Qt.BrushStyle.NoBrush)
            painter.drawRect(self._selection_rect)
            
            # Corner and edge resize handle grips
            if self._selection_ready:
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
        elif key == Qt.Key.Key_C and (modifiers & Qt.KeyboardModifier.ControlModifier):
            if self._selection_ready:
                self._action_copy()
        elif key == Qt.Key.Key_S and (modifiers & Qt.KeyboardModifier.ControlModifier):
            if self._selection_ready:
                self._action_save()
        else:
            super().keyPressEvent(event)
