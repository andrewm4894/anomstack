from typing import List

from pydantic import BaseModel, Field


class Anomaly(BaseModel):
    anomaly_timestamp: str = Field(
        ...,
        description="The timestamp where the anomaly was detected."
    )
    anomaly_explanation: str = Field(
        ...,
        description="A brief explanation of why this point is considered anomalous."
    )

class DetectAnomaliesResponse(BaseModel):
    anomalies: List[Anomaly] = Field(
        ...,
        description="A list of detected anomalies, if any, with their timestamps and explanations."
    )

detect_anomalies_schema = DetectAnomaliesResponse.schema()