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


class DocumentationDialog(QDialog):
    """Dialog showing the model's documentation summary."""

    def __init__(self, parent: QWidget | None = None) -> None:
        """Initialize documentation dialog."""
        super().__init__(parent)
        self.setWindowTitle("Cardan Demonstration: Mathematics and Scope")
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
        <h1>Cardan and Torque Projection Demonstration</h1>
        <p>The speed ratio is cos(δ)/(1 − sin²(δ) sin²(φ)) for supported shafts
        at fixed bend δ and input phase φ. Its reciprocal is the ideal
        delivered-torque ratio only when joint storage and losses are negligible.</p>
        <p>The extra torque projection is synthetic. The hand sketch is historical;
        it does not define the supported-shaft mechanism. Scalar inertia responses
        do not integrate a golf swing, determine face yaw or rank human grips.</p>
        <p>See content/wrist-as-universal-joint/MATHEMATICAL_DERIVATION.md and
        README_ENHANCED_MODEL.md for the full derivation and model boundaries.</p>
        </body>
        </html>
        """
