import pytest

pytestmark = pytest.mark.usefixtures("qgis_plugin_path")


class TestProcessing:
    def test_native_algorithm(self):
        """native:xxxのアルゴリズムが実行できること"""
        from qgis.core import (
            Qgis,
            QgsFeature,
            QgsGeometry,
            QgsPointXY,
            QgsProcessingContext,
            QgsProcessingFeedback,
            QgsVectorLayer,
        )

        import processing as qgis_processing

        layer = QgsVectorLayer("Point?crs=EPSG:4326", "test", "memory")
        dp = layer.dataProvider()
        assert dp is not None
        f = QgsFeature()
        f.setGeometry(QgsGeometry.fromPointXY(QgsPointXY(1.0, 2.0)))
        dp.addFeature(f)

        context = QgsProcessingContext()
        feedback = QgsProcessingFeedback()

        result = qgis_processing.run(  # pyright: ignore[reportAttributeAccessIssue]
            "native:buffer",
            {
                "INPUT": layer,
                "DISTANCE": 1.0,
                "SEGMENTS": 5,
                "END_CAP_STYLE": 0,
                "JOIN_STYLE": 0,
                "MITER_LIMIT": 2,
                "DISSOLVE": False,
                "OUTPUT": "memory:",
            },
            context=context,
            feedback=feedback,
        )

        output_layer = result["OUTPUT"]
        assert isinstance(output_layer, QgsVectorLayer)
        assert output_layer.featureCount() == 1
        assert output_layer.geometryType() == Qgis.GeometryType.Polygon

    def test_qgis_algorithm(self):
        """qgis:xxxのアルゴリズムが実行できること"""
        from qgis.core import (
            QgsProcessingContext,
            QgsProcessingFeedback,
            QgsRectangle,
            QgsVectorLayer,
        )

        import processing as qgis_processing

        context = QgsProcessingContext()
        feedback = QgsProcessingFeedback()

        result = qgis_processing.run(  # pyright: ignore[reportAttributeAccessIssue]
            "qgis:randompointsinextent",
            {
                "EXTENT": QgsRectangle(0, 0, 10, 10),
                "POINTS_NUMBER": 5,
                "MIN_DISTANCE": 0,
                "TARGET_CRS": "EPSG:4326",
                "OUTPUT": "memory:",
            },
            context=context,
            feedback=feedback,
        )

        output_layer = result["OUTPUT"]
        assert isinstance(output_layer, QgsVectorLayer)
        assert output_layer.featureCount() == 5

    def test_user_defined_algorithm(self):
        """ユーザー定義のプロセッシング(SampleAlgorithm)が実行できること"""
        from plugin_dir.processing.provider import SampleProvider  # type: ignore
        from plugin_dir.processing.sample_algorithm import (  # type: ignore
            SampleAlgorithm,
        )
        from qgis.core import (
            Qgis,
            QgsApplication,
            QgsFeature,
            QgsGeometry,
            QgsPointXY,
            QgsProcessingContext,
            QgsProcessingFeedback,
            QgsVectorLayer,
        )

        import processing as qgis_processing

        # メタデータの検証
        alg = SampleAlgorithm()
        assert alg.name() == "sample_algorithm"
        assert alg.displayName() == "Sample Algorithm"
        assert alg.group() == "Sample"
        assert alg.groupId() == "sample"

        # 入力レイヤーを作成
        layer = QgsVectorLayer("Point?crs=EPSG:4326", "test", "memory")
        dp = layer.dataProvider()
        assert dp is not None
        f = QgsFeature()
        f.setGeometry(QgsGeometry.fromPointXY(QgsPointXY(1.0, 2.0)))
        dp.addFeature(f)

        # alg.run() で実行
        alg.initAlgorithm()
        context = QgsProcessingContext()
        feedback = QgsProcessingFeedback()

        output, success = alg.run(
            {"INPUT": layer, "DISTANCE": 1.0, "OUTPUT": "memory:"},
            context,
            feedback,
        )
        assert success
        output_layer = context.getMapLayer(output["OUTPUT"])
        assert output_layer is not None
        assert isinstance(output_layer, QgsVectorLayer)
        assert output_layer.featureCount() == 1
        assert output_layer.geometryType() == Qgis.GeometryType.Polygon

        # processing.run() で実行
        registry = QgsApplication.processingRegistry()
        assert registry is not None
        if not registry.providerById("sample"):
            registry.addProvider(SampleProvider())

        context2 = QgsProcessingContext()
        feedback2 = QgsProcessingFeedback()

        result = qgis_processing.run(  # pyright: ignore[reportAttributeAccessIssue]
            "sample:sample_algorithm",
            {"INPUT": layer, "DISTANCE": 1.0, "OUTPUT": "memory:"},
            context=context2,
            feedback=feedback2,
        )
        output_layer2 = result["OUTPUT"]
        assert isinstance(output_layer2, QgsVectorLayer)
        assert output_layer2.featureCount() == 1
        assert output_layer2.geometryType() == Qgis.GeometryType.Polygon
