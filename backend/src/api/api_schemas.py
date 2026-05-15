from pydantic import BaseModel, ConfigDict


class AnalyseRequest(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    user_message: str | None


class AnalyseResponse(BaseModel):
    message: str
