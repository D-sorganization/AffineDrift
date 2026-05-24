"""Small Qt widget subclasses used by the enhanced wrist model app."""

from __future__ import annotations

from typing import Any

from PyQt6.QtCore import QEvent, QObject
from PyQt6.QtGui import QWheelEvent
from PyQt6.QtWidgets import QLineEdit, QSlider


class WheelIgnoringSlider(QSlider):
    """Slider that ignores wheel events so the parent scroll area handles them."""

    def wheelEvent(self, event: QWheelEvent | None) -> None:
        """Ignore wheel events and let them bubble upward."""
        if event:
            event.ignore()


class WheelIgnoringLineEdit(QLineEdit):
    """Line edit that ignores wheel events so the parent scroll area handles them."""

    def wheelEvent(self, event: QWheelEvent | None) -> None:
        """Ignore wheel events and let them bubble upward."""
        if event:
            event.ignore()


class WheelEventFilter(QObject):
    """Event filter that blocks wheel events from reaching input controls."""

    def eventFilter(self, watched: QObject | None, event: QEvent | None) -> bool:
        """Filter out wheel events to prevent value changes."""
        if event and event.type() == QEvent.Type.Wheel:
            if isinstance(event, QWheelEvent):
                event.accept()
                return True
        return False


_WHEEL_FILTER_ATTR = "_wheel_event_filter"


def suppress_wheel_on_widgets(*widgets: Any) -> None:
    """Convenience function to install wheel event filter on multiple widgets."""
    for widget in widgets:
        filter_instance = WheelEventFilter()
        setattr(widget, _WHEEL_FILTER_ATTR, filter_instance)
        widget.installEventFilter(filter_instance)
