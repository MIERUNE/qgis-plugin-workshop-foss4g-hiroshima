# CLAUDE.md

## プロジェクト概要

### テスト（Docker 必須）

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

## コーディング規約

### プラグイン内 import

- プラグイン内モジュール参照は relative import を使う：`from .ui.dialog import Dialog`。
- 絶対 import（`from ui.dialog import Dialog`）は Plugin Reloader の変更検知を壊すことがある（[Issue #16](https://github.com/MIERUNE/qgis-plugin-template/issues/16)）ため使わない。
- テスト内ではルールが反転する。`conftest.py` が登録する仮想パッケージ経由で `from plugin_dir.processing.provider import SampleProvider` のように書く。プラグインを top-level モジュールとして import しないこと（`processing/` 等の名前が QGIS の組込モジュールと衝突する）。

### 型チェック方針

- 抑制が必要な場合は `# pyright: ignore[<具体的なルール名>]` を使う（例：`# pyright: ignore[reportAttributeAccessIssue]`）。
- 包括的な `# type: ignore` は使わない。

### Processing アルゴリズムのテスト

- `native:*` はテスト可能。
- `qgis:*` は概ねテスト可能。
- `gdal:*` はこの環境ではテスト不可。試みない。
- `processing.Processing.initialize()` は呼ばない（GUI 部品を読み込み、xvfb 下で segfault することがある）。プロバイダは `QgsApplication.processingRegistry()` に直接登録する（`conftest.py` の `qgis_plugin_path` フィクスチャ参照）。

### プラグインのライフサイクル

- `Plugin.initGui` で QGIS に追加したもの（アクション、ツールバー、プロバイダ等）は、必ず `Plugin.unload` で対応する remove を行う。
- 追加・削除のべき等性をフラグで担保する。プロバイダ登録のリファレンス実装：

  ```python
  if registry.providerById(self._provider.id()) is None:
      registry.addProvider(self._provider)
      self._provider_added = True
  ```

  `unload` 側では `self._provider_added` を見てから削除する。新たに global 登録を追加するときも同じパターンを踏襲する。

### ディレクトリと命名

- ルート直下が QGIS にとってのプラグインパッケージそのもの。新しい関心領域は既存のサブパッケージに無理に押し込まず、兄弟ディレクトリを追加する（例：カスタム式なら `expressions/`）。
- ファイル／モジュールは `snake_case.py`、クラスは `PascalCase`、関数・メソッドは `snake_case`、定数は `UPPER_SNAKE_CASE`。
- Qt のオーバーライドメソッド（`initAlgorithm`、`processAlgorithm`、`initGui`、`unload` 等）は Qt 側の casing を維持する。
- テストファイルは `test_<対象>.py`、テストクラスは `TestXxx`。
