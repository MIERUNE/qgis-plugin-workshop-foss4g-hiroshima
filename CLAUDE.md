# CLAUDE.md

## Project overview

Countries Checker: a QGIS plugin that lists the countries falling within a
given map extent. Country data ships in `data/ne_countries.gpkg` (layer
`ne_countries`, `NAME_LONG` field).

### Testing (Docker required)

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

## Coding conventions

### Imports inside the plugin

- Reference in-plugin modules with relative imports: `from .ui.dialog import Dialog`.
- Do not use absolute imports (`from ui.dialog import Dialog`); they can break
  Plugin Reloader's change detection
  ([Issue #16](https://github.com/MIERUNE/qgis-plugin-template/issues/16)).
- The rule is inverted inside tests. Use the virtual package that `conftest.py`
  registers, e.g. `from plugin_dir.ui.dialog import Dialog` or
  `from plugin_dir.countries import countries_in_extent`. Do not import the
  plugin as a top-level module (subpackage names such as `ui/` can collide with
  QGIS built-in modules).

### Type-checking policy

- When suppression is required, use `# pyright: ignore[<specific-rule>]`
  (e.g. `# pyright: ignore[reportAttributeAccessIssue]`).
- Do not use blanket `# type: ignore`.

### Testing Processing algorithms

- `native:*` is testable.
- `qgis:*` is mostly testable.
- `gdal:*` is not testable in this environment. Do not attempt it.
- Do not call `processing.Processing.initialize()` (it loads GUI components and
  can segfault under xvfb). Register providers directly on
  `QgsApplication.processingRegistry()` (see the `qgis_plugin_path` fixture in
  `conftest.py`).

### Plugin lifecycle

- Anything added to QGIS in `Plugin.initGui` (actions, toolbars, providers,
  etc.) must be removed with the matching call in `Plugin.unload`.
- Guarantee idempotency of add/remove with a flag. Reference pattern for
  registering something globally (e.g. a Processing provider):

  ```python
  if registry.providerById(self._provider.id()) is None:
      registry.addProvider(self._provider)
      self._provider_added = True
  ```

  On the `unload` side, check `self._provider_added` before removing. Follow the
  same pattern whenever you add a new global registration.

### Directories and naming

- The repository root is the QGIS plugin package itself. For a new area of
  concern, add a sibling directory rather than forcing it into an existing
  subpackage (e.g. `expressions/` for custom expressions).
- Files/modules are `snake_case.py`, classes are `PascalCase`, functions and
  methods are `snake_case`, constants are `UPPER_SNAKE_CASE`.
- Keep Qt's casing for overridden Qt methods (`initAlgorithm`,
  `processAlgorithm`, `initGui`, `unload`, etc.).
- Test files are `test_<target>.py`, test classes are `TestXxx`.
