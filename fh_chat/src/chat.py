import asyncio
import json
import os

from anthropic import Anthropic
from fasthtml.common import *
from starlette.responses import StreamingResponse


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
