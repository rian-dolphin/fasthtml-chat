"""Chat message UI components for FastHTMLChat."""

import json
from typing import Optional

from fasthtml.common import Div, Hidden


class ChatTheme:
    """UI themes for chat components."""

    DEFAULT = "default"  # DaisyUI-based
    MINIMAL = "minimal"  # Clean, minimalist design
    BUBBLE = "bubble"  # Bubble chat style


def ChatMessage(
    msg: str, user: bool, id: Optional[int] = None, theme: str = ChatTheme.DEFAULT
):
    """
    Create a chat message component.

    Args:
        msg: Message content
        user: True if message is from user, False if from assistant
        id: Optional message ID for targeting with HTMX
        theme: Theme name to apply

    Returns:
        A FastHTML component for the message
    """
    if theme == ChatTheme.DEFAULT:
        bubble_class = "chat-bubble-primary" if user else "chat-bubble-secondary"
        chat_class = "chat-end" if user else "chat-start"
        return Div(cls=f"chat {chat_class}", id=f"message-{id}")(
            Div("You" if user else "Assistant", cls="chat-header"),
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
    elif theme == ChatTheme.MINIMAL:
        container_class = "flex justify-end" if user else "flex justify-start"
        msg_class = (
            "bg-blue-500 text-white rounded-lg p-3 mb-2 max-w-3/4"
            if user
            else "bg-gray-200 text-gray-800 rounded-lg p-3 mb-2 max-w-3/4"
        )

        return Div(cls=container_class, id=f"message-{id}")(
            Div(
                msg,
                cls=msg_class,
                id=f"message-{id}-content" if id else None,
            ),
            Hidden(
                json.dumps({"role": "user" if user else "assistant", "content": msg}),
                name="messages",
                id=f"message-{id}-hidden" if id else None,
            ),
        )
    elif theme == ChatTheme.BUBBLE:
        align_class = "ml-auto" if user else "mr-auto"
        bg_class = "bg-blue-500 text-white" if user else "bg-gray-100 text-gray-800"

        return Div(cls=f"max-w-3/4 {align_class} my-2", id=f"message-{id}")(
            Div(
                "You" if user else "Assistant",
                cls=f"text-xs mb-1 {align_class}",
            ),
            Div(
                msg,
                cls=f"{bg_class} p-3 rounded-lg",
                id=f"message-{id}-content" if id else None,
            ),
            Hidden(
                json.dumps({"role": "user" if user else "assistant", "content": msg}),
                name="messages",
                id=f"message-{id}-hidden" if id else None,
            ),
        )
    else:
        raise ValueError(f"Unknown theme: {theme}")


def InitialChatPlaceholder():
    """Create a placeholder for the initial chat state with hidden message field."""
    return Div(id="message-placeholder")(
        Hidden(
            json.dumps(
                {
                    "role": "placeholder",
                    "content": "Initiate the messages for hx-include",
                }
            ),
            name="messages",
            id="message-placeholder-hidden",
        ),
    )
