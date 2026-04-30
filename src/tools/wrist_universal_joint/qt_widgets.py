"""Small Qt widget subclasses used by the enhanced wrist model app."""

from __future__ import annotations

from PyQt6.QtCore import QEvent
from PyQt6.QtWidgets import QLineEdit, QSlider


class WheelIgnoringSlider(QSlider):  # type: ignore[misc]
    """Slider that ignores wheel events so the parent scroll area handles them."""

    def wheelEvent(self, event: QEvent) -> None:
        """Ignore wheel events and let them bubble upward."""
        event.ignore()


class WheelIgnoringLineEdit(QLineEdit):  # type: ignore[misc]
    """Line edit that ignores wheel events so the parent scroll area handles them."""

    def wheelEvent(self, event: QEvent) -> None:
        """Ignore wheel events and let them bubble upward."""
        event.ignore()
