import json
import os

from anthropic import Anthropic
from fasthtml.common import *
from starlette.responses import StreamingResponse

from fh_chat import ChatInput, stream_response_anthropic

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
        stream_response_anthropic(
            all_messages,
            client,
            model_name,
            system_prompt,
            temperature=0.5,
            user_bubble_class="chat-bubble chat-bubble-primary",
            assistant_bubble_class="chat-bubble chat-bubble-secondary",
            bubble_header=False,
        ),
        media_type="text/html",
    )
    response.headers["X-Transfer-Encoding"] = "chunked"
    return response


serve()
