"""Small local web chat for the Somali-first assistant.

The server binds to localhost by default. It is intentionally dependency-free
and keeps one in-memory conversation per process for the first MVP.
"""

from __future__ import annotations

import argparse
import json
import threading
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

from .model import ModelConfigurationError, ModelRequestError, OpenAIResponsesAdapter
from .pipeline import ConversationSession, SomaliAssistant


CHAT_HTML = r'''<!doctype html>
<html lang="so">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Somali AI</title>
<style>
:root{font-family:system-ui,-apple-system,sans-serif;color-scheme:light dark}
body{margin:0;background:Canvas;color:CanvasText}.app{max-width:850px;margin:auto;height:100vh;display:flex;flex-direction:column}
header{padding:16px 18px;border-bottom:1px solid color-mix(in srgb,CanvasText 16%,transparent);display:flex;justify-content:space-between;align-items:center}
header strong{font-size:1.1rem}.chat{flex:1;overflow:auto;padding:22px 16px}.msg{max-width:78%;padding:12px 14px;border-radius:16px;margin:10px 0;white-space:pre-wrap;line-height:1.45}.user{margin-left:auto;background:color-mix(in srgb,AccentColor 22%,Canvas)}.ai{background:color-mix(in srgb,CanvasText 9%,Canvas)}
form{display:flex;gap:8px;padding:12px 14px 18px;border-top:1px solid color-mix(in srgb,CanvasText 16%,transparent)}textarea{flex:1;resize:none;min-height:48px;max-height:150px;padding:12px;border-radius:14px;border:1px solid color-mix(in srgb,CanvasText 24%,transparent);font:inherit}button{border:0;border-radius:12px;padding:10px 15px;font:inherit;cursor:pointer}.send{background:AccentColor;color:white}.meta{font-size:.76rem;opacity:.65;margin:2px 4px}.status{padding:0 16px 8px;font-size:.82rem;opacity:.7}
</style>
</head>
<body><main class="app">
<header><strong>Somali AI v0.1</strong><button id="clear">Wadahadal cusub</button></header>
<section id="chat" class="chat"><div class="msg ai">Salaan. Maxaan kuu qaban karaa?</div></section>
<div id="status" class="status"></div>
<form id="form"><textarea id="input" aria-label="Fariin" placeholder="Qor fariintaada…" required></textarea><button class="send" type="submit">Dir</button></form>
</main>
<script>
const chat=document.querySelector('#chat'), input=document.querySelector('#input'), status=document.querySelector('#status');
function add(text,cls,meta=''){const d=document.createElement('div');d.className='msg '+cls;d.textContent=text;chat.appendChild(d);if(meta){const m=document.createElement('div');m.className='meta';m.textContent=meta;chat.appendChild(m)}chat.scrollTop=chat.scrollHeight}
document.querySelector('#form').addEventListener('submit',async e=>{e.preventDefault();const message=input.value.trim();if(!message)return;add(message,'user');input.value='';status.textContent='AI-gu wuu fikirayaa…';try{const r=await fetch('/api/chat',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({message})});const data=await r.json();if(!r.ok)throw new Error(data.error||'Request failed');add(data.text,'ai',`${data.model} · evidence ${data.evidence_count} · checker ${data.finding_count}`);status.textContent=''}catch(err){status.textContent='Khalad: '+err.message}});
document.querySelector('#clear').addEventListener('click',async()=>{await fetch('/api/clear',{method:'POST'});chat.replaceChildren();add('Wadahadal cusub ayaa bilaabmay.','ai');status.textContent=''});
input.addEventListener('keydown',e=>{if(e.key==='Enter'&&!e.shiftKey){e.preventDefault();document.querySelector('#form').requestSubmit()}});
</script></body></html>'''


class AssistantWebApp:
    def __init__(self, session: ConversationSession) -> None:
        self.session = session
        self._lock = threading.Lock()

    def chat(self, message: str) -> dict:
        with self._lock:
            result = self.session.ask(message)
        return {
            "text": result.text,
            "model": result.model,
            "evidence_count": len(result.knowledge_paths),
            "finding_count": len(result.findings),
        }

    def clear(self) -> None:
        with self._lock:
            self.session.clear()


def make_handler(app: AssistantWebApp):
    class Handler(BaseHTTPRequestHandler):
        def _json(self, status: int, payload: dict) -> None:
            body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
            self.send_response(status)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def do_GET(self) -> None:  # noqa: N802
            if self.path != "/":
                self.send_error(HTTPStatus.NOT_FOUND)
                return
            body = CHAT_HTML.encode("utf-8")
            self.send_response(HTTPStatus.OK)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def do_POST(self) -> None:  # noqa: N802
            if self.path == "/api/clear":
                app.clear()
                self._json(HTTPStatus.OK, {"ok": True})
                return
            if self.path != "/api/chat":
                self.send_error(HTTPStatus.NOT_FOUND)
                return
            try:
                length = int(self.headers.get("Content-Length", "0"))
                if length <= 0 or length > 100_000:
                    raise ValueError("invalid request size")
                payload = json.loads(self.rfile.read(length).decode("utf-8"))
                message = payload.get("message", "") if isinstance(payload, dict) else ""
                if not isinstance(message, str) or not message.strip():
                    raise ValueError("message is required")
                self._json(HTTPStatus.OK, app.chat(message.strip()))
            except (ValueError, json.JSONDecodeError) as exc:
                self._json(HTTPStatus.BAD_REQUEST, {"error": str(exc)})
            except (ModelRequestError, RuntimeError) as exc:
                self._json(HTTPStatus.BAD_GATEWAY, {"error": str(exc)})

        def log_message(self, fmt: str, *args) -> None:
            return

    return Handler


def main() -> int:
    parser = argparse.ArgumentParser(description="Run the local Somali AI web chat")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8080)
    args = parser.parse_args()

    try:
        model = OpenAIResponsesAdapter.from_env()
    except ModelConfigurationError as exc:
        print(f"Configuration error: {exc}")
        return 2

    session = ConversationSession(SomaliAssistant(model))
    app = AssistantWebApp(session)
    server = ThreadingHTTPServer((args.host, args.port), make_handler(app))
    print(f"Somali AI web chat: http://{args.host}:{args.port}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
