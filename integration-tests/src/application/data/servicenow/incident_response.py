from pydantic import BaseModel, Field


class IncidentResponseResult(BaseModel):
    state: str = "inserted"
    number: int = hash("any_result_number")


class IncidentResponse(BaseModel):
    result: IncidentResponseResult = Field(default_factory=lambda: IncidentResponseResult())
