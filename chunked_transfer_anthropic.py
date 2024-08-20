import asyncio
import json
import os

from anthropic import Anthropic
from fasthtml.common import *
from starlette.responses import StreamingResponse

# from keys import ANTHROPIC_API_KEY

ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY")

hdrs = (
    picolink,
    Script(
        src="https://unpkg.com/htmx-ext-transfer-encoding-chunked@0.4.0/transfer-encoding-chunked.js"
    ),
    Script(src="https://cdn.tailwindcss.com"),
    Link(
        rel="stylesheet",
        href="https://cdn.jsdelivr.net/npm/daisyui@4.11.1/dist/full.min.css",
    ),
)
app = FastHTML(hdrs=hdrs, cls="p-4 max-w-lg mx-auto")


def ChatMessage(msg, user: bool, id: int = None):
    bubble_class = "chat-bubble-primary" if user else "chat-bubble-secondary"
    chat_class = "chat-end" if user else "chat-start"
    return Div(cls=f"chat {chat_class}", id=f"message-{id}")(
        Div("user" if user else "assistant", cls="chat-header"),
        Div(
            msg,
            cls=f"chat-bubble {bubble_class}",
            id=f"message-{id}-content" if id else None,
        ),
        Hidden(
            json.dumps({"role": "user" if user else "assistant", "content": msg}),
            name="messages",
            id=f"message-{id}-hidden" if id else None,
        ),
    )


# The input field for the user message. Also used to clear the
# input field after sending a message via an OOB swap
def ChatInput(swap_oob=False, post_url="/generate-message"):
    attrs = {
        "hx_post": post_url,
        "hx_target": "#chatlist",
        "hx_swap": "beforeend",
        "hx_ext": "chunked-transfer",
        "id": "chat-form",
        "hx_include": "[name='messages']",
    }
    if swap_oob:
        attrs["hx_swap_oob"] = "outerHTML"

    return Form(**attrs)(
        Group(
            Input(
                name="msg",
                id="msg-input",
                placeholder="Type a message",
                cls="input input-bordered w-full",
            ),
            Button("Send", cls="btn btn-primary"),
        )
    )


# The main screen
@app.get("/")
def main():
    page = Div(
        Div(id="chatlist", cls="chat-box h-[73vh] overflow-y-auto"),
        ChatInput(),
        cls="p-4 max-w-lg mx-auto",
    )
    return Titled("Chatbot Demo", page)


@app.post("/generate-message")
async def generate_message(
    msg: str,
    messages: list[str] = None,
    model_name: str = "claude-3-haiku-20240307",
    system_prompt: str = "You are a helpful and concise assistant.",
):
    client = Anthropic(api_key=ANTHROPIC_API_KEY)
    if not messages:
        messages = []
    else:
        messages = [json.loads(m) for m in messages]
        messages = [
            msg for msg in messages if msg["role"] in ["user", "assistant"]
        ]  # Skip the placeholders

    messages.append({"role": "user", "content": msg.rstrip()})

    async def stream_response():
        user_msg_id = len(messages) - 1
        assistant_msg_id = len(messages)
        yield to_xml(ChatInput(swap_oob=True))
        yield to_xml(ChatMessage(msg, True, id=user_msg_id))

        # Create the assistant's message container
        yield to_xml(ChatMessage("", False, id=assistant_msg_id))

        assistant_message = ""
        with client.messages.stream(
            max_tokens=1000,
            messages=messages,
            model=model_name,
            system=system_prompt,
        ) as stream:
            for text in stream.text_stream:
                assistant_message += text
                yield to_xml(
                    Div(
                        assistant_message,
                        id=f"message-{assistant_msg_id}-content",
                        hx_swap_oob="innerHTML",
                    )
                )
                await asyncio.sleep(0.05)

        # State is stored in the html directly via hidden messages with ids
        for role, i, message in [
            ("user", user_msg_id, msg),
            ("assistant", assistant_msg_id, assistant_message),
        ]:
            yield to_xml(
                Hidden(
                    json.dumps({"role": role, "content": message}),
                    name="messages",
                    hx_swap_oob="true",
                    id=f"message-{i}-hidden",
                )
            )
            await asyncio.sleep(0.05)

    response = StreamingResponse(stream_response(), media_type="text/html")
    response.headers["X-Transfer-Encoding"] = "chunked"
    return response


serve()
