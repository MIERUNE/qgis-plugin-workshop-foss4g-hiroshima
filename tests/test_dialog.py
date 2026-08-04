from unittest.mock import MagicMock

import pytest
from plugin_dir.ui import (  # pyright: ignore[reportMissingImports]
    dialog as dialog_module,
)
from plugin_dir.ui.dialog import Dialog  # pyright: ignore[reportMissingImports]
from qgis.core import QgsCoordinateReferenceSystem, QgsRectangle
from qgis.gui import QgsExtentGroupBox
from qgis.PyQt.QtWidgets import QListWidget, QPushButton

pytestmark = pytest.mark.usefixtures("qgis_plugin_path")

WGS84 = QgsCoordinateReferenceSystem("EPSG:4326")


def _result_texts(dialog: Dialog) -> list[str]:
    return [dialog.resultList.item(i).text() for i in range(dialog.resultList.count())]


class TestDialogInitial:
    def test_window_title(self):
        """The window title should match the expected value."""
        dialog = Dialog()
        assert dialog.windowTitle() == "Countries Checker"

    def test_button_labels(self):
        """The Check countries / Close button labels should match the expected values."""
        dialog = Dialog()
        assert isinstance(dialog.pushButton_run, QPushButton)
        assert isinstance(dialog.pushButton_close, QPushButton)
        assert dialog.pushButton_run.text() == "Check countries"
        assert dialog.pushButton_close.text() == "Close"

    def test_widgets_exist(self):
        """The extent input and result list widgets should exist."""
        dialog = Dialog()
        assert isinstance(dialog.extentGroupBox, QgsExtentGroupBox)
        assert isinstance(dialog.resultList, QListWidget)


class TestDialogCheckCountries:
    def test_ok_click_lists_japan(self):
        """Clicking Check countries on an extent over Japan should list Japan."""
        dialog = Dialog()
        dialog.extentGroupBox.setOutputExtentFromUser(
            QgsRectangle(138.0, 34.0, 141.0, 37.0), WGS84
        )
        dialog.pushButton_run.click()
        assert "Japan" in _result_texts(dialog)

    def test_check_re_run_replaces_results(self):
        """Re-running the search should clear the previous results."""
        dialog = Dialog()
        dialog.extentGroupBox.setOutputExtentFromUser(
            QgsRectangle(138.0, 34.0, 141.0, 37.0), WGS84
        )
        dialog.check_countries()
        assert "Japan" in _result_texts(dialog)

        dialog.extentGroupBox.setOutputExtentFromUser(
            QgsRectangle(-140.0, -30.0, -139.0, -29.0), WGS84
        )
        dialog.check_countries()
        assert "Japan" not in _result_texts(dialog)

    def test_empty_extent_warns(self, monkeypatch: pytest.MonkeyPatch):
        """With no extent set, it should warn and not search."""
        mock_warn = MagicMock()
        monkeypatch.setattr(dialog_module.QMessageBox, "warning", mock_warn)

        dialog = Dialog()  # no canvas -> the initial extent is empty
        dialog.check_countries()

        assert mock_warn.call_count == 1
        assert dialog.resultList.count() == 0


class TestDialogCloseButton:
    def test_close_click_invokes_reject_once(self, monkeypatch: pytest.MonkeyPatch):
        """Clicking Close should invoke reject() exactly once."""
        dialog = Dialog()
        mock_reject = MagicMock()
        monkeypatch.setattr(dialog, "reject", mock_reject)

        dialog.pushButton_close.click()

        assert mock_reject.call_count == 1
