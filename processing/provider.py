from qgis.core import QgsProcessingProvider

from .sample_algorithm import SampleAlgorithm


class SampleProvider(QgsProcessingProvider):
    def loadAlgorithms(self):
        self.addAlgorithm(SampleAlgorithm())

    def id(self):
        return "sample"

    def name(self):
        return "Sample"

    def longName(self):
        return "Sample Provider"
