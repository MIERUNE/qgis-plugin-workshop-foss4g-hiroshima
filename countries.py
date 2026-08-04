"""Logic to find the countries that fall within a given extent."""

import os
from typing import Optional

from qgis.core import (
    QgsCoordinateReferenceSystem,
    QgsCoordinateTransform,
    QgsFeatureRequest,
    QgsProject,
    QgsRectangle,
    QgsVectorLayer,
)

# data/ne_countries.gpkg ships at the plugin root.
DATA_PATH = os.path.join(os.path.dirname(__file__), "data", "ne_countries.gpkg")
LAYER_NAME = "ne_countries"
NAME_FIELD = "NAME_LONG"


def load_countries_layer() -> QgsVectorLayer:
    """Load the bundled ne_countries layer."""
    uri = f"{DATA_PATH}|layername={LAYER_NAME}"
    return QgsVectorLayer(uri, LAYER_NAME, "ogr")


def countries_in_extent(
    extent: QgsRectangle,
    extent_crs: QgsCoordinateReferenceSystem,
    layer: Optional[QgsVectorLayer] = None,
) -> list[str]:
    """Return the country names (NAME_LONG) intersecting the extent, sorted.

    The extent is reprojected when its CRS differs from the layer's CRS.
    """
    if layer is None:
        layer = load_countries_layer()
    if not layer.isValid():
        raise RuntimeError(f"Could not load layer: {DATA_PATH}")

    layer_crs = layer.crs()
    if extent_crs.isValid() and extent_crs != layer_crs:
        transform = QgsCoordinateTransform(
            extent_crs, layer_crs, QgsProject.instance()
        )
        extent = transform.transformBoundingBox(extent)

    request = QgsFeatureRequest().setFilterRect(extent)
    names = set()
    for feature in layer.getFeatures(request):
        geometry = feature.geometry()
        # setFilterRect only tests bounding boxes, so confirm a real intersection.
        if not geometry.isNull() and geometry.intersects(extent):
            name = feature[NAME_FIELD]
            if name:
                names.add(str(name))
    return sorted(names)
