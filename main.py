"""Samsung Edge Screen Snip & Pin Application.

Main entry point for the desktop application.
Features:
- Samsung Edge style sliding sidebar on the right edge of the screen
- Snip & Pin screen regions that stay always on top of all windows
- Smooth zoom with mouse wheel, drag & drop repositioning, resize
- Copy to clipboard, save to file, opacity adjustment
- Windows Autostart integration
- System tray minimization
"""

import sys
import ctypes

from PyQt6.QtWidgets import (
    QApplication, QSystemTrayIcon, QMenu
)
from PyQt6.QtCore import Qt, QPoint
from PyQt6.QtGui import QAction, QPixmap

from src.styles import DARK_THEME_QSS
from src.icons import create_app_icon, draw_icon
from src.edge_panel import SamsungEdgeController
from src.snipping_tool import SnippingOverlay
from src.pinned_overlay import PinnedImageWidget
from src.autostart import is_autostart_enabled, set_autostart


class AppController:
    """Master Application Controller coordinating Tray, Edge Panel, Snip and Pinned Cards."""

    def __init__(self, app: QApplication):
        self.app = app
        self.app.setStyleSheet(DARK_THEME_QSS)

        # Snipping overlay instance
        self.snip_overlay = None

        # Edge panel controller
        self.edge_controller = SamsungEdgeController(
            on_snip_callback=self.trigger_snip,
            on_quit_callback=self.quit_app
        )

        # System tray icon setup
        self._init_tray()

    def _init_tray(self):
        """Initializes the Windows System Tray Icon."""
        if not QSystemTrayIcon.isSystemTrayAvailable():
            return

        self.tray_icon = QSystemTrayIcon(create_app_icon(32), self.app)
        self.tray_icon.setToolTip("Samsung Edge Screen Snip & Pin")

        tray_menu = QMenu()
        
        # Snip action
        act_snip = QAction(draw_icon("snip", "#FFFFFF", 16), "Выделить область (Snip)", tray_menu)
        act_snip.triggered.connect(self.trigger_snip)
        tray_menu.addAction(act_snip)

        # Toggle Edge Handle action
        self.act_toggle_handle = QAction("Показать шторку Edge", tray_menu)
        self.act_toggle_handle.setCheckable(True)
        self.act_toggle_handle.setChecked(True)
        self.act_toggle_handle.triggered.connect(self._toggle_edge_handle)
        tray_menu.addAction(self.act_toggle_handle)

        tray_menu.addSeparator()

        # Autostart toggle
        self.act_autostart = QAction("Автозапуск при старте Windows", tray_menu)
        self.act_autostart.setCheckable(True)
        self.act_autostart.setChecked(is_autostart_enabled())
        self.act_autostart.triggered.connect(self._toggle_autostart)
        tray_menu.addAction(self.act_autostart)

        # Close all pinned
        act_close_all = QAction(draw_icon("trash", "#FFFFFF", 16), "Закрыть все закрепы", tray_menu)
        act_close_all.triggered.connect(self.edge_controller.close_all_pinned)
        tray_menu.addAction(act_close_all)

        tray_menu.addSeparator()

        # Quit
        act_quit = QAction(draw_icon("close", "#F87171", 16), "Выход", tray_menu)
        act_quit.triggered.connect(self.quit_app)
        tray_menu.addAction(act_quit)

        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.activated.connect(self._on_tray_activated)
        self.tray_icon.show()

    def _on_tray_activated(self, reason):
        if reason == QSystemTrayIcon.ActivationReason.Trigger:
            if not self.edge_controller.panel.isVisible():
                self.edge_controller.restore_from_tray()
                self.act_toggle_handle.setChecked(True)
            else:
                if self.edge_controller.panel.is_open:
                    self.edge_controller.panel.close_panel()
                else:
                    self.edge_controller.panel.open_panel()

    def _toggle_edge_handle(self, checked: bool):
        if checked:
            self.edge_controller.restore_from_tray()
        else:
            self.edge_controller.hide_to_tray()

    def _toggle_autostart(self, checked: bool):
        set_autostart(checked)
        self.edge_controller.panel._update_autostart_badge()

    def trigger_snip(self):
        """Launches the fullscreen capture and snipping overlay."""
        if self.snip_overlay is not None:
            self.snip_overlay.close()

        self.snip_overlay = SnippingOverlay()
        self.snip_overlay.snip_pinned.connect(self.on_snip_pinned)
        self.snip_overlay.start_capture()

    def on_snip_pinned(self, pixmap: QPixmap, pos: QPoint):
        """Called when user confirms pinning a region."""
        pinned = PinnedImageWidget(pixmap, pos)
        pinned.show()
        self.edge_controller.add_pinned_widget(pinned)

    def quit_app(self):
        """Closes all windows and exits application."""
        self.edge_controller.close_all_pinned()
        self.tray_icon.hide()
        self.app.quit()


def main():
    # Set Windows App ID for high resolution icon in taskbar
    try:
        myappid = 'samsung.edge.snip.pin.app.v1'
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
    except Exception:
        pass

    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)  # Keep running in tray even if all pinned are closed
    app.setWindowIcon(create_app_icon(64))

    controller = AppController(app)

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
