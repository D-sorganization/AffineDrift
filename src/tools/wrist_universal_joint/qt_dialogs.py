"""Dialog helpers for the enhanced wrist universal joint Qt app."""

from __future__ import annotations

from PyQt6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QScrollArea,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)


class DocumentationDialog(QDialog):  # type: ignore[misc]
    """Dialog showing the model's documentation summary."""

    def __init__(self, parent: QWidget | None = None) -> None:
        """Initialize documentation dialog."""
        super().__init__(parent)
        self.setWindowTitle("Universal Joint Model - Mathematics & Physics")
        self.setGeometry(150, 150, 900, 800)
        self._init_ui()

    def _init_ui(self) -> None:
        """Create the dialog layout."""
        layout = QVBoxLayout(self)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        text_widget = QTextEdit()
        text_widget.setReadOnly(True)
        text_widget.setHtml(self._documentation_html())
        scroll.setWidget(text_widget)
        layout.addWidget(scroll)

        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Close)
        button_box.rejected.connect(self.accept)
        layout.addWidget(button_box)

    def _documentation_html(self) -> str:
        """Return the embedded HTML documentation content."""
        return """
        <html>
        <head>
        <style>
        body { font-family: Arial, sans-serif; line-height: 1.6; padding: 15px; }
        h1 { color: #2c3e50; border-bottom: 3px solid #3498db; padding-bottom: 8px; }
        h2 { color: #34495e; margin-top: 25px; border-bottom: 1px solid #bdc3c7;
             padding-bottom: 5px; }
        </style>
        </head>
        <body>
        <h1>Enhanced Wrist Universal Joint Model</h1>
        <p>See the full documentation in the README_ENHANCED_MODEL.md file.</p>
        </body>
        </html>
        """
