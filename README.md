# qgis-plugin-template

QGIS3.x プラグイン開発のひな形

## What is this?

QGISプラグインの開発を始めるためのひな形です

- PythonコードによるUI実装
- ProcessingAlgorithmのボイラープレート
- 自動テスト
- 静的型チェック

## Preparation

以下の手順で、型チェックが可能となり、VSCode上でQGIS Python APIのコード補完が有効になります。

1. `uv sync`
2. VSCodeでQGIS Python APIのコード補完を有効にする
    1. `pyrightconfig.json` の `extraPaths` を自身のQGISインストール先に合わせて編集する
        - **macOS**: `/Applications/QGIS.app/Contents/Resources/python3.XX/site-packages`
        - **Windows (OSGeo4W)**: ??
3. VSCodeのPythonインタプリタを、`uv sync`で構築された仮想環境のPythonに設定する

## テストの実行

テストはQGIS Pythonランタイムに依存するため、Dockerを利用して実行します:

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

### Processingアルゴリズムのテスト

- `native:xxx`はテスト可能
- `qgis:xxx`はおそらくテスト可能
- `gdal:xxx`はテスト不可能

> Recommend: 頑張りすぎない

## Tips

### Pythonバージョン

macOSのQGIS3.40はPython3.9を内臓していて、これが現状最も古いPythonバージョンです。このバージョンのQGISのサポートが必要なら、3.9のシンタックスで実装する必要があります。

### PyQt5/6の両対応

- このリポジトリで構築される開発環境は、PyQt5をベースとしています。これはQGISに内臓されているPythonスタブが依然としてPyQt5に依存しているためです。
- ほとんどのAPIはPyQt5/6で共通ですが、一部で相違があります。なので、PyQt5のAPIで実装するとPyQt6環境で動作しなくなることがあります（逆も同様）。どちらの環境でも動作させる必要がある場合は必要に応じて互換レイヤーを導入しましょう。

### 型チェック

QGIS Python APIの型定義は完全ではないので、適宜`# type: ignore`を利用して型チェックを回避せざるを得ませんが、型定義が存在する部分については積極的に型チェックを有効にして、コードの品質を保ちましょう。

#### 一部の型が当たらない問題

QGISが内蔵しているPythonの型スタブに問題があり、`QAction`など一部のクラスに型が当たりません。

### relative import

- 関心ごとに応じて、モジュールを分割しましょう（例：`ui`モジュール）
- `relative import`の利用を推奨します：以下のような絶対パスによるインポートは[Plugin Reloader](https://plugins.qgis.org/plugins/plugin_reloader/)で変更が反映されなくなることがあります（[Issue #16](https://github.com/MIERUNE/qgis-plugin-template/issues/16)）

```python
from child import Child # not good
from .child import Child # better
```
