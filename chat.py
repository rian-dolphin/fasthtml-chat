import asyncio
import json

import logfire
from dotenv import load_dotenv
from fasthtml.common import *
from pydantic_ai import Agent
from pydantic_ai.messages import (
    ModelMessage,
    ModelRequest,
    ModelResponse,
    TextPart,
    UserPromptPart,
)
from starlette.responses import StreamingResponse

load_dotenv()
logfire.configure(environment="dev")
logfire.instrument_pydantic_ai()
# Set up the app, including daisyui and tailwind for the chat component
hdrs = (
    Script(src="https://cdn.jsdelivr.net/npm/@tailwindcss/browser@4"),
    Link(
        rel="stylesheet",
        href="https://cdn.jsdelivr.net/npm/daisyui@5",
    ),
    Script(
        src="https://unpkg.com/htmx-ext-transfer-encoding-chunked@0.4.0/transfer-encoding-chunked.js"
    ),
)

app = FastHTML(hdrs=hdrs, cls="p-4 max-w-lg mx-auto", live=True, debug=True)


# Initialize Pydantic AI agent with GPT-4o
agent = Agent("openai:gpt-4o")


def convert_messages_to_pydantic_ai(chat_history_json: str) -> list[ModelMessage]:
    """Convert JSON chat history to pydantic-ai format"""
    messages = json.loads(chat_history_json) if chat_history_json else []
    pydantic_messages = []

    for msg in messages:
        if msg["role"] == "user":
            pydantic_messages.append(
                ModelRequest(parts=[UserPromptPart(content=msg["content"])])
            )
        elif msg["role"] == "assistant":
            pydantic_messages.append(
                ModelResponse(parts=[TextPart(content=msg["content"])])
            )

    return pydantic_messages


def ChatMessage(msg, user: bool, id=None):
    bubble_class = "chat-bubble-primary" if user else "chat-bubble-secondary"
    chat_class = "chat-end" if user else "chat-start"
    return Div(cls=f"chat {chat_class}", id=f"msg-{id}")(
        Div("user" if user else "assistant", cls="chat-header"),
        Div(
            msg,
            cls=f"chat-bubble {bubble_class}",
            id=f"msg-{id}-content" if id else None,
        ),
        # Chat history now stored as JSON in a single hidden field
    )


# The input field for the user message. Also used to clear the
# input field after sending a message via an OOB swap
def ChatInput():
    return Input(
        name="msg",
        id="msg-input",
        placeholder="Type a message",
        cls="input input-bordered w-full",
        hx_swap_oob="true",
    )


# The main screen
@app.get
def index():
    page = Form(
        hx_post=send,
        hx_target="#chatlist",
        hx_swap="beforeend",
        hx_ext="chunked-transfer",
        hx_disabled_elt="#msg-group",
    )(
        Div(id="chatlist", cls="chat-box h-[73vh] overflow-y-auto"),
        Hidden(
            "", name="chat_history", id="chat-history-json"
        ),  # JSON storage for chat history
        Div(cls="flex space-x-2 mt-2")(
            Group(ChatInput(), Button("Send", cls="btn btn-primary"), id="msg-group")
        ),
    )
    return Titled("Chatbot Demo", page)


async def stream_response(msg, chat_history_json):
    from fasthtml.common import Div, Hidden, to_xml

    # Parse existing chat history
    chat_history = json.loads(chat_history_json) if chat_history_json else []

    # Add user message to history
    chat_history.append({"role": "user", "content": msg})

    # Show user message
    yield to_xml(ChatMessage(msg, True, id=len(chat_history) - 1))

    # Convert history (excluding the new user message we just added) to Pydantic AI format
    message_history = convert_messages_to_pydantic_ai(json.dumps(chat_history[:-1]))

    # Use Pydantic AI streaming with conversation history
    response_txt = ""
    first_chunk = True
    async with agent.run_stream(msg, message_history=message_history) as response:
        async for text_chunk in response.stream_text():
            response_txt = text_chunk

            if first_chunk:
                # For first chunk, show the complete assistant message
                yield to_xml(ChatMessage(response_txt, False, id=len(chat_history)))
                first_chunk = False
            else:
                # For subsequent chunks, update the content
                yield to_xml(
                    Div(
                        response_txt,
                        cls="chat-bubble chat-bubble-secondary",
                        id=f"msg-{len(chat_history)}-content",
                        hx_swap_oob="outerHTML",
                    )
                )
            await asyncio.sleep(0.1)  # Small delay between updates

    # Add assistant message to history
    chat_history.append({"role": "assistant", "content": response_txt})

    # Update the JSON hidden field with complete conversation
    yield to_xml(
        Hidden(
            json.dumps(chat_history),
            name="chat_history",
            id="chat-history-json",
            hx_swap_oob="outerHTML",
        )
    )

    # Reset input field
    yield to_xml(ChatInput())


@app.post
async def send(msg: str, chat_history: str = ""):
    return StreamingResponse(
        stream_response(msg, chat_history),
        media_type="text/plain",
        headers={"X-Transfer-Encoding": "chunked"},
    )


serve()
