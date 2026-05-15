from collections.abc import Callable
import time
from pathlib import Path
from typing import Any, Dict

from daytona import Daytona, DaytonaConfig
from deepagents import create_deep_agent
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_daytona import DaytonaSandbox
from langgraph.store.memory import InMemoryStore

from src.agent.llm import get_instruct_llm, get_llm
from src.agent.prompts import PROMPT_INJECTION_SYSTEM_PROMPT, SYSTEM_PROMPT
from src.agent.schemas import PromptInjection
from src.core.config import get_settings

settings = get_settings()


def get_agent_resources(emit: Callable):
    """Передаём emit как tool в агента."""
    config = DaytonaConfig(api_key=settings.deytona_api_key)
    daytona = Daytona(config)
    sandbox = daytona.create()
    backend = DaytonaSandbox(sandbox=sandbox)

    deep_agent = create_deep_agent(
        model=get_llm(),
        backend=backend,
        store=InMemoryStore(),
        system_prompt=SYSTEM_PROMPT,
        tools=[emit],  # ← смотри как deepagent принимает кастомные tools
        debug=False,
    )
    return deep_agent, sandbox, backend, daytona


def check_prompt_injection(user_message: str) -> PromptInjection:
    """Провяет на наличие промпт инъекции в пользовательское сообщение"""

    model = get_instruct_llm()

    structured_model = model.with_structured_output(PromptInjection)

    messages = [
        SystemMessage(content=PROMPT_INJECTION_SYSTEM_PROMPT),
        HumanMessage(content=user_message),
    ]

    response = structured_model.invoke(messages)

    return response


def _emit_chart_image(
    *,
    emit: Callable,
    sandbox,
    session_id: str,
    sandbox_path: str,
    title: str | None,
) -> str:
    if not sandbox_path:
        return emit(type="error", payload="Пустой путь к изображению графика.", title="Ошибка графика")

    if not sandbox_path.startswith("/"):
        sandbox_path = f"/home/daytona/{sandbox_path}"

    # repo layout: backend/src/agent/agent.py → parents[3] == backend/
    artifacts_dir = Path(__file__).resolve().parents[3] / "uploaded_files" / "artifacts" / session_id
    artifacts_dir.mkdir(parents=True, exist_ok=True)

    filename = Path(sandbox_path).name
    local_path = artifacts_dir / filename

    try:
        print(f"[CHART_IMAGE] Downloading from sandbox: {sandbox_path} -> {local_path}")
        sandbox.fs.download_file(sandbox_path, str(local_path))
        print(f"[CHART_IMAGE] Downloaded OK, exists={local_path.exists()}")
    except Exception as e:
        return emit(
            type="error",
            payload=f"Не удалось скачать изображение графика из sandbox: {str(e)}",
            title="Ошибка графика",
        )

    image_url = f"/v1/artifacts/{session_id}/{filename}"
    return emit(type="image", payload=image_url, title=title)


def analyze_csv(
    local_csv_path: str,
    sandbox_csv_path: str,
    user_message: str | None,
    session_id: str,  # ← новый параметр
    emit: Callable,
) -> Dict[str, Any]:
    deep_agent = None
    sandbox = None
    daytona = None

    try:
        if user_message:
            injection_result = check_prompt_injection(user_message)
            if injection_result.injection_detected:
                return {
                    "error": "Промпт инъекция обнаружена.",
                    "injection_pattern": injection_result.detected_patterns,
                }

        def emit_artifact(type: str, payload: str, title: str | None = None) -> str:
            """Send a completed artifact to the user interface immediately."""
            if type == "chart_image":
                return _emit_chart_image(
                    emit=emit,
                    sandbox=sandbox,
                    session_id=session_id,
                    sandbox_path=payload,
                    title=title,
                )

            if type == "image" and payload:
                is_local_png = payload.lower().endswith(".png")
                is_sandbox_path = payload.startswith("/home/daytona/")
                is_backend_url = payload.startswith("/v1/")
                is_http_url = payload.startswith("http://") or payload.startswith("https://")
                if (is_local_png or is_sandbox_path) and not is_backend_url and not is_http_url:
                    return _emit_chart_image(
                        emit=emit,
                        sandbox=sandbox,
                        session_id=session_id,
                        sandbox_path=payload,
                        title=title,
                    )

            return emit(type=type, payload=payload, title=title)

        deep_agent, sandbox, backend, daytona = get_agent_resources(emit_artifact)

        local_path = Path(local_csv_path)
        if not local_path.exists():
            return {"error": f"Локальный файл {local_csv_path} не найден."}

        try:
            sandbox.fs.upload_file(str(local_path), sandbox_csv_path)
        except Exception as e:
            return {"error": f"Не удалось загрузить файл в Daytona: {str(e)}"}

        file_info = f"\nCSV-файл загружен по пути: {sandbox_csv_path}\nВыполни полный цикл анализа строго по этапам из системной инструкции.\n"
        full_user_message = (user_message or "") + file_info

        last_error: Exception | None = None
        for attempt in range(1, 4):
            try:
                deep_agent.invoke(
                    {"messages": [{"role": "user", "content": full_user_message}]},
                )
                last_error = None
                break
            except Exception as e:
                last_error = e
                error_text = str(e)
                is_transient = "502" in error_text or "Upstream" in error_text or "Response validation failed" in error_text
                if attempt < 3 and is_transient:
                    time.sleep(2 * attempt)
                    continue
                break

        if last_error is not None:
            return {"error": f"Ошибка в процессе работы агента: {str(last_error)}"}

        # Архив больше не нужен — всё отправлено через emit
        return {"status": "success"}

    except Exception as e:
        return {"error": f"Непредвиденная системная ошибка: {str(e)}"}
