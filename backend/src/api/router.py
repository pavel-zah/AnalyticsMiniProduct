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
        print(f"[QUEUE] Creating new queue for session {session_id}")
        _session_queues[session_id] = asyncio.Queue()
    return _session_queues[session_id]


def _make_emit(session_id: str):
    """
    Фабрика emit_artifact, привязанная к сессии.
    Вызывается агентом синхронно — используем thread-safe put_nowait.
    """
    print(f"[EMIT] Creating emit function for session {session_id}")
    queue = _get_or_create_queue(session_id)
    # КРИТИЧНО: Получаем event loop в главном потоке и сохраняем в closure
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
                - chart    → MUST be fig.to_json() output, nothing else (legacy)
                - chart_image → sandbox file path to PNG image
                - image    → public URL to image on backend
                - table    → df.to_json(orient='records')
                - error    → error description and what you will try instead
            title: Optional display title shown above the artifact (in Russian)

        Returns:
            Confirmation string
        """
        # Ensure payload is a clean string
        if isinstance(payload, bytes):
            payload = payload.decode('utf-8', errors='replace')
        payload = str(payload).strip()
        
        # Логируем что агент пытается отправить артефакт
        payload_preview = payload[:100].replace('\n', ' ') if payload else ''
        payload_end = payload[-50:].replace('\n', ' ') if payload else ''
        print(f"\n[ARTIFACT] 📤 Agent sending artifact:")
        print(f"[ARTIFACT]    type: {type}")
        print(f"[ARTIFACT]    title: {title if title else '(no title)'}")
        print(f"[ARTIFACT]    payload_size: {len(payload)} chars")
        print(f"[ARTIFACT]    payload_preview: {payload_preview}{'...' if len(payload) > 100 else ''}")
        print(f"[ARTIFACT]    payload_end: ...{payload_end}")
        
        # Для chart-артефактов проверяем валидность JSON
        if type == 'chart':
            try:
                import json
                json.loads(payload)
                print(f"[ARTIFACT] ✓ Payload is valid JSON")
            except json.JSONDecodeError as e:
                print(f"[ARTIFACT] ⚠️ WARNING: Invalid JSON at position {e.pos}: {str(e)}")
                # Try common fixes
                fixed = False
                
                # Fix 1: Remove trailing newlines/spaces (already done above)
                # Fix 2: Remove extra closing brace if present
                if not fixed and payload.count('}') > payload.count('{'):
                    test_payload = payload[:-1]
                    try:
                        import json
                        json.loads(test_payload)
                        print(f"[ARTIFACT] ✓ Fixed: removed extra closing brace")
                        payload = test_payload
                        fixed = True
                    except:
                        pass
                
                # Fix 3: Try to remove common trailing garbage
                if not fixed and payload[-1] not in '}]"':
                    for i in range(1, min(6, len(payload))):
                        test_payload = payload[:-i]
                        try:
                            import json
                            json.loads(test_payload)
                            print(f"[ARTIFACT] ✓ Fixed: removed trailing {i} char(s)")
                            payload = test_payload
                            fixed = True
                            break
                        except:
                            pass
                
                if not fixed:
                    print(f"[ARTIFACT] ⚠️ Could not auto-fix JSON, sending as-is for frontend validation")
                    # Сохраняем для анализа
                    debug_dir = os.path.join(os.path.dirname(__file__), '../../..', 'debug_artifacts')
                    os.makedirs(debug_dir, exist_ok=True)
                    debug_path = os.path.join(debug_dir, f"invalid_chart_{session_id}_{int(time.time())}.json")
                    try:
                        with open(debug_path, 'w', encoding='utf-8') as f:
                            f.write(payload)
                        print(f"[ARTIFACT] 💾 Saved invalid JSON to {debug_path}")
                    except Exception as debug_e:
                        print(f"[ARTIFACT] ⚠️ Could not save debug file: {debug_e}")
        
        event = {"type": type, "payload": payload, "title": title}
        try:
            # Используем loop из closure, а не пытаемся получить его из worker thread
            loop.call_soon_threadsafe(queue.put_nowait, event)
            print(f"[ARTIFACT] ✅ Event queued successfully for session {session_id}")
            return f"✅ artifact '{type}' sent"
        except Exception as e:
            print(f"[ARTIFACT] ❌ ERROR queuing event: {str(e)}")
            import traceback
            traceback.print_exc()
            return f"❌ Failed: {str(e)}"

    return emit_artifact


@router.post("/analyse")
async def analyse_dataset(
    user_message: str = Form(default=""),
    file: UploadFile = None,
):
    print("\n" + "=" * 80)
    print("[ROUTER] /v1/analyse POST called")
    print("=" * 80)
    print(f"[ROUTER] File: {file}")
    print(f"[ROUTER] Filename: {file.filename if file else 'None'}")
    print(f"[ROUTER] Content-Type: {file.content_type if file else 'None'}")
    print(f"[ROUTER] Message: {user_message[:100] if user_message else 'None'}")
    
    try:
        if file is None:
            print(f"[ROUTER] ERROR: file is None")
            raise HTTPException(status_code=400, detail="File is required")
        
        if file.content_type != "text/csv":
            print(f"[ROUTER] ERROR: Invalid content type: {file.content_type}")
            raise HTTPException(status_code=400, detail="Only CSV files are supported")

        print(f"[ROUTER] ✓ File validation passed")
        
        session_id = str(uuid.uuid4())
        print(f"[ROUTER] ✓ Session created: {session_id}")
        
        _get_or_create_queue(session_id)
        print(f"[ROUTER] ✓ Queue created")

        file_path = UPLOAD_DIR / f"{session_id}_{file.filename}"
        print(f"[ROUTER] Reading file content...")
        content = await file.read()
        print(f"[ROUTER] ✓ File size: {len(content)} bytes")
        
        print(f"[ROUTER] Saving file to: {file_path}")
        with open(file_path, "wb") as buffer:
            buffer.write(content)
        print(f"[ROUTER] ✓ File saved")

        print(f"[ROUTER] Creating background task...")
        asyncio.create_task(
            _run_agent_task(
                session_id=session_id,
                file_path=file_path,
                filename=file.filename,
                user_message=user_message,
            )
        )
        print(f"[ROUTER] ✓ Background task started")

        response = {"session_id": session_id}
        print(f"[ROUTER] Returning: {response}")
        print("=" * 80 + "\n")
        return response
        
    except HTTPException as e:
        print(f"[ROUTER] HTTPException: {e.status_code} - {e.detail}")
        print("=" * 80 + "\n")
        raise
    except Exception as e:
        print(f"[ROUTER] Exception: {str(e)}")
        import traceback
        traceback.print_exc()
        print("=" * 80 + "\n")
        raise HTTPException(status_code=500, detail=f"Upload error: {str(e)}")


async def _run_agent_task(
    session_id: str,
    file_path: str,
    filename: str,
    user_message: str,
):
    """Background task for running agent analysis."""
    print(f"\n[AGENT_TASK] Starting for session {session_id}")
    emit = _make_emit(session_id)
    queue = _get_or_create_queue(session_id)
    print(f"[AGENT_TASK] ✓ Emit created")

    try:
        print(f"[AGENT_TASK] Running analyze_csv in executor...")
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
        print(f"[AGENT_TASK] ✓ analyze_csv returned: {result}")

        if result and "error" in result:
            print(f"[AGENT_TASK] ERROR: {result['error']}")
            queue.put_nowait({
                "type": "error",
                "payload": result["error"],
                "title": "Ошибка агента",
            })

    except Exception as e:
        print(f"[AGENT_TASK] Exception: {str(e)}")
        import traceback
        traceback.print_exc()
        queue.put_nowait({
            "type": "error",
            "payload": f"Системная ошибка: {str(e)}",
            "title": None,
        })

    finally:
        print(f"[AGENT_TASK] Sending completion signal")
        queue.put_nowait({
            "type": "thinking",
            "payload": "Анализ завершён.",
            "title": None,
        })
        print(f"[AGENT_TASK] ✓ Completed for session {session_id}")
        
        # Cleanup: удаляем ТОЛЬКО файлы текущей сессии
        print(f"[AGENT_TASK] Cleaning up files for session {session_id}")
        try:
            for f in Path(UPLOAD_DIR).iterdir():
                if session_id in str(f):
                    f.unlink(missing_ok=True)
                    print(f"[AGENT_TASK] Deleted: {f}")
        except Exception as cleanup_error:
            print(f"[AGENT_TASK] Cleanup error: {cleanup_error}")
        print(f"[AGENT_TASK] ✓ Cleanup done\n")


@router.get("/stream/{session_id}")
async def stream_artifacts(session_id: str):
    print(f"\n[STREAM] /v1/stream/{session_id} called")
    if session_id not in _session_queues:
        print(f"[STREAM] ERROR: Session not found")
        raise HTTPException(status_code=404, detail="Session not found")

    print(f"[STREAM] Session found, starting stream")
    queue = _session_queues[session_id]

    async def event_generator():
        print(f"[STREAM] event_generator started for {session_id}")
        event_count = 0
        try:
            while True:
                try:
                    event = await asyncio.wait_for(queue.get(), timeout=900.0)
                    event_count += 1
                    print(f"[STREAM] Event #{event_count}: {event.get('type')}")
                except asyncio.TimeoutError:
                    print(f"[STREAM] Timeout (15 minutes)")
                    yield f"data: {json.dumps({'type': 'error', 'payload': 'Timeout: анализ занял более 15 минут', 'title': None}, ensure_ascii=False)}\n\n"
                    break

                yield f"data: {json.dumps(event, ensure_ascii=False)}\n\n"

                if event.get("type") == "thinking" and event.get("payload") == "Анализ завершён.":
                    print(f"[STREAM] Completion signal received")
                    break

        except Exception as e:
            print(f"[STREAM] Exception: {str(e)}")
        finally:
            print(f"[STREAM] Cleaning up (sent {event_count} events)")
            _session_queues.pop(session_id, None)
            print(f"[STREAM] ✓ Queue closed for session {session_id}\n")

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
        print(f"[ARTIFACTS] 404: {file_path} (requested filename={filename})")
        raise HTTPException(status_code=404, detail="Artifact not found")

    print(f"[ARTIFACTS] 200: {file_path}")
    return FileResponse(str(file_path))
