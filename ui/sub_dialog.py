from qgis.PyQt.QtWidgets import (
    QDialog,
    QHBoxLayout,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
)


class SubDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Dialog")
        self.resize(318, 68)

        layout = QVBoxLayout()
        self.setLayout(layout)

        self.lineEdit = QLineEdit()
        self.lineEdit.setMinimumWidth(300)
        layout.addWidget(self.lineEdit)

        button_layout = QHBoxLayout()
        layout.addLayout(button_layout)

        self.pushButton_run = QPushButton("OK")
        button_layout.addWidget(self.pushButton_run)

        self.pushButton_cancel = QPushButton("キャンセル")
        button_layout.addWidget(self.pushButton_cancel)

        # シグナルとスロットの接続
        self.pushButton_run.clicked.connect(
            lambda: self.get_and_show_input_text(
                "\nlambda sample"
            )  # ラムダ式でもconnectできる
        )
        self.pushButton_cancel.clicked.connect(self._on_cancel_clicked)

    def _on_cancel_clicked(self, checked: bool) -> None:
        self.reject()

    def get_and_show_input_text(self, suffix: str):
        text_value = self.lineEdit.text()
        QMessageBox.information(self, "ウィンドウ名", text_value + suffix)
