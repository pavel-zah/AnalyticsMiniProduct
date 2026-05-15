from functools import lru_cache

from langchain_openrouter import ChatOpenRouter

from ..core.config import settings


class LLMFactory:
    """Фабрика для создания LLM на основе конфигурации"""

    @staticmethod
    def create_openrouter_llm(model: str | None = None) -> ChatOpenRouter:
        """Создаёт OpenRouter LLM"""
        model = model or settings.openrouter_model

        return ChatOpenRouter(
            model=model,
            api_key=settings.openrouter_api_key,
            base_url=settings.openrouter_base_url,
            app_title=None,
            streaming=False,
        )


llm: ChatOpenRouter | None = None


@lru_cache(maxsize=1)
def get_llm() -> ChatOpenRouter:
    """
    Возвращает singleton инстанс LLM.
    Кешируется для переиспользования.

    Returns:
        Настроенный LLM
    """

    global llm

    if llm is None:
        llm = LLMFactory.create_openrouter_llm()
    return llm


instruct_llm: ChatOpenRouter | None = None


@lru_cache(maxsize=1)
def get_instruct_llm() -> ChatOpenRouter:
    """
    Возвращает singleton инстанс Instruct LLM.
    Кешируется для переиспользования.

    Returns:
        Настроенный Instruct LLM
    """

    global instruct_llm

    if instruct_llm is None:
        instruct_llm = LLMFactory.create_openrouter_llm(
            settings.openrouter_instuct_model
        )
    return instruct_llm
