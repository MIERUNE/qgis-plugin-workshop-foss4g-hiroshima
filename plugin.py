import os
from typing import Optional

from qgis.core import QgsApplication
from qgis.gui import QgisInterface
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtWidgets import QAction

from .processing.provider import SampleProvider
from .ui.dialog import Dialog
from .ui.sub_dialog import SubDialog

PLUGIN_NAME = "sample"


class Plugin:
    def __init__(self, iface: QgisInterface):
        self.iface = iface
        self.win = self.iface.mainWindow()
        self.plugin_dir = os.path.dirname(__file__)
        self.actions = []
        self.menu = PLUGIN_NAME
        self.provider: Optional[SampleProvider] = None
        self._provider_added = False

        toolbar = self.iface.addToolBar(PLUGIN_NAME)
        assert toolbar is not None
        self.toolbar = toolbar
        self.toolbar.setObjectName(PLUGIN_NAME)

    def add_action(
        self,
        icon_path,
        text,
        callback,
        enabled_flag=True,
        add_to_menu=True,
        add_to_toolbar=True,
        status_tip=None,
        whats_this=None,
        parent=None,
    ):
        icon = QIcon(icon_path)
        action = QAction(icon, text, parent)
        action.triggered.connect(callback)
        action.setEnabled(enabled_flag)
        if status_tip is not None:
            action.setStatusTip(status_tip)
        if whats_this is not None:
            action.setWhatsThis(whats_this)
        if add_to_toolbar:
            self.toolbar.addAction(action)
        if add_to_menu:
            self.iface.addPluginToMenu(self.menu, action)
        self.actions.append(action)
        return action

    def initGui(self):
        self.provider = SampleProvider()

        registry = QgsApplication.processingRegistry()
        assert registry is not None
        if not registry.providerById(self.provider.id()):
            registry.addProvider(self.provider)
            self._provider_added = True

        # メニュー設定
        self.add_action(
            icon_path=None, text="Menu01", callback=self.show_dialog, parent=self.win
        )
        self.add_action(
            icon_path=None,
            text="Menu02",
            callback=self.show_sub_dialog,
            parent=self.win,
        )

    def unload(self):
        if self._provider_added and self.provider is not None:
            registry = QgsApplication.processingRegistry()
            assert registry is not None
            registry.removeProvider(self.provider)
            self._provider_added = False
        self.provider = None

        for action in self.actions:
            self.iface.removePluginMenu(PLUGIN_NAME, action)
            self.iface.removeToolBarIcon(action)
        del self.toolbar

    def show_dialog(self):
        self.dialog = Dialog()
        self.dialog.show()

    def show_sub_dialog(self):
        self.sub_dialog = SubDialog()
        self.sub_dialog.show()
