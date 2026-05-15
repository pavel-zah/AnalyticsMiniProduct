import asyncio
import json
import os
import time
import uuid
from pathlib import Path
from typing import Dict

from fastapi import APIRouter, Form, HTTPException, UploadFile
from fastapi.responses import FileResponse, StreamingResponse

from src.agent.agent import analyze_csv

BASE_DIR = Path(__file__).resolve().parents[3]
UPLOAD_DIR = BASE_DIR / "uploaded_files"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
print(f"[ROUTER] UPLOAD_DIR initialized: {UPLOAD_DIR}")

ARTIFACTS_DIR = UPLOAD_DIR / "artifacts"
ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)
print(f"[ROUTER] ARTIFACTS_DIR initialized: {ARTIFACTS_DIR}")

router = APIRouter(prefix="/v1", tags=["Analysis task"])
print(f"[ROUTER] Router created with prefix=/v1")

_session_queues: Dict[str, asyncio.Queue] = {}


def _get_or_create_queue(session_id: str) -> asyncio.Queue:
    if session_id not in _session_queues:
        _session_queues[session_id] = asyncio.Queue()
    return _session_queues[session_id]


def _make_emit(session_id: str):
    """
    Фабрика emit_artifact, привязанная к сессии.
    Вызывается агентом синхронно — используем thread-safe put_nowait.
    """
    print(f"[EMIT] Creating emit function for session {session_id}")
    queue = _get_or_create_queue(session_id)
    # Получаем event loop в главном потоке и сохраняем в closure
    # Агент будет работать в thread pool executor и не сможет получить loop
    loop = asyncio.get_event_loop()
    print(f"[EMIT] ✓ Captured event loop: {loop}")

    def emit_artifact(type: str, payload: str, title: str = None) -> str:
        """
        Send a completed artifact to the user interface immediately.

        Call this after every completed result — do NOT accumulate and send at the end.

        Args:
            type: One of: 'thinking', 'text', 'code', 'chart', 'chart_image', 'image', 'table', 'error'
            payload:
                - thinking → plain text, what you are about to do (1-2 sentences)
                - text     → markdown string with analysis and conclusions
                - code     → raw Python code string that was executed
                - chart_image → sandbox file path to PNG image
                - image    → public URL to image on backend
                - table    → df.to_json(orient='records')
                - error    → error description and what you will try instead
            title: Optional display title shown above the artifact (in Russian)

        Returns:
            Confirmation string
        """

        if isinstance(payload, bytes):
            payload = payload.decode("utf-8", errors="replace")
        payload = str(payload).strip()

        event = {"type": type, "payload": payload, "title": title}
        try:
            loop.call_soon_threadsafe(queue.put_nowait, event)
            return f"artifact '{type}' sent"
        except Exception as e:
            import traceback

            traceback.print_exc()
            return f"❌ Failed: {str(e)}"

    return emit_artifact


@router.post("/analyse")
async def analyse_dataset(
    user_message: str = Form(default=""),
    file: UploadFile = None,
):
    try:
        if file is None:
            raise HTTPException(status_code=400, detail="File is required")

        if file.content_type != "text/csv":
            raise HTTPException(status_code=400, detail="Only CSV files are supported")

        session_id = str(uuid.uuid4())

        _get_or_create_queue(session_id)

        file_path = UPLOAD_DIR / f"{session_id}_{file.filename}"
        content = await file.read()

        with open(file_path, "wb") as buffer:
            buffer.write(content)

        asyncio.create_task(
            _run_agent_task(
                session_id=session_id,
                file_path=file_path,
                filename=file.filename,
                user_message=user_message,
            )
        )

        response = {"session_id": session_id}
        return response

    except HTTPException as e:
        raise
    except Exception as e:
        import traceback

        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Upload error: {str(e)}")


async def _run_agent_task(
    session_id: str,
    file_path: str,
    filename: str,
    user_message: str,
):
    """Background task for running agent analysis."""
    emit = _make_emit(session_id)
    queue = _get_or_create_queue(session_id)

    try:
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(
            None,
            lambda: analyze_csv(
                local_csv_path=str(file_path),
                sandbox_csv_path=f"/home/daytona/{filename}",
                user_message=user_message,
                session_id=session_id,
                emit=emit,
            ),
        )

        if result and "error" in result:
            queue.put_nowait(
                {
                    "type": "error",
                    "payload": result["error"],
                    "title": "Ошибка агента",
                }
            )

    except Exception as e:
        import traceback

        traceback.print_exc()
        queue.put_nowait(
            {
                "type": "error",
                "payload": f"Системная ошибка: {str(e)}",
                "title": None,
            }
        )

    finally:
        queue.put_nowait(
            {
                "type": "thinking",
                "payload": "Анализ завершён.",
                "title": None,
            }
        )

        try:
            for f in Path(UPLOAD_DIR).iterdir():
                if session_id in str(f):
                    f.unlink(missing_ok=True)
        except Exception:
            pass


@router.get("/stream/{session_id}")
async def stream_artifacts(session_id: str):
    if session_id not in _session_queues:
        raise HTTPException(status_code=404, detail="Session not found")

    queue = _session_queues[session_id]

    async def event_generator():
        event_count = 0
        try:
            while True:
                try:
                    event = await asyncio.wait_for(queue.get(), timeout=900.0)
                    event_count += 1
                except asyncio.TimeoutError:
                    yield f"data: {json.dumps({'type': 'error', 'payload': 'Timeout: анализ занял более 15 минут', 'title': None}, ensure_ascii=False)}\n\n"
                    break

                yield f"data: {json.dumps(event, ensure_ascii=False)}\n\n"

                if (
                    event.get("type") == "thinking"
                    and event.get("payload") == "Анализ завершён."
                ):
                    break

        except Exception:
            pass
        finally:
            _session_queues.pop(session_id, None)

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


@router.get("/artifacts/{session_id}/{filename}")
async def get_artifact_file(session_id: str, filename: str):
    safe_name = Path(filename).name
    file_path = ARTIFACTS_DIR / session_id / safe_name
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Artifact not found")

    print(f"[ARTIFACTS] 200: {file_path}")
    return FileResponse(str(file_path))
