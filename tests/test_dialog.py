from unittest.mock import MagicMock

import pytest
from plugin_dir.ui import (  # pyright: ignore[reportMissingImports]
    dialog as dialog_module,
)
from plugin_dir.ui.dialog import Dialog  # pyright: ignore[reportMissingImports]
from qgis.PyQt.QtWidgets import (
    QHBoxLayout,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
)

pytestmark = pytest.mark.usefixtures("qgis_plugin_path")


class TestDialogInitial:
    def test_window_title(self):
        """ウィンドウタイトルが期待値であること"""
        dialog = Dialog()
        assert dialog.windowTitle() == "Dialog"

    def test_button_labels(self):
        """OK / キャンセル ボタンのラベルが期待値であること"""
        dialog = Dialog()
        assert isinstance(dialog.pushButton_run, QPushButton)
        assert isinstance(dialog.pushButton_cancel, QPushButton)
        assert dialog.pushButton_run.text() == "OK"
        assert dialog.pushButton_cancel.text() == "キャンセル"

    def test_line_edit_properties(self):
        """lineEdit の型・最小幅・初期テキストが期待値であること"""
        dialog = Dialog()
        assert isinstance(dialog.lineEdit, QLineEdit)
        assert dialog.lineEdit.minimumWidth() >= 300
        assert dialog.lineEdit.text() == ""

    def test_layout_structure(self):
        """ルートレイアウトが QVBoxLayout かつボタン群が QHBoxLayout に格納されていること"""
        dialog = Dialog()
        root_layout = dialog.layout()
        assert root_layout is not None
        assert isinstance(root_layout, QVBoxLayout)

        button_layout = None
        for i in range(root_layout.count()):
            item = root_layout.itemAt(i)
            assert item is not None
            sub_layout = item.layout()
            if isinstance(sub_layout, QHBoxLayout):
                button_layout = sub_layout
                break
        assert button_layout is not None

        button_widgets = []
        for i in range(button_layout.count()):
            item = button_layout.itemAt(i)
            assert item is not None
            widget = item.widget()
            if widget is not None:
                button_widgets.append(widget)
        assert dialog.pushButton_run in button_widgets
        assert dialog.pushButton_cancel in button_widgets


class TestDialogOkButton:
    def test_ok_click_invokes_message_box_once(self, monkeypatch: pytest.MonkeyPatch):
        """OK クリックで QMessageBox.information が一度だけ呼ばれること"""
        mock_info = MagicMock()
        monkeypatch.setattr(dialog_module.QMessageBox, "information", mock_info)

        dialog = Dialog()
        dialog.lineEdit.setText("hello")
        dialog.pushButton_run.click()

        assert mock_info.call_count == 1

    def test_ok_click_passes_line_edit_text(self, monkeypatch: pytest.MonkeyPatch):
        """QMessageBox.information の引数に lineEdit のテキストが渡ること"""
        mock_info = MagicMock()
        monkeypatch.setattr(dialog_module.QMessageBox, "information", mock_info)

        dialog = Dialog()
        dialog.lineEdit.setText("hello")
        dialog.pushButton_run.click()

        assert mock_info.call_args is not None
        assert mock_info.call_args.args[2] == "hello"

    def test_ok_click_with_empty_text(self, monkeypatch: pytest.MonkeyPatch):
        """空文字列状態でもモックは空文字を引数として呼ばれること"""
        mock_info = MagicMock()
        monkeypatch.setattr(dialog_module.QMessageBox, "information", mock_info)

        dialog = Dialog()
        dialog.lineEdit.setText("")
        dialog.pushButton_run.click()

        assert mock_info.call_count == 1
        assert mock_info.call_args is not None
        assert mock_info.call_args.args[2] == ""

    def test_get_and_show_input_text_direct_call(self, monkeypatch: pytest.MonkeyPatch):
        """get_and_show_input_text を直接呼んでもモックが期待引数で呼ばれること"""
        mock_info = MagicMock()
        monkeypatch.setattr(dialog_module.QMessageBox, "information", mock_info)

        dialog = Dialog()
        dialog.lineEdit.setText("foo")
        dialog.get_and_show_input_text()

        assert mock_info.call_count == 1
        assert mock_info.call_args is not None
        assert mock_info.call_args.args[2] == "foo"


class TestDialogCancelButton:
    def test_cancel_click_invokes_reject_once(self, monkeypatch: pytest.MonkeyPatch):
        """キャンセルボタンのクリックで reject() が一度だけ呼ばれること"""
        dialog = Dialog()
        mock_reject = MagicMock()
        monkeypatch.setattr(dialog, "reject", mock_reject)

        dialog.pushButton_cancel.click()

        assert mock_reject.call_count == 1

    def test_on_cancel_clicked_direct_call(self, monkeypatch: pytest.MonkeyPatch):
        """_on_cancel_clicked を直接呼んでも reject() が起動すること"""
        dialog = Dialog()
        mock_reject = MagicMock()
        monkeypatch.setattr(dialog, "reject", mock_reject)

        dialog._on_cancel_clicked(checked=False)

        assert mock_reject.call_count == 1


class TestDialogSignalWiring:
    def test_run_signal_connected_to_slot(self, monkeypatch: pytest.MonkeyPatch):
        """pushButton_run.clicked が get_and_show_input_text に結線されていること"""
        mock_slot = MagicMock()
        # Dialog.__init__ 内の self.get_and_show_input_text 評価が
        # クラス属性経由で関数オブジェクトを解決するため、インスタンス化前にパッチする。
        monkeypatch.setattr(Dialog, "get_and_show_input_text", mock_slot)

        dialog = Dialog()
        dialog.pushButton_run.click()

        assert mock_slot.call_count == 1

    def test_cancel_signal_connected_to_slot(self, monkeypatch: pytest.MonkeyPatch):
        """pushButton_cancel.clicked が _on_cancel_clicked に結線されていること"""
        mock_slot = MagicMock()
        monkeypatch.setattr(Dialog, "_on_cancel_clicked", mock_slot)

        dialog = Dialog()
        dialog.pushButton_cancel.click()

        assert mock_slot.call_count == 1
