from fasthtml.common import *

from fh_chat import Chat, ChatPage

hdrs = (
    picolink,
    Script(src="https://cdn.tailwindcss.com"),
    Link(
        rel="stylesheet",
        href="https://cdn.jsdelivr.net/npm/daisyui@4.11.1/dist/full.min.css",
    ),
)
app = FastHTML(hdrs=hdrs, cls="p-4 max-w-lg mx-auto")

app.get("/")(ChatPage)

# Choose one of these client setups:

# Anthropic setup
from anthropic import Anthropic

ANTHROPIC_API_KEY = os.environ["ANTHROPIC_API_KEY"]
anthropic_client = Anthropic(api_key=ANTHROPIC_API_KEY)
chat = Chat(
    anthropic_client,
    model="claude-3-haiku-20240307",
    system="Respond with a haiku",
    max_tokens=1000,
    temperature=0.5,
)

# OpenAI setup
# from openai import OpenAI
# OPENAI_API_KEY = "..."
# openai_client = OpenAI(api_key=OPENAI_API_KEY)
# chat = Chat(openai_client, model="gpt-3.5-turbo", system="Respond with a haiku")

# Claudette setup
# from claudette import Client
# os.environ["ANTHROPIC_API_KEY"] = "..."
# claudette_client = Client(model="claude-3-haiku-20240307")
# chat = Chat(claudette_client, sp="Respond with a haiku")

app.post("/generate-message")(chat.generate_message)

serve()
