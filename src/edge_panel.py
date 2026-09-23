"""Unified Samsung Edge Panel widget with attached sliding tab, vertical dragging, and persistent animated tooltips."""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QFrame, QGraphicsOpacityEffect
)
from PyQt6.QtCore import (
    Qt, QPropertyAnimation, QEasingCurve, QPoint, QRectF,
    pyqtSignal, QTimer, QEvent, QObject
)
from PyQt6.QtGui import (
    QPainter, QColor, QPen, QPainterPath, QMouseEvent,
    QGuiApplication, QCursor, QFontMetrics, QFont
)
from .icons import draw_icon
from .autostart import is_autostart_enabled, set_autostart


class InstantBadgeWidget(QWidget):
    """Instant floating tooltip badge with mathematically smooth vector borders and zero corner artifacts."""

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
        
        self.badge_text = ""
        self._font = QFont("Segoe UI", 10)
        self._font.setBold(True)
        
        self.opacity_effect = QGraphicsOpacityEffect(self)
        self.setGraphicsEffect(self.opacity_effect)
        self.opacity_anim = QPropertyAnimation(self.opacity_effect, b"opacity")
        self.opacity_anim.setDuration(120)
        self._current_target = None

    def paintEvent(self, event):
        if not self.badge_text:
            return

        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        painter.setRenderHint(QPainter.RenderHint.TextAntialiasing, True)

        w = float(self.width())
        h = float(self.height())
        rect = QRectF(1.0, 1.0, w - 2.0, h - 2.0)

        # 1. Smooth Rounded Rect Path
        path = QPainterPath()
        path.addRoundedRect(rect, 8.0, 8.0)

        # 2. Fill background
        painter.fillPath(path, QColor(24, 28, 36, 245))

        # 3. Clean vector stroke (no corner dots)
        pen = QPen(QColor(255, 255, 255, 75), 1.2, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap, Qt.PenJoinStyle.RoundJoin)
        painter.setPen(pen)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawPath(path)

        # 4. Text
        painter.setFont(self._font)
        painter.setPen(QColor(245, 247, 250))
        painter.drawText(rect, Qt.AlignmentFlag.AlignCenter, self.badge_text)

        painter.end()

    def show_badge(self, text: str, target_widget: QWidget):
        self._current_target = target_widget
        self.badge_text = text
        
        fm = QFontMetrics(self._font)
        text_w = fm.horizontalAdvance(text)
        badge_w = text_w + 24
        badge_h = 30
        
        self.setFixedSize(badge_w, badge_h)
        
        # Position to the left of the target button
        glob_pos = target_widget.mapToGlobal(QPoint(0, target_widget.height() // 2))
        x = glob_pos.x() - badge_w - 10
        y = glob_pos.y() - badge_h // 2
        
        self.move(x, y)
        self.show()
        self.update()
        
        self.opacity_anim.stop()
        self.opacity_anim.setStartValue(self.opacity_effect.opacity())
        self.opacity_anim.setEndValue(1.0)
        self.opacity_anim.start()

    def hide_badge(self, target_widget: QWidget = None):
        if target_widget is not None and self._current_target != target_widget:
            return
            
        self._current_target = None
        self.opacity_anim.stop()
        self.opacity_anim.setStartValue(self.opacity_effect.opacity())
        self.opacity_anim.setEndValue(0.0)
        self.opacity_anim.start()


class SamsungEdgeUnifiedPanel(QWidget):
    """Unified Edge Panel with attached sliding tab, non-overlapping buttons, and instant tooltips."""

    request_snip = pyqtSignal()
    request_close_all = pyqtSignal()
    request_toggle_pin_visibility = pyqtSignal()
    request_quit = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.setAttribute(Qt.WidgetAttribute.WA_Hover, True)
        self.setMouseTracking(True)

        self.tab_width = 16
        self.drawer_width = 52
        self.total_width = self.tab_width + self.drawer_width  # 68px
        self.panel_height = 290
        
        self.setFixedSize(self.total_width, self.panel_height)
        
        self.is_open = False
        self._dragging_handle = False
        self._drag_start_global = QPoint()
        self._drag_start_y = 0
        self._pinned_count = 0
        self._pins_visible = True
        self._tooltip_map = {}

        # Auto close timer
        self.auto_close_timer = QTimer(self)
        self.auto_close_timer.setSingleShot(True)
        self.auto_close_timer.setInterval(280)
        self.auto_close_timer.timeout.connect(self._check_and_close)

        # Instant animated badge tooltip
        self.badge = InstantBadgeWidget()

        self._init_ui()
        self._position_closed_default()

    def _init_ui(self):
        # Host layout
        host_layout = QHBoxLayout(self)
        host_layout.setContentsMargins(self.tab_width, 0, 0, 0)
        host_layout.setSpacing(0)

        # Drawer container
        self.drawer_container = QWidget(self)
        self.drawer_container.setFixedWidth(self.drawer_width)
        
        layout = QVBoxLayout(self.drawer_container)
        layout.setContentsMargins(6, 12, 6, 12)
        layout.setSpacing(6)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # 1. Snip Button
        self.btn_snip = QPushButton(self.drawer_container)
        self.btn_snip.setProperty("class", "edge-primary-btn")
        self.btn_snip.setFixedSize(36, 36)
        self.btn_snip.setIcon(draw_icon("snip", "#FFFFFF", 18))
        self.btn_snip.setCursor(Qt.CursorShape.PointingHandCursor)
        self._register_tooltip(self.btn_snip, "✂️ Выделить область (Snip)")
        self.btn_snip.clicked.connect(self._on_snip_clicked)
        layout.addWidget(self.btn_snip)

        # Separator
        sep1 = QFrame(self.drawer_container)
        sep1.setFrameShape(QFrame.Shape.HLine)
        sep1.setStyleSheet("background-color: rgba(255, 255, 255, 0.15); max-height: 1px; min-height: 1px;")
        layout.addWidget(sep1)

        # 2. Toggle Pins Visibility
        self.btn_toggle_vis = QPushButton(self.drawer_container)
        self.btn_toggle_vis.setProperty("class", "edge-icon-btn")
        self.btn_toggle_vis.setFixedSize(36, 36)
        self.btn_toggle_vis.setIcon(draw_icon("pin", "#CBD5E1", 16))
        self.btn_toggle_vis.setCursor(Qt.CursorShape.PointingHandCursor)
        self._register_tooltip(self.btn_toggle_vis, "📌 Скрыть / Показать закрепы")
        self.btn_toggle_vis.setEnabled(False)
        self.btn_toggle_vis.clicked.connect(self._on_toggle_vis_clicked)
        layout.addWidget(self.btn_toggle_vis)

        # 3. Clear All Pinned
        self.btn_clear_all = QPushButton(self.drawer_container)
        self.btn_clear_all.setProperty("class", "edge-icon-btn")
        self.btn_clear_all.setFixedSize(36, 36)
        self.btn_clear_all.setIcon(draw_icon("trash", "#CBD5E1", 16))
        self.btn_clear_all.setCursor(Qt.CursorShape.PointingHandCursor)
        self._register_tooltip(self.btn_clear_all, "🗑️ Закрыть все закрепы")
        self.btn_clear_all.setEnabled(False)
        self.btn_clear_all.clicked.connect(self.request_close_all.emit)
        layout.addWidget(self.btn_clear_all)

        # 4. Autostart Toggle
        self.btn_autostart = QPushButton(self.drawer_container)
        self.btn_autostart.setProperty("class", "edge-icon-btn")
        self.btn_autostart.setFixedSize(36, 36)
        self.btn_autostart.setCursor(Qt.CursorShape.PointingHandCursor)
        self._register_tooltip(self.btn_autostart, "🚀 Автозапуск: Включен" if is_autostart_enabled() else "🚀 Автозапуск: Отключен")
        self._update_autostart_badge()
        self.btn_autostart.clicked.connect(self._on_autostart_clicked)
        layout.addWidget(self.btn_autostart)

        # Separator
        sep2 = QFrame(self.drawer_container)
        sep2.setFrameShape(QFrame.Shape.HLine)
        sep2.setStyleSheet("background-color: rgba(255, 255, 255, 0.15); max-height: 1px; min-height: 1px;")
        layout.addWidget(sep2)

        # 5. Quit
        self.btn_quit = QPushButton(self.drawer_container)
        self.btn_quit.setProperty("class", "edge-icon-btn")
        self.btn_quit.setFixedSize(36, 36)
        self.btn_quit.setIcon(draw_icon("close", "#F87171", 14))
        self.btn_quit.setCursor(Qt.CursorShape.PointingHandCursor)
        self._register_tooltip(self.btn_quit, "✖ Выход")
        self.btn_quit.clicked.connect(self.request_quit.emit)
        layout.addWidget(self.btn_quit)

        host_layout.addWidget(self.drawer_container)

    def _register_tooltip(self, widget: QWidget, text: str):
        """Registers a tooltip using eventFilter for reliable hover detection."""
        self._tooltip_map[widget] = text
        widget.installEventFilter(self)

    def eventFilter(self, watched: QObject, event: QEvent) -> bool:
        if watched in self._tooltip_map:
            if event.type() in (QEvent.Type.Enter, QEvent.Type.HoverEnter):
                text = self._tooltip_map[watched]
                self.badge.show_badge(text, watched)
            elif event.type() in (QEvent.Type.Leave, QEvent.Type.HoverLeave):
                self.badge.hide_badge(watched)
        return super().eventFilter(watched, event)

    def _update_autostart_badge(self):
        enabled = is_autostart_enabled()
        text = "🚀 Автозапуск: Включен" if enabled else "🚀 Автозапуск: Отключен"
        self._tooltip_map[self.btn_autostart] = text
        self.btn_autostart.setIcon(draw_icon("autostart", "#60A5FA" if enabled else "#94A3B8", 16))

    def _on_autostart_clicked(self):
        current = is_autostart_enabled()
        set_autostart(not current)
        self._update_autostart_badge()
        text = "🚀 Автозапуск: Включен" if not current else "🚀 Автозапуск: Отключен"
        self.badge.show_badge(text, self.btn_autostart)

    def _on_snip_clicked(self):
        self.badge.hide_badge()
        self.close_panel()
        QTimer.singleShot(160, self.request_snip.emit)

    def _on_toggle_vis_clicked(self):
        self._pins_visible = not self._pins_visible
        txt = "📌 Показать закрепы" if not self._pins_visible else "📌 Скрыть закрепы"
        self._tooltip_map[self.btn_toggle_vis] = txt
        self.badge.show_badge(txt, self.btn_toggle_vis)
        self.request_toggle_pin_visibility.emit()

    def update_pinned_count(self, count: int):
        self._pinned_count = count
        if count == 0:
            self.btn_toggle_vis.setEnabled(False)
            self.btn_clear_all.setEnabled(False)
            self._tooltip_map[self.btn_toggle_vis] = "📌 Нет закрепов"
        else:
            self.btn_toggle_vis.setEnabled(True)
            self.btn_clear_all.setEnabled(True)
            self._tooltip_map[self.btn_toggle_vis] = f"📌 Закрепы ({count} шт.)"

    def _position_closed_default(self):
        screen = QGuiApplication.primaryScreen().geometry()
        x = screen.right() - self.tab_width + 1
        y = screen.height() // 3
        self.move(x, y)
        self.show()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform, True)

        w = float(self.width())
        h = float(self.height())
        tw = float(self.tab_width)
        radius = 16.0
        
        # Main drawer body
        drawer_path = QPainterPath()
        drawer_path.addRoundedRect(QRectF(tw, 0, w - tw + 10, h), radius, radius)
        
        # Tab handle pill
        tab_h = 76.0
        tab_y = (h - tab_h) / 2.0
        tab_path = QPainterPath()
        tab_path.addRoundedRect(QRectF(0, tab_y, tw + 10, tab_h), 8.0, 8.0)

        combined_path = drawer_path.united(tab_path)

        # Fill with frosted acrylic grey
        bg_color = QColor(42, 46, 54, 225)
        painter.fillPath(combined_path, bg_color)

        # Clean anti-aliased border
        border_pen = QPen(QColor(255, 255, 255, 55), 1.2, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap, Qt.PenJoinStyle.RoundJoin)
        painter.setPen(border_pen)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawPath(combined_path)

        # Vertical light grey grip line in the tab handle
        grip_pen = QPen(QColor(255, 255, 255, 180), 2.5, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap)
        painter.setPen(grip_pen)
        painter.drawLine(int(tw / 2) - 1, int(tab_y + 20), int(tw / 2) - 1, int(tab_y + tab_h - 20))

        painter.end()

    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.LeftButton:
            self._dragging_handle = True
            self._drag_start_global = event.globalPosition().toPoint()
            self._drag_start_y = self.y()
            event.accept()

    def mouseMoveEvent(self, event: QMouseEvent):
        if self._dragging_handle and (event.buttons() & Qt.MouseButton.LeftButton):
            cur_glob = event.globalPosition().toPoint()
            delta_x = cur_glob.x() - self._drag_start_global.x()
            delta_y = cur_glob.y() - self._drag_start_global.y()
            
            # Dragging vertically along wall
            screen = QGuiApplication.primaryScreen().geometry()
            new_y = self._drag_start_y + delta_y
            new_y = max(20, min(new_y, screen.height() - self.height() - 20))
            self.move(self.x(), new_y)

            # Swipe left opens panel
            if not self.is_open and delta_x < -10:
                self.open_panel()

            event.accept()
        else:
            if not self.is_open and event.pos().x() < 4:
                self.open_panel()
            super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.LeftButton:
            if self._dragging_handle:
                cur_glob = event.globalPosition().toPoint()
                delta_x = cur_glob.x() - self._drag_start_global.x()
                delta_y = abs(cur_glob.y() - self._drag_start_global.y())
                
                # Click toggle
                if delta_y < 5 and abs(delta_x) < 5:
                    if not self.is_open:
                        self.open_panel()
                    else:
                        self.close_panel()
                        
                self._dragging_handle = False
            event.accept()

    def enterEvent(self, event):
        self.auto_close_timer.stop()
        super().enterEvent(event)

    def leaveEvent(self, event):
        self.badge.hide_badge()
        if self.is_open:
            self.auto_close_timer.start()
        super().leaveEvent(event)

    def _check_and_close(self):
        cursor_pos = QCursor.pos()
        if not self.frameGeometry().contains(cursor_pos):
            self.close_panel()

    def open_panel(self):
        """Slides the entire widget smoothly to the left."""
        if self.is_open:
            return

        screen = QGuiApplication.primaryScreen().geometry()
        target_x = screen.right() - self.total_width + 1

        self.anim = QPropertyAnimation(self, b"pos")
        self.anim.setDuration(200)
        self.anim.setStartValue(self.pos())
        self.anim.setEndValue(QPoint(target_x, self.y()))
        self.anim.setEasingCurve(QEasingCurve.Type.OutCubic)
        self.anim.start()
        
        self.is_open = True
        self.raise_()

    def close_panel(self):
        """Slides the entire widget back into the screen edge."""
        if not self.is_open:
            return

        self.badge.hide_badge()
        screen = QGuiApplication.primaryScreen().geometry()
        target_x = screen.right() - self.tab_width + 1

        self.anim = QPropertyAnimation(self, b"pos")
        self.anim.setDuration(180)
        self.anim.setStartValue(self.pos())
        self.anim.setEndValue(QPoint(target_x, self.y()))
        self.anim.setEasingCurve(QEasingCurve.Type.InCubic)
        self.anim.start()
        
        self.is_open = False


class SamsungEdgeController:
    """Master controller managing the unified Edge Panel and pinned items."""

    def __init__(self, on_snip_callback, on_quit_callback):
        self.on_snip_callback = on_snip_callback
        self.on_quit_callback = on_quit_callback
        self.pinned_widgets = []

        self.panel = SamsungEdgeUnifiedPanel()

        self.panel.request_snip.connect(self.on_snip_callback)
        self.panel.request_close_all.connect(self.close_all_pinned)
        self.panel.request_toggle_pin_visibility.connect(self.toggle_pinned_visibility)
        self.panel.request_quit.connect(self.on_quit_callback)

    def add_pinned_widget(self, widget):
        self.pinned_widgets.append(widget)
        widget.closed.connect(self._on_widget_closed)
        self.panel.update_pinned_count(len(self.pinned_widgets))

    def _on_widget_closed(self, widget):
        if widget in self.pinned_widgets:
            self.pinned_widgets.remove(widget)
            self.panel.update_pinned_count(len(self.pinned_widgets))

    def close_all_pinned(self):
        for w in list(self.pinned_widgets):
            w.close()
        self.pinned_widgets.clear()
        self.panel.update_pinned_count(0)

    def toggle_pinned_visibility(self):
        if not self.pinned_widgets:
            return
        first_visible = self.pinned_widgets[0].isVisible()
        for w in self.pinned_widgets:
            if first_visible:
                w.hide()
            else:
                w.show()

    def show(self):
        self.panel.show()
        self.panel.raise_()

    def hide_to_tray(self):
        self.panel.close_panel()
        self.panel.hide()

    def restore_from_tray(self):
        self.panel.show()
        self.panel.raise_()
