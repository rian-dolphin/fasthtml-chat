import asyncio
import json
from typing import List, Optional

from fasthtml.common import *
from starlette.responses import StreamingResponse

from .clients import AnthropicClient, ClaudetteClient, OpenAIClient


class Chat:
    def __init__(self, client, **kwargs):
        self.ai_client = self._create_client(client, **kwargs)

    def _create_client(self, client, **kwargs):
        if "anthropic" in str(type(client)).lower():
            return AnthropicClient(client, **kwargs)
        elif "openai" in str(type(client)).lower():
            return OpenAIClient(client, **kwargs)
        elif "claudette" in str(type(client)).lower():
            return ClaudetteClient(client, **kwargs)
        else:
            raise ValueError(
                "Unsupported client type. Please use an Anthropic, OpenAI, or Claudette client."
            )

    @staticmethod
    def chat_message(msg: str, user: bool, id: Optional[int] = None):
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

    @staticmethod
    def chat_input(swap_oob: bool = False, post_url: str = "/generate-message"):
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

    @staticmethod
    def chat_page(include_style_headers: bool = False):
        page = Div(cls="p-4 max-w-3xl mx-auto")(
            Div(id="chatlist", cls="chat-box h-[73vh] overflow-y-auto"),
            Chat.chat_input(),
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
            Title(f"Chatbot Demo"),
            page,
            Script(
                src="https://unpkg.com/htmx-ext-transfer-encoding-chunked@0.4.0/transfer-encoding-chunked.js"
            ),
        ] + (style_headers if include_style_headers else [])

    async def generate_message(self, msg: str, messages: List[str] = None):
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
            yield to_xml(self.chat_input(swap_oob=True))
            yield to_xml(self.chat_message(msg, True, id=user_msg_id))

            # Create the assistant's message container
            yield to_xml(self.chat_message("", False, id=assistant_msg_id))

            assistant_message = ""
            async for text in self.ai_client.generate_stream(messages):
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
                        hx_swap_oob="outerHTML",
                        id=f"message-{i}-hidden",
                    )
                )
                await asyncio.sleep(0.05)

        response = StreamingResponse(stream_response(), media_type="text/html")
        response.headers["X-Transfer-Encoding"] = "chunked"
        return response
