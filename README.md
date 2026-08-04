# Countries Checker

A QGIS 3.x plugin that lists the countries falling within a given map extent.

## What is this?

The plugin adds a **Countries Checker** dialog where you specify a map extent
(type coordinates, use the current map extent, or draw on the canvas) and get
back the list of countries that intersect it. Country geometries come from the
bundled `data/ne_countries.gpkg` (Natural Earth, `NAME_LONG` field).

It also serves as a QGIS plugin template with:

- A UI implemented in Python code
- Automated tests
- Static type checking

## Preparation

The steps below enable type checking and QGIS Python API autocompletion in VSCode.

1. `uv sync`
2. Enable QGIS Python API autocompletion in VSCode
    1. Edit `extraPaths` in `pyrightconfig.json` to match your QGIS installation
        - **macOS**: `/Applications/QGIS.app/Contents/Resources/python3.XX/site-packages`
        - **Windows (OSGeo4W)**: ??
3. Set the VSCode Python interpreter to the virtual environment built by `uv sync`

## Running the tests

The tests depend on the QGIS Python runtime, so run them with Docker:

```bash
docker run --rm \
  -v "$(pwd)":/plugin \
  -w /plugin \
  qgis/qgis:3.40 \
  sh -c "
    pip3 install --break-system-packages pytest pytest-qgis &&
    xvfb-run -s '+extension GLX -screen 0 1024x768x24' \
      python3 -m pytest tests/ -v
  "
```

## Tips

### Python version

QGIS 3.40 on macOS bundles Python 3.9, which is currently the oldest Python
version in play. If you need to support that QGIS build, implement using
Python 3.9 syntax.

### PyQt5 / PyQt6 compatibility

- The development environment built by this repository is based on PyQt5,
  because the Python stubs bundled with QGIS still depend on PyQt5.
- Most APIs are shared between PyQt5 and PyQt6, but a few differ. Code written
  against the PyQt5 API can therefore break under PyQt6 (and vice versa). When
  you need to support both, introduce a compatibility layer as needed.

### Type checking

The QGIS Python API type definitions are incomplete, so occasionally you have to
suppress checks with `# pyright: ignore[<specific-rule>]`. Where type
definitions exist, keep type checking on to preserve code quality.

#### Some types not resolving

There is an issue with the Python type stubs bundled with QGIS: some classes,
such as `QAction`, do not resolve their types.

### Relative imports

- Split modules by concern (e.g. the `ui` module).
- Prefer relative imports: absolute imports like the one below can stop
  [Plugin Reloader](https://plugins.qgis.org/plugins/plugin_reloader/) from
  picking up changes ([Issue #16](https://github.com/MIERUNE/qgis-plugin-template/issues/16)).

```python
from child import Child   # not good
from .child import Child  # better
```
