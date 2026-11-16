
from brain_tools import ai
from chat import MAX_HISTORY


def restore_history(conversation_id: str, messages: list):

    history = [
        {
            "role": "system",
            "content": ai.system_prompt
        }
    ]

    for message in messages:

        role = message.get("role")
        content = message.get("content")

        if role not in ("user", "assistant"):
            continue

        if not isinstance(content, str):
            continue

        history.append({
            "role": role,
            "content": content
        })

    # Preserve the system prompt and recent messages
    ai.histories[conversation_id] = (
        [history[0]] + history[-MAX_HISTORY:]
    )


def process_message(conversation_id: str, message: str):

    print(f"[WEB] Conversation: {conversation_id}")
    print(f"[WEB] Prompt: {message}")

    result = ai.ask(
        prompt=message,
        conversation_id=conversation_id,
        use_tts=False
    )

    response = result.get("response", "")

    print(f"[WEB] Response: {response}")

    return response
