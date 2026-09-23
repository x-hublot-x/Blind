"""Stylesheets and theme definitions with frosted glass styling and clean borders."""

DARK_THEME_QSS = """
/* Global styling */
* {
    font-family: 'Segoe UI', 'SF Pro Display', -apple-system, Roboto, sans-serif;
    font-size: 13px;
    color: #F3F4F6;
}

/* Tooltips - Clean, pixel-perfect solid styling without raster corner dots */
QToolTip {
    background-color: #1A1D24;
    color: #F9FAFB;
    border: 1px solid #3B4252;
    border-radius: 5px;
    padding: 4px 8px;
    font-size: 11px;
}

/* Vertical Icon Action Buttons in Edge Panel */
QPushButton.edge-icon-btn {
    background-color: rgba(255, 255, 255, 0.08);
    color: #FFFFFF;
    border: 1px solid rgba(255, 255, 255, 0.14);
    border-radius: 10px;
    padding: 4px;
    min-width: 36px;
    max-width: 36px;
    min-height: 36px;
    max-height: 36px;
}
QPushButton.edge-icon-btn:hover {
    background-color: rgba(255, 255, 255, 0.24);
    border-color: rgba(255, 255, 255, 0.45);
}
QPushButton.edge-icon-btn:pressed {
    background-color: rgba(255, 255, 255, 0.35);
}

/* Primary Highlight Action (Snip Button) */
QPushButton.edge-primary-btn {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                                stop:0 #3B82F6, stop:1 #2563EB);
    color: #FFFFFF;
    border: 1px solid rgba(255, 255, 255, 0.35);
    border-radius: 10px;
    padding: 4px;
    min-width: 36px;
    max-width: 36px;
    min-height: 36px;
    max-height: 36px;
}
QPushButton.edge-primary-btn:hover {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                                stop:0 #60A5FA, stop:1 #3B82F6);
    border-color: rgba(255, 255, 255, 0.6);
}
QPushButton.edge-primary-btn:pressed {
    background: #1D4ED8;
}

/* Snip Action Bar (Under/Above Selection) */
#SnipActionBar {
    background-color: rgba(35, 39, 48, 0.94);
    border: 1px solid rgba(255, 255, 255, 0.22);
    border-radius: 12px;
    padding: 4px;
}

/* Primary Button in Snip Bar */
QPushButton.primary-btn {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                                stop:0 #3B82F6, stop:1 #2563EB);
    color: #FFFFFF;
    border: none;
    border-radius: 8px;
    padding: 6px 12px;
    font-weight: 600;
    font-size: 12px;
}
QPushButton.primary-btn:hover {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                                stop:0 #60A5FA, stop:1 #3B82F6);
}
QPushButton.primary-btn:pressed {
    background: #1D4ED8;
}

/* Secondary Button in Snip Bar */
QPushButton.secondary-btn {
    background-color: rgba(255, 255, 255, 0.09);
    color: #F1F5F9;
    border: 1px solid rgba(255, 255, 255, 0.15);
    border-radius: 8px;
    padding: 6px 10px;
    font-weight: 500;
    font-size: 12px;
}
QPushButton.secondary-btn:hover {
    background-color: rgba(255, 255, 255, 0.2);
    border-color: rgba(255, 255, 255, 0.35);
    color: #FFFFFF;
}
QPushButton.secondary-btn:pressed {
    background-color: rgba(255, 255, 255, 0.05);
}

/* Danger Button in Snip Bar */
QPushButton.danger-icon-btn {
    background-color: rgba(255, 255, 255, 0.09);
    color: #F87171;
    border: 1px solid rgba(255, 255, 255, 0.15);
    border-radius: 8px;
    padding: 6px;
}
QPushButton.danger-icon-btn:hover {
    background-color: #EF4444;
    border-color: #F87171;
    color: #FFFFFF;
}

/* Micro Action Buttons on Pinned Screenshot */
QPushButton.micro-btn {
    background-color: rgba(255, 255, 255, 0.08);
    color: #E2E8F0;
    border: 1px solid rgba(255, 255, 255, 0.12);
    border-radius: 5px;
    padding: 2px;
    min-width: 20px;
    max-width: 20px;
    min-height: 20px;
    max-height: 20px;
}
QPushButton.micro-btn:hover {
    background-color: rgba(255, 255, 255, 0.25);
    border-color: rgba(255, 255, 255, 0.45);
    color: #FFFFFF;
}
QPushButton.micro-btn:pressed {
    background-color: rgba(255, 255, 255, 0.35);
}

/* Micro Danger Button (Close) */
QPushButton.micro-danger-btn {
    background-color: rgba(255, 255, 255, 0.08);
    color: #F87171;
    border: 1px solid rgba(255, 255, 255, 0.12);
    border-radius: 5px;
    padding: 2px;
    min-width: 20px;
    max-width: 20px;
    min-height: 20px;
    max-height: 20px;
}
QPushButton.micro-danger-btn:hover {
    background-color: #EF4444;
    border-color: #F87171;
    color: #FFFFFF;
}
"""
