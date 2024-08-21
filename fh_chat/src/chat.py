import asyncio
import json
from typing import List, Optional

from fasthtml.common import *
from starlette.responses import StreamingResponse

from .clients import AnthropicClient, ClaudetteClient, OpenAIClient
from .ui import ChatInput, ChatMessage


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
            yield to_xml(ChatInput(swap_oob=True))
            yield to_xml(ChatMessage(msg, True, id=user_msg_id))

            # Create the assistant's message container
            yield to_xml(ChatMessage("", False, id=assistant_msg_id))

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
