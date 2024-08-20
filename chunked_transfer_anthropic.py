import asyncio
import json
import os

from anthropic import Anthropic
from fasthtml.common import *
from starlette.responses import StreamingResponse

ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY")

# Set up the app, including daisyui and tailwind for the chat component
hdrs = (
    picolink,
    Script(
        src="https://unpkg.com/htmx-ext-transfer-encoding-chunked@0.2.0/transfer-encoding-chunked.js"
    ),
    Script(src="https://cdn.tailwindcss.com"),
    Link(
        rel="stylesheet",
        href="https://cdn.jsdelivr.net/npm/daisyui@4.11.1/dist/full.min.css",
    ),
)
app = FastHTML(hdrs=hdrs, cls="p-4 max-w-lg mx-auto")

# Set up a chat model
client = Anthropic(api_key=ANTHROPIC_API_KEY)
sp = "You are a helpful and concise assistant."


def ChatMessage(msg, user: bool, id: int = None):
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


def InitialChatMessage():
    # Create initial html divs with the name 'messages' for hx-include
    return Div(id=f"message-placeholder")(
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


# The input field for the user message. Also used to clear the
# input field after sending a message via an OOB swap
def ChatInput(swap_oob=False):
    attrs = {
        "hx_post": send,
        "hx_target": "#chatlist",
        "hx_swap": "beforeend",
        "hx_ext": "chunked-transfer",
        "id": "chat-form",
        "hx_include": "[name='messages']",
    }
    if swap_oob:
        attrs["hx_swap_oob"] = "outerHTML"

    return Form(**attrs)(
        Group(
            Input(
                name="msg",
                id="msg-input",
                placeholder="Type a message",
                cls="input input-bordered w-full",
            ),
            Button("Send", cls="btn btn-primary"),
        )
    )


# The main screen
@app.get
def index():
    page = Div(
        Div(id="chatlist", cls="chat-box h-[73vh] overflow-y-auto")(
            InitialChatMessage(),
            InitialChatMessage(),  # Need two placeholders so 'messages' given as a list to "/send"
        ),
        ChatInput(),
        cls="p-4 max-w-lg mx-auto",
    )
    return Titled("Chatbot Demo", page)


@app.post
async def send(msg: str, messages: list[str] = None):
    if not messages:
        messages = []
    else:
        messages = messages[2:]  # Skip the placeholders
        messages = [json.loads(m) for m in messages]
    messages.append({"role": "user", "content": msg.rstrip()})

    async def stream_response():
        yield to_xml(ChatInput(swap_oob=True))
        yield to_xml(ChatMessage(msg, True, id=len(messages) - 1))

        # Create the assistant's message container
        assistant_id = len(messages)
        yield to_xml(ChatMessage("", False, id=assistant_id))

        assistant_message = ""
        with client.messages.stream(
            max_tokens=1000,
            messages=messages,
            model="claude-3-haiku-20240307",
            system=sp,
        ) as stream:
            for text in stream.text_stream:
                assistant_message += text
                yield to_xml(
                    Div(
                        assistant_message,
                        id=f"message-{assistant_id}-content",
                        hx_swap_oob="innerHTML",
                    )
                )
                await asyncio.sleep(0.05)

        messages.append({"role": "assistant", "content": assistant_message})

        # Update all hidden messages
        # State is stored in the html directly via hidden messages with ids
        for i, message in enumerate(messages):
            yield to_xml(
                Hidden(
                    json.dumps(message),
                    name="messages",
                    hx_swap_oob="true",
                    id=f"message-{i}-hidden",
                )
            )

    return StreamingResponse(stream_response(), media_type="text/html")


serve()
