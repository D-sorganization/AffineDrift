"""Small Qt widget subclasses used by the enhanced wrist model app."""

from __future__ import annotations

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
