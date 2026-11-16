
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from starlette.concurrency import run_in_threadpool

from web.chat_service import process_message, restore_history

app = FastAPI()


@app.websocket("/ws/chat/{conversation_id}")
async def chat(websocket: WebSocket, conversation_id: str):
    await websocket.accept()

    print(f"[WEB] Connected: {conversation_id}")

    try:
        while True:
            data = await websocket.receive_json()

            message_type = data.get("type")

            # Restore the browser's conversation into Python
            if message_type == "restore":
                messages = data.get("messages", [])

                await run_in_threadpool(
                    restore_history,
                    conversation_id,
                    messages
                )

                await websocket.send_json({
                    "type": "ready"
                })

                print(
                    f"[WEB] Restored {len(messages)} messages "
                    f"for {conversation_id}"
                )

            # Process a normal user message
            elif message_type == "message":
                message = data.get("content", "").strip()

                if not message:
                    continue

                print(f"[WEB] User: {message}")

                try:
                    response = await run_in_threadpool(
                        process_message,
                        conversation_id,
                        message
                    )

                    await websocket.send_json({
                        "type": "message",
                        "content": response
                    })

                except Exception as e:
                    print(f"[WEB ERROR] {e}")

                    await websocket.send_json({
                        "type": "error",
                        "content": "An error occurred while processing your message."
                    })

            else:
                await websocket.send_json({
                    "type": "error",
                    "content": "Unknown message type."
                })

    except WebSocketDisconnect:
        print(f"[WEB] Disconnected: {conversation_id}")

    except Exception as e:
        print(f"[WEB CONNECTION ERROR] {e}")


app.mount(
    "/",
    StaticFiles(directory="web/static", html=True),
    name="static"
)
