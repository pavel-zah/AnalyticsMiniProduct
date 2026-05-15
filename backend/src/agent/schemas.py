from pydantic import BaseModel, Field


class PromptInjection(BaseModel):
    """Prompt injection detection result."""

    injection_detected: bool = Field(
        description="True если обнаружена попытка prompt injection, иначе False"
    )
    confidence: float = Field(
        default=0.0, description="Уровень уверенности в обнаружении (0.0-1.0)"
    )
    detected_patterns: list[str] = Field(
        default_factory=list, description="Список обнаруженных подозрительных паттернов"
    )
