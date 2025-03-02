"""Streaming response utilities for FastHTMLChat."""

import asyncio
import json
from typing import AsyncGenerator, Callable, Dict, List, Optional

from fasthtml.common import Div, Hidden, to_xml

from ..components.chat import ChatInput
from ..components.message import ChatMessage, ChatTheme


async def stream_chat_response(
    model_stream: AsyncGenerator[str, None],
    msg: str,
    messages: List[Dict[str, str]] = None,
    theme: str = ChatTheme.DEFAULT,
    post_url: str = "/generate-message",
    delay: float = 0.05,
    message_preprocessor: Optional[Callable[[str], str]] = None,
):
    """
    Stream a chat response using chunked transfer encoding.

    Args:
        model_stream: Async generator yielding response chunks
        msg: User message that triggered the response
        messages: Previous messages list (will be initialized if None)
        theme: Theme to use for message components
        post_url: URL to post new messages to
        delay: Delay between chunks (in seconds)
        message_preprocessor: Optional function to preprocess message before display

    Yields:
        HTML chunks for streaming
    """
    if not messages:
        messages = []

    # Calculate IDs for the messages
    user_msg_id = len(messages)
    assistant_msg_id = len(messages) + 1

    # First yield back a fresh input form
    yield to_xml(ChatInput(swap_oob=True, post_url=post_url, theme=theme))

    # Yield the user message
    yield to_xml(ChatMessage(msg, True, id=user_msg_id, theme=theme))

    # Create the assistant's empty message container
    yield to_xml(ChatMessage("", False, id=assistant_msg_id, theme=theme))

    # Start streaming the assistant's response
    assistant_message = ""

    async for chunk in model_stream:
        assistant_message += chunk

        # Apply preprocessor if provided
        display_message = assistant_message
        if message_preprocessor:
            display_message = message_preprocessor(assistant_message)

        yield to_xml(
            Div(
                display_message,
                id=f"message-{assistant_msg_id}-content",
                hx_swap_oob="innerHTML",
            )
        )

        await asyncio.sleep(delay)

    # Update hidden message state
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
        await asyncio.sleep(delay)
