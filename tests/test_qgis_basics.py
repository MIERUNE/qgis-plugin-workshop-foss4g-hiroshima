import pytest
from qgis.core import (
    Qgis,
    QgsCoordinateReferenceSystem,
    QgsVectorLayer,
)

pytestmark = pytest.mark.usefixtures("qgis_plugin_path")


class TestQgisBasic:
    def test_memory_layer_creation(self):
        """A memory layer should be created correctly."""
        layer = QgsVectorLayer("Point?crs=EPSG:4326", "test", "memory")
        assert layer.isValid()

    def test_memory_layer_geometry_type(self):
        """A memory layer should have the correct geometry type."""
        point = QgsVectorLayer("Point?crs=EPSG:4326", "p", "memory")
        line = QgsVectorLayer("LineString?crs=EPSG:4326", "l", "memory")
        polygon = QgsVectorLayer("Polygon?crs=EPSG:4326", "pg", "memory")

        assert point.wkbType() == Qgis.WkbType.Point
        assert line.wkbType() == Qgis.WkbType.LineString
        assert polygon.wkbType() == Qgis.WkbType.Polygon

    def test_crs(self):
        """CRS creation and comparison should work correctly."""
        crs_4326 = QgsCoordinateReferenceSystem("EPSG:4326")
        crs_3857 = QgsCoordinateReferenceSystem("EPSG:3857")

        assert crs_4326.isValid()
        assert crs_3857.isValid()
        assert crs_4326 != crs_3857

    def test_memory_layer_with_fields(self):
        """A memory layer with fields should be created correctly."""
        layer = QgsVectorLayer(
            "Point?crs=EPSG:4326&field=name:string&field=value:integer",
            "test",
            "memory",
        )
        assert layer.isValid()
        assert layer.fields().count() == 2
        assert layer.fields().at(0).name() == "name"
        assert layer.fields().at(1).name() == "value"
