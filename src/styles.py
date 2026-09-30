"""Stylesheets and theme definitions with polished modern frosted glass styling."""

DARK_THEME_QSS = """
/* Global typography and palette */
* {
    font-family: 'Segoe UI Variable Display', 'Segoe UI', -apple-system, BlinkMacSystemFont, Roboto, sans-serif;
    font-size: 13px;
    color: #F1F5F9;
    outline: none;
}

/* Tooltips */
QToolTip {
    background-color: #181C26;
    color: #F8FAFC;
    border: 1px solid rgba(255, 255, 255, 0.18);
    border-radius: 6px;
    padding: 5px 9px;
    font-size: 12px;
    font-weight: 500;
}

/* Vertical Icon Action Buttons in Edge Panel */
QPushButton.edge-icon-btn {
    background-color: rgba(255, 255, 255, 0.07);
    color: #F1F5F9;
    border: 1px solid rgba(255, 255, 255, 0.12);
    border-radius: 11px;
    padding: 4px;
    min-width: 36px;
    max-width: 36px;
    min-height: 36px;
    max-height: 36px;
}
QPushButton.edge-icon-btn:hover {
    background-color: rgba(255, 255, 255, 0.18);
    border-color: rgba(255, 255, 255, 0.35);
}
QPushButton.edge-icon-btn:pressed {
    background-color: rgba(255, 255, 255, 0.28);
}

/* Primary Highlight Action (Snip Button) */
QPushButton.edge-primary-btn {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                                stop:0 #3B82F6, stop:1 #1D4ED8);
    color: #FFFFFF;
    border: 1px solid rgba(255, 255, 255, 0.30);
    border-radius: 11px;
    padding: 4px;
    min-width: 36px;
    max-width: 36px;
    min-height: 36px;
    max-height: 36px;
}
QPushButton.edge-primary-btn:hover {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                                stop:0 #60A5FA, stop:1 #2563EB);
    border-color: rgba(255, 255, 255, 0.55);
}
QPushButton.edge-primary-btn:pressed {
    background: #1E40AF;
}

/* Snip Floating Action Bar */
#SnipActionBar {
    background-color: rgba(20, 24, 33, 0.95);
    border: 1px solid rgba(255, 255, 255, 0.18);
    border-radius: 14px;
    padding: 5px;
}

/* Primary Button in Snip Bar (Pin) */
QPushButton.primary-btn {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                                stop:0 #3B82F6, stop:1 #2563EB);
    color: #FFFFFF;
    border: 1px solid rgba(255, 255, 255, 0.25);
    border-radius: 9px;
    padding: 6px 14px;
    font-weight: 600;
    font-size: 12px;
}
QPushButton.primary-btn:hover {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                                stop:0 #60A5FA, stop:1 #3B82F6);
    border-color: rgba(255, 255, 255, 0.45);
}
QPushButton.primary-btn:pressed {
    background: #1D4ED8;
}

/* Secondary Action Button in Snip Bar */
QPushButton.secondary-btn {
    background-color: rgba(255, 255, 255, 0.08);
    color: #F1F5F9;
    border: 1px solid rgba(255, 255, 255, 0.12);
    border-radius: 9px;
    padding: 6px 11px;
    font-weight: 500;
    font-size: 12px;
}
QPushButton.secondary-btn:hover {
    background-color: rgba(255, 255, 255, 0.18);
    border-color: rgba(255, 255, 255, 0.30);
    color: #FFFFFF;
}
QPushButton.secondary-btn:pressed {
    background-color: rgba(255, 255, 255, 0.10);
}

/* Active State for Drawing Tool Buttons */
QPushButton.tool-active-btn {
    background-color: #2563EB;
    color: #FFFFFF;
    border: 1px solid #60A5FA;
    border-radius: 9px;
    padding: 6px 11px;
    font-weight: 600;
    font-size: 12px;
}
QPushButton.tool-active-btn:hover {
    background-color: #3B82F6;
    border-color: #93C5FD;
}

/* Danger Button in Snip Bar (Cancel) */
QPushButton.danger-icon-btn {
    background-color: rgba(239, 68, 68, 0.12);
    color: #F87171;
    border: 1px solid rgba(239, 68, 68, 0.25);
    border-radius: 9px;
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
    border-radius: 6px;
    padding: 3px;
    min-width: 22px;
    max-width: 22px;
    min-height: 22px;
    max-height: 22px;
}
QPushButton.micro-btn:hover {
    background-color: rgba(255, 255, 255, 0.22);
    border-color: rgba(255, 255, 255, 0.40);
    color: #FFFFFF;
}
QPushButton.micro-btn:pressed {
    background-color: rgba(255, 255, 255, 0.32);
}

/* Micro Danger Button (Close) */
QPushButton.micro-danger-btn {
    background-color: rgba(239, 68, 68, 0.12);
    color: #F87171;
    border: 1px solid rgba(239, 68, 68, 0.25);
    border-radius: 6px;
    padding: 3px;
    min-width: 22px;
    max-width: 22px;
    min-height: 22px;
    max-height: 22px;
}
QPushButton.micro-danger-btn:hover {
    background-color: #EF4444;
    border-color: #F87171;
    color: #FFFFFF;
}
"""

