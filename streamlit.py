import asyncio
import json
import os

from anthropic import Anthropic
from fasthtml.common import *
from starlette.responses import StreamingResponse

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


class ChatMessage:
    def __init__(self, role, message_id, content=""):
        self.role = role
        self.message_id = message_id
        self.content = content

    @classmethod
    def create(cls, role, message_id, content=""):
        instance = cls(role, message_id, content)
        return instance.render()

    def initial_render(self):
        user = self.role == "user"
        bubble_class = "chat-bubble-primary" if user else "chat-bubble-secondary"
        chat_class = "chat-end" if user else "chat-start"
        return Div(cls=f"chat {chat_class}", id=f"message-{self.message_id}")(
            Div(self.role, cls="chat-header"),
            Div(
                self.content,
                cls=f"chat-bubble {bubble_class}",
                id=f"message-{self.message_id}-content",
            ),
            self.hidden(initial=True),
        )

    def update_content(self, new_content):
        self.content += new_content
        return (
            Div(
                self.content,
                id=f"message-{self.message_id}-content",
                hx_swap_oob="innerHTML",
            ),
            self.hidden(initial=False),
        )

    def hidden(self, initial=False):
        hidden_attrs = {
            "name": "messages",
            "id": f"message-{self.message_id}-hidden",
        }
        # Inital render should not have a swap since nothing to swaw with yet
        if not initial:
            hidden_attrs["hx_swap_oob"] = "outerHTML"

        return Hidden(
            json.dumps({"role": self.role, "content": self.content}), **hidden_attrs
        )


def ChatInput():
    return Input(
        name="msg",
        id="msg-input",
        placeholder="Type a message",
        cls="input input-bordered w-full",
        hx_swap_oob="outerHTML",
    )


@app.get("/")
def index():
    page = Form(
        hx_post="/generate-message",
        hx_target="#chatlist",
        hx_swap="beforeend",
        hx_ext="chunked-transfer",
        hx_disabled_elt="#msg-group",
    )(
        Div(id="chatlist", cls="chat-box h-[73vh] overflow-y-auto"),
        Div(cls="flex space-x-2 mt-2")(
            Group(ChatInput(), Button("Send", cls="btn btn-primary"), id="msg-group")
        ),
    )
    return Titled("Chatbot Demo", page)


@app.post("/generate-message")
def generate_message(
    msg: str,
    messages: list[str] = None,
):
    client = Anthropic(api_key=ANTHROPIC_API_KEY)
    model_name: str = "claude-3-haiku-20240307"
    system_prompt: str = "You are a helpful and concise assistant."

    if not messages:
        messages = []
    else:
        messages = [json.loads(m) for m in messages]

    all_messages = messages + [{"role": "user", "content": msg.rstrip()}]

    response = StreamingResponse(
        stream_response(all_messages, client, model_name, system_prompt),
        media_type="text/html",
    )
    response.headers["X-Transfer-Encoding"] = "chunked"
    return response


async def stream_response(all_messages, client, model_name, system_prompt):
    user_msg_id = len(all_messages) - 1
    assistant_msg_id = len(all_messages)

    user_message = ChatMessage("user", user_msg_id, all_messages[-1]["content"])
    yield to_xml(user_message.initial_render())

    assistant_message = ChatMessage("assistant", assistant_msg_id)
    yield to_xml(assistant_message.initial_render())

    with client.messages.stream(
        max_tokens=1000,
        messages=all_messages,
        model=model_name,
        system=system_prompt,
    ) as stream:
        for text in stream.text_stream:
            content_update, hidden_update = assistant_message.update_content(text)
            yield to_xml(content_update)
            yield to_xml(hidden_update)
            await asyncio.sleep(0.05)

    yield to_xml(ChatInput())


serve()
