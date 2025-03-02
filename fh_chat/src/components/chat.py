from fasthtml.common import *

from .message import ChatTheme, InitialChatPlaceholder


def ChatInput(
    swap_oob: bool = False,
    post_url: str = "/generate-message",
    theme: str = ChatTheme.DEFAULT,
    placeholder: str = "Type a message",
    button_text: str = "Send",
    **kwargs,
):
    """
    Create a chat input component.

    Args:
        swap_oob: Whether to use HTMX out-of-band swap
        post_url: URL to post messages to
        theme: Theme name
        placeholder: Input placeholder text
        button_text: Send button text
        **kwargs: Additional attributes for the form

    Returns:
        A FastHTML form component
    """
    attrs = {
        "hx_post": post_url,
        "hx_target": "#chatlist",
        "hx_swap": "beforeend",
        "hx_ext": "chunked-transfer",
        "id": "chat-form",
        "hx_include": "[name='messages']",
        **kwargs,
    }

    if swap_oob:
        attrs["hx_swap_oob"] = "outerHTML"

    if theme == ChatTheme.DEFAULT:
        return Form(**attrs)(
            Group(
                Input(
                    name="msg",
                    id="msg-input",
                    placeholder=placeholder,
                    cls="input input-bordered w-full",
                ),
                Button(button_text, cls="btn btn-primary"),
            )
        )
    elif theme == ChatTheme.MINIMAL:
        return Form(**attrs)(
            Div(cls="flex items-center gap-2")(
                Input(
                    name="msg",
                    id="msg-input",
                    placeholder=placeholder,
                    cls="border border-gray-300 rounded-md p-2 flex-grow",
                ),
                Button(button_text, cls="bg-blue-500 text-white px-4 py-2 rounded-md"),
            )
        )
    elif theme == ChatTheme.BUBBLE:
        return Form(**attrs)(
            Div(cls="flex items-center mt-4 gap-2")(
                Input(
                    name="msg",
                    id="msg-input",
                    placeholder=placeholder,
                    cls="flex-grow p-3 border rounded-full focus:outline-none focus:ring-2 focus:ring-blue-500",
                ),
                Button(
                    button_text,
                    cls="bg-blue-500 hover:bg-blue-600 text-white p-3 rounded-full w-12 h-12 flex items-center justify-center",
                ),
            )
        )
    else:
        raise ValueError(f"Unknown theme: {theme}")


def Chat(
    id: str = "chat",
    height: str = "70vh",
    theme: str = ChatTheme.DEFAULT,
    post_url: str = "/generate-message",
    button_text: str = "Send",
    placeholder: str = "Type a message",
    container_class: str = "",
    title: str = None,
    **kwargs,
):
    """
    Create a complete chat component.

    Args:
        id: ID for the chat container
        height: Height of the chat area
        theme: Theme name
        post_url: URL to post messages to
        button_text: Send button text
        placeholder: Input placeholder text
        container_class: Additional CSS classes for the container
        title: Optional title for the chat component
        **kwargs: Additional attributes for the container

    Returns:
        A FastHTML component for the complete chat interface
    """
    # Theme-specific classes
    if theme == ChatTheme.DEFAULT:
        chat_list_class = f"h-[{height}] overflow-y-auto p-4"
        container_cls = f"p-4 max-w-lg mx-auto {container_class}"
    elif theme == ChatTheme.MINIMAL:
        chat_list_class = f"h-[{height}] overflow-y-auto border rounded-lg p-4 mb-4"
        container_cls = f"max-w-lg mx-auto {container_class}"
    elif theme == ChatTheme.BUBBLE:
        chat_list_class = f"h-[{height}] overflow-y-auto p-4 bg-gray-50 rounded-lg"
        container_cls = f"max-w-xl mx-auto shadow-lg rounded-lg p-4 {container_class}"
    else:
        raise ValueError(f"Unknown theme: {theme}")

    title_component = Div(title, cls="text-xl font-bold mb-4") if title else None

    components = [
        title_component,
        InitialChatPlaceholder(),
        Div(id="chatlist", cls=chat_list_class),
        ChatInput(
            post_url=post_url,
            theme=theme,
            placeholder=placeholder,
            button_text=button_text,
        ),
    ]

    # Filter out None values
    components = [c for c in components if c is not None]

    return Div(*components, id=id, cls=container_cls, **kwargs)


def get_chat_headers():
    """Return the required headers for chat functionality."""
    return [
        Script(
            src="https://unpkg.com/htmx-ext-transfer-encoding-chunked@0.4.0/transfer-encoding-chunked.js"
        ),
        Script(src="https://cdn.tailwindcss.com"),
        Link(
            rel="stylesheet",
            href="https://cdn.jsdelivr.net/npm/daisyui@4.11.1/dist/full.min.css",
        ),
    ]
