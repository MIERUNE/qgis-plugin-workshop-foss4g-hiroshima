from typing import Optional

from qgis.gui import QgisInterface, QgsExtentGroupBox
from qgis.PyQt.QtWidgets import (
    QDialog,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from ..countries import countries_in_extent


class Dialog(QDialog):
    def __init__(
        self,
        iface: Optional[QgisInterface] = None,
        parent: Optional[QWidget] = None,
    ):
        super().__init__(parent)
        self.iface = iface
        self.setWindowTitle("Countries Checker")
        self.resize(400, 400)

        layout = QVBoxLayout()
        self.setLayout(layout)

        layout.addWidget(QLabel("Specify the target extent:"))

        # QGIS standard extent widget. When a map canvas is provided, the
        # "current map extent" and "draw on canvas" options become available.
        self.extentGroupBox = QgsExtentGroupBox()
        canvas = iface.mapCanvas() if iface is not None else None
        if canvas is not None:
            self.extentGroupBox.setMapCanvas(canvas)
            self.extentGroupBox.setCurrentExtent(
                canvas.extent(), canvas.mapSettings().destinationCrs()
            )
            self.extentGroupBox.setOutputExtentFromCurrent()
        layout.addWidget(self.extentGroupBox)

        layout.addWidget(QLabel("Countries within the extent:"))
        self.resultList = QListWidget()
        layout.addWidget(self.resultList)

        button_layout = QHBoxLayout()
        layout.addLayout(button_layout)

        self.pushButton_run = QPushButton("Check countries")
        button_layout.addWidget(self.pushButton_run)

        self.pushButton_close = QPushButton("Close")
        button_layout.addWidget(self.pushButton_close)

        # Connect signals and slots
        self.pushButton_run.clicked.connect(self.check_countries)
        self.pushButton_close.clicked.connect(self._on_close_clicked)

    def _on_close_clicked(self, checked: bool) -> None:
        self.reject()

    def check_countries(self) -> None:
        """Search for countries within the extent and show them in the list."""
        extent = self.extentGroupBox.outputExtent()
        crs = self.extentGroupBox.outputCrs()

        self.resultList.clear()

        if extent is None or extent.isEmpty():
            QMessageBox.warning(
                self, "Countries Checker", "Please specify a valid extent."
            )
            return

        names = countries_in_extent(extent, crs)
        if names:
            self.resultList.addItems(names)
        else:
            self.resultList.addItem("(No countries found)")
