"""The one stylesheet every ROSE window shares.

Set on the editor window, it cascades to every tab, panel and dialog parented
under it. Windows that are opened without a parent (Preferences) do not inherit
it and call applyROSEStyle() themselves.

Buttons carry their role as a dynamic property rather than an inline stylesheet:
an inline sheet on the button outranks everything here, so a coloured button
set that way lost its hover and pressed states. setButtonVariant() sets it.
"""

#the amber the canvases already use for selection, so a pressed button and a
#selected node read as the same kind of "active"
ACCENT = "#FFA637"
ACCENT_TEXT = "#222222"

BUTTON_BACKGROUND = "#3D3D3D"
BUTTON_HOVER = "#4A4A4A"
BUTTON_BORDER = "#555555"
BUTTON_TEXT = "#DDDDDD"
DISABLED_BACKGROUND = "#333333"
DISABLED_TEXT = "#777777"

ACCEPT_BACKGROUND = "#2E6B2E"
ACCEPT_HOVER = "#3A823A"
DANGER_BACKGROUND = "#6B2E2E"
DANGER_HOVER = "#823A3A"
#a toggled-on choice - the side prefix buttons, which pick one of three
MARKED_BACKGROUND = "#336600"
MARKED_HOVER = "#3F7A00"

GROUP_HEADER_BACKGROUND = "#323232"
GROUP_HEADER_HOVER = "#3A3A3A"

BUTTON_RADIUS = 6

ROSE_STYLESHEET = """
QPushButton, QToolBar QToolButton {{
    background-color: {background};
    border: 1px solid {border};
    border-radius: {radius}px;
    color: {text};
    padding: 4px 12px;
    min-height: 16px;
}}
QPushButton:hover, QToolBar QToolButton:hover {{
    background-color: {hover};
    border-color: #6A6A6A;
}}
QPushButton:pressed, QToolBar QToolButton:pressed,
QPushButton:checked, QToolBar QToolButton:checked {{
    background-color: {accent};
    border-color: {accent};
    color: {accent_text};
}}
QPushButton:disabled, QToolBar QToolButton:disabled {{
    background-color: {disabled_background};
    border-color: #444444;
    color: {disabled_text};
}}
QPushButton:default {{
    border-color: {accent};
}}

QPushButton[variant="accept"] {{ background-color: {accept}; }}
QPushButton[variant="accept"]:hover {{ background-color: {accept_hover}; }}
QPushButton[variant="danger"] {{ background-color: {danger}; }}
QPushButton[variant="danger"]:hover {{ background-color: {danger_hover}; }}
QPushButton[marked="true"] {{ background-color: {marked}; border-color: {marked}; }}
QPushButton[marked="true"]:hover {{ background-color: {marked_hover}; }}
QPushButton[variant="accept"]:pressed, QPushButton[variant="danger"]:pressed,
QPushButton[marked="true"]:pressed {{
    background-color: {accent};
    color: {accent_text};
}}
QPushButton[variant="accept"]:disabled, QPushButton[variant="danger"]:disabled {{
    background-color: {disabled_background};
    color: {disabled_text};
}}

/* tight spaces - a row's remove button, the reload button in the tab bar */
QPushButton[compact="true"] {{
    padding: 1px 4px;
    min-height: 14px;
    border-radius: 4px;
}}

QToolBar {{
    spacing: 4px;
    padding: 3px;
}}

/* the collapsible headers in the grouped lists */
QWidget#listGroupHeader {{
    background-color: {group_background};
    border-radius: 4px;
}}
QWidget#listGroupHeader:hover {{
    background-color: {group_hover};
}}
""".format(
    background = BUTTON_BACKGROUND, hover = BUTTON_HOVER, border = BUTTON_BORDER, text = BUTTON_TEXT,
    radius = BUTTON_RADIUS, accent = ACCENT, accent_text = ACCENT_TEXT,
    disabled_background = DISABLED_BACKGROUND, disabled_text = DISABLED_TEXT,
    accept = ACCEPT_BACKGROUND, accept_hover = ACCEPT_HOVER,
    danger = DANGER_BACKGROUND, danger_hover = DANGER_HOVER,
    marked = MARKED_BACKGROUND, marked_hover = MARKED_HOVER,
    group_background = GROUP_HEADER_BACKGROUND, group_hover = GROUP_HEADER_HOVER,
)


def applyROSEStyle(widget):
    widget.setStyleSheet(ROSE_STYLESHEET)


def repolish(widget):
    """Re-read the stylesheet after a dynamic property changed - Qt does not
    notice a property change on its own."""
    style = widget.style()
    style.unpolish(widget)
    style.polish(widget)
    widget.update()


def setButtonVariant(button, variant):
    """"accept", "danger", or None for a plain button."""
    button.setProperty("variant", variant or "")
    repolish(button)


def setButtonMarked(button, is_marked):
    button.setProperty("marked", bool(is_marked))
    repolish(button)


def setButtonCompact(button, is_compact = True):
    button.setProperty("compact", bool(is_compact))
    repolish(button)
