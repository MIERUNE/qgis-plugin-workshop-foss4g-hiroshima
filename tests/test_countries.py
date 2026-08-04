import pytest
from plugin_dir.countries import (  # pyright: ignore[reportMissingImports]
    countries_in_extent,
    load_countries_layer,
)
from qgis.core import QgsCoordinateReferenceSystem, QgsRectangle

pytestmark = pytest.mark.usefixtures("qgis_plugin_path")

WGS84 = QgsCoordinateReferenceSystem("EPSG:4326")
WEB_MERCATOR = QgsCoordinateReferenceSystem("EPSG:3857")


class TestLoadCountriesLayer:
    def test_layer_is_valid(self):
        """The bundled gpkg layer should load."""
        layer = load_countries_layer()
        assert layer.isValid()
        assert layer.featureCount() == 258

    def test_name_field_exists(self):
        """The NAME_LONG field should exist."""
        layer = load_countries_layer()
        assert layer.fields().indexOf("NAME_LONG") >= 0


class TestCountriesInExtent:
    def test_extent_over_japan_returns_japan(self):
        """An extent over Japan should return Japan."""
        extent = QgsRectangle(138.0, 34.0, 141.0, 37.0)
        names = countries_in_extent(extent, WGS84)
        assert "Japan" in names

    def test_ocean_extent_returns_empty(self):
        """An extent over the ocean should return no countries."""
        extent = QgsRectangle(-140.0, -30.0, -139.0, -29.0)
        names = countries_in_extent(extent, WGS84)
        assert names == []

    def test_result_is_sorted_and_unique(self):
        """The result should be sorted and free of duplicates."""
        extent = QgsRectangle(5.0, 45.0, 10.0, 50.0)
        names = countries_in_extent(extent, WGS84)
        assert names == sorted(names)
        assert len(names) == len(set(names))
        assert len(names) > 1

    def test_extent_crs_is_transformed(self):
        """An extent in a different CRS should be reprojected (Tokyo in Web Mercator)."""
        # Tokyo area (lon 139.7, lat 35.7) expressed in EPSG:3857
        extent = QgsRectangle(15_500_000, 4_200_000, 15_600_000, 4_300_000)
        names = countries_in_extent(extent, WEB_MERCATOR)
        assert "Japan" in names
