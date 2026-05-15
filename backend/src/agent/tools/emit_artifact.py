import asyncio
import json
import os
import time

from session_store import get_queue


def make_emit_artifact(session_id: str):
    """
    Фабрика — создаёт tool привязанный к конкретной сессии.
    Вызывается при старте агента для каждого запроса.
    """

    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

    def emit_artifact(type: str, payload: str, title: str = None) -> str:
        """
        Send a completed artifact to the user interface immediately.

        Call this after every completed result — do NOT accumulate and send at the end.

        Args:
            type: One of: 'thinking', 'text', 'code', 'chart', 'chart_image', 'image', 'table', 'error'
            payload:
                - thinking → plain text, what you are about to do
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
        if isinstance(payload, bytes):
            payload = payload.decode("utf-8", errors="replace")
        payload = str(payload).strip()

        event = {
            "type": type,
            "payload": payload,
            "title": title,
        }

        queue = get_queue(session_id)

        try:
            loop.call_soon_threadsafe(queue.put_nowait, event)
            print(f"[ARTIFACT] Event queued successfully for session {session_id}")
            return f"artifact '{type}' sent to user"
        except Exception as e:
            print(f"[ARTIFACT] ERROR queuing event: {str(e)}")
            import traceback

            traceback.print_exc()
            return f"Failed to send artifact: {str(e)}"

    return emit_artifact
