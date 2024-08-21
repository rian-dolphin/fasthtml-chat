import json

from fasthtml.common import *


def ChatMessage(msg: str, user: bool, id: Optional[int] = None):
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


def ChatInput(swap_oob: bool = False, post_url: str = "/generate-message"):
    attrs = {
        "hx_post": post_url,
        "hx_target": "#chatlist",
        "hx_swap": "beforeend",
        "hx_ext": "chunked-transfer",
        "id": "chat-form",
        "hx_include": "[name='messages']",
        "hx_disabled_elt": "#msg-group",
    }
    if swap_oob:
        attrs["hx_swap_oob"] = "outerHTML"

    return Form(**attrs)(
        Group(id="msg-group")(
            Input(
                name="msg",
                id="msg-input",
                placeholder="Type a message",
                cls="input input-bordered w-full",
            ),
            Button("Send", cls="btn btn-primary"),
        )
    )


def ChatPage(
    include_style_headers: bool = False,
    title: str = "Chatbot Demo",
    cls: str = "p-4 max-w-3xl mx-auto",
    view_height: str = 73,
):
    page = Div(cls=cls)(
        Div(id="chatlist", cls=f"chat-box h-[{view_height}vh] overflow-y-auto"),
        ChatInput(),
    )
    style_headers = [
        picolink,
        Script(src="https://cdn.tailwindcss.com"),
        Link(
            rel="stylesheet",
            href="https://cdn.jsdelivr.net/npm/daisyui@4.11.1/dist/full.min.css",
        ),
    ]
    return [
        Title(title),
        page,
        Script(
            src="https://unpkg.com/htmx-ext-transfer-encoding-chunked@0.4.0/transfer-encoding-chunked.js"
        ),
    ] + (style_headers if include_style_headers else [])
