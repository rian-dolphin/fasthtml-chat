import asyncio

from anthropic import Anthropic
from claudette import *
from fasthtml.common import *
from starlette.responses import StreamingResponse

from keys import ANTHROPIC_API_KEY

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

# Set up a chat model (https://claudette.answer.ai/)
client = Anthropic(api_key=ANTHROPIC_API_KEY)
sp = "You are a helpful and concise assistant."


def ChatMessage(msg, user: bool, id=None):
    bubble_class = "chat-bubble-primary" if user else "chat-bubble-secondary"
    chat_class = "chat-end" if user else "chat-start"
    return Div(cls=f"chat {chat_class}", id=id)(
        Div("user" if user else "assistant", cls="chat-header"),
        Div(msg, cls=f"chat-bubble {bubble_class}", id=f"{id}-content" if id else None),
        Hidden(
            f"{{'role': '{'user' if user else 'assistant'}', 'content': '{msg}'}}",
            name="messages",
        ),
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
        hx_ext="chunked-transfer",  # Add this line to enable chunked transfer
    )(
        Div(id="chatlist", cls="chat-box h-[73vh] overflow-y-auto"),
        Div(cls="flex space-x-2 mt-2")(
            Group(ChatInput(), Button("Send", cls="btn btn-primary"))
        ),
    )
    return Titled("Chatbot Demo", page)


@app.post
async def send(msg: str, messages: list[str] = None):
    if not messages:
        messages = []
    else:
        messages = [eval(str(m)) for m in messages]
    messages.append({"role": "user", "content": msg.rstrip()})

    async def stream_response():
        yield to_xml(ChatMessage(msg, True))
        yield to_xml(ChatInput())  # Clear the input field via an OOB swap

        # Create the assistant's message container
        assistant_id = f"assistant-{len(messages)}"
        yield to_xml(ChatMessage("", False, id=assistant_id))

        assistant_message = ""
        with client.messages.stream(
            max_tokens=1000,
            messages=messages,
            model="claude-3-haiku-20240307",
            system="You are a very concise assistant.",
        ) as stream:
            for text in stream.text_stream:
                assistant_message += text
                # Update the entire content each time
                yield to_xml(
                    Div(
                        assistant_message,
                        id=f"{assistant_id}-content",
                        hx_swap_oob="innerHTML",
                    )
                )
                await asyncio.sleep(0.15)  # Small delay to control the stream rate

        messages.append({"role": "assistant", "content": assistant_message})
        # Update the hidden input with the full message
        yield to_xml(
            Hidden(
                f"{{'role': 'assistant', 'content': '{assistant_message}'}}",
                name="messages",
                hx_swap_oob="beforeend",
            )
        )

    return StreamingResponse(stream_response(), media_type="text/html")


serve()
