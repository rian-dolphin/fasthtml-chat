from anthropic import Anthropic
from claudette import *
from fasthtml.common import *

from keys import ANTHROPIC_API_KEY

# Set up the app, including daisyui and tailwind for the chat component
hdrs = (
    picolink,
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


def ChatMessage(msg, user: bool):
    bubble_class = "chat-bubble-primary" if user else "chat-bubble-secondary"
    chat_class = "chat-end" if user else "chat-start"
    return Div(cls=f"chat {chat_class}")(
        Div("user" if user else "assistant", cls="chat-header"),
        Div(msg, cls=f"chat-bubble {bubble_class}"),
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
    page = Form(hx_post=send, hx_target="#chatlist", hx_swap="beforeend")(
        Div(id="chatlist", cls="chat-box h-[73vh] overflow-y-auto"),
        Div(cls="flex space-x-2 mt-2")(
            Group(ChatInput(), Button("Send", cls="btn btn-primary"))
        ),
    )
    return Titled("Chatbot Demo", page)


# Handle the form submission
@app.post
def send(msg: str, messages: list[str] = None):
    if not messages:
        messages = []
    else:
        messages = [eval(str(m)) for m in messages]
    messages.append({"role": "user", "content": msg.rstrip()})
    print(messages)
    response = client.messages.create(
        model="claude-3-haiku-20240307",
        max_tokens=1000,
        temperature=0,
        system="You are a very concise assistant.",
        messages=messages,
    )
    assistant_msg = response.content[0].text
    messages.append({"role": "assistant", "content": assistant_msg})
    return (
        ChatMessage(msg, True),
        ChatMessage(assistant_msg, False),
        ChatInput(),  # And clear the input field via an OOB swap
    )


serve()
