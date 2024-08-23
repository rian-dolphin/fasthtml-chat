from fasthtml.common import *


def ChatInput():
    return Input(
        name="msg",
        id="msg-input",
        placeholder="Type a message",
        cls="input input-bordered w-full",
        hx_swap_oob="outerHTML",
    )


def ChatPage(
    include_style_headers: bool = False,
    title: str = "Chatbot Demo",
    cls: str = "p-4 max-w-3xl mx-auto",
    view_height: str = 73,
):
    page = Form(
        hx_post="/generate-message",
        hx_target="#chatlist",
        hx_swap="beforeend",
        hx_ext="chunked-transfer",
        hx_disabled_elt="#msg-group",
    )(
        Div(id="chatlist", cls=f"chat-box h-[{view_height}vh] overflow-y-auto"),
        Div(cls="flex space-x-2 mt-2")(
            Group(ChatInput(), Button("Send", cls="btn btn-primary"), id="msg-group")
        ),
    )
    style_headers = [
        picolink,
        Script(src="https://cdn.tailwindcss.com"),
        Link(
            rel="stylesheet",
            href="https://cdn.jsdelivr.net/npm/daisyui@4.11.1/dist/full.min.css",
        ),
    ]
    return tuple(
        [
            Title(title),
            page,
            Script(
                src="https://unpkg.com/htmx-ext-transfer-encoding-chunked@0.4.0/transfer-encoding-chunked.js"
            ),
        ]
        + (style_headers if include_style_headers else [])
    )
