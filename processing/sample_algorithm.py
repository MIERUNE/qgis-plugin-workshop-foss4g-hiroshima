from qgis import processing
from qgis.core import (
    Qgis,
    QgsProcessingAlgorithm,
    QgsProcessingFeedback,
    QgsProcessingParameterFeatureSink,
    QgsProcessingParameterFeatureSource,
    QgsProcessingParameterNumber,
)


class SampleAlgorithm(QgsProcessingAlgorithm):
    INPUT = "INPUT"
    DISTANCE = "DISTANCE"
    OUTPUT = "OUTPUT"

    def initAlgorithm(self, config=None):
        self.addParameter(
            QgsProcessingParameterFeatureSource(
                self.INPUT,
                "Input layer",
                [Qgis.ProcessingSourceType.VectorAnyGeometry],
            )
        )
        self.addParameter(
            QgsProcessingParameterNumber(
                self.DISTANCE,
                "Buffer distance",
                type=QgsProcessingParameterNumber.Type.Double,  # pyright: ignore[reportAttributeAccessIssue]
                defaultValue=1.0,
            )
        )
        self.addParameter(
            QgsProcessingParameterFeatureSink(
                self.OUTPUT,
                "Output layer",
            )
        )

    def processAlgorithm(self, parameters, context, feedback: QgsProcessingFeedback):
        distance = self.parameterAsDouble(parameters, self.DISTANCE, context)

        result = processing.run(
            "native:buffer",
            {
                "INPUT": parameters[self.INPUT],
                "DISTANCE": distance,
                "SEGMENTS": 5,
                "END_CAP_STYLE": 0,
                "JOIN_STYLE": 0,
                "MITER_LIMIT": 2,
                "DISSOLVE": False,
                "OUTPUT": parameters[self.OUTPUT],
            },
            context=context,
            feedback=feedback,
            is_child_algorithm=True,
        )
        assert result is not None

        return {self.OUTPUT: result["OUTPUT"]}

    def name(self):
        return "sample_algorithm"

    def displayName(self):
        return "Sample Algorithm"

    def group(self):
        return "Sample"

    def groupId(self):
        return "sample"

    def createInstance(self):
        return SampleAlgorithm()
