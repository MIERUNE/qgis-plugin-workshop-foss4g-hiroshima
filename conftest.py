"""pytest conftest: make plugin importable as 'plugin_dir' package."""

import os
import sys
import types
from pathlib import Path

import pytest

# The plugin root is this directory. Expose it as a virtual 'plugin_dir'
# package so plugin modules can be imported via `plugin_dir.xxx` in tests,
# instead of being picked up as top-level modules.
#
# This keeps plugin subpackages (e.g. `processing/`) from shadowing QGIS
# built-in modules with the same name, while avoiding a filesystem symlink
# outside the project directory (which can fail in Docker / read-only
# environments).
_plugin_root = Path(__file__).resolve().parent

_pkg = types.ModuleType("plugin_dir")
_pkg.__path__ = [str(_plugin_root)]
sys.modules["plugin_dir"] = _pkg

# Remove the plugin root from sys.path so that plugin subpackages
# (e.g. 'processing/') don't shadow QGIS built-in modules.
# Plugin modules must be imported via 'plugin_dir.xxx' instead.
_plugin_root_str = str(_plugin_root)
sys.path[:] = [p for p in sys.path if p not in (_plugin_root_str, "")]


@pytest.fixture(scope="session")
def qgis_plugin_path(qgis_app):
    """Add QGIS's built-in plugin directory to sys.path.

    Depends on qgis_app (provided by pytest-qgis) to ensure
    QgsApplication is fully initialized before querying pkgDataPath().
    """
    from qgis.core import QgsApplication

    qgis_plugins = os.path.join(QgsApplication.pkgDataPath(), "python", "plugins")
    if os.path.isdir(qgis_plugins) and qgis_plugins not in sys.path:
        sys.path.append(qgis_plugins)

    # Register built-in algorithm providers directly.
    # Avoid processing.Processing.initialize() as it loads GUI
    # components that can cause segfaults in headless test environments.
    from qgis.analysis import QgsNativeAlgorithms

    registry = QgsApplication.processingRegistry()
    assert registry is not None
    if not registry.providerById("native"):
        registry.addProvider(QgsNativeAlgorithms())
