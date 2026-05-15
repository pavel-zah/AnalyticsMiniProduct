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
    # КРИТИЧНО: Получаем event loop в главном потоке и сохраняем в closure
    # Агент будет работать в thread pool executor и не сможет получить loop
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        # Если нет running loop, создаём новый
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
        
        event = {
            "type": type,
            "payload": payload,
            "title": title,
        }

        queue = get_queue(session_id)

        try:
            # Используем loop из closure, а не пытаемся получить его из worker thread
            loop.call_soon_threadsafe(queue.put_nowait, event)
            print(f"[ARTIFACT] ✅ Event queued successfully for session {session_id}")
            return f"✅ artifact '{type}' sent to user"
        except Exception as e:
            print(f"[ARTIFACT] ❌ ERROR queuing event: {str(e)}")
            import traceback
            traceback.print_exc()
            return f"❌ Failed to send artifact: {str(e)}"

    return emit_artifact
