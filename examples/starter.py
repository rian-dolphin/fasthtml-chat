from anthropic import Anthropic
from claudette import Client
from fasthtml.common import *
from openai import OpenAI

from fh_chat import Chat
from keys import ANTHROPIC_API_KEY, OPENAI_API_KEY

hdrs = (
    picolink,
    Script(src="https://cdn.tailwindcss.com"),
    Link(
        rel="stylesheet",
        href="https://cdn.jsdelivr.net/npm/daisyui@4.11.1/dist/full.min.css",
    ),
)
app = FastHTML(hdrs=hdrs, cls="p-4 max-w-lg mx-auto")

app.get("/")(Chat.chat_page)

# Choose one of these client setups:

# Anthropic setup
anthropic_client = Anthropic(api_key=ANTHROPIC_API_KEY)
chat = Chat(anthropic_client, model_name="claude-3-haiku-20240307", max_tokens=1000)

# OpenAI setup
# openai_client = OpenAI(api_key=OPENAI_API_KEY)
# chat = Chat(openai_client, model_name="gpt-3.5-turbo")

# Claudette setup
# os.environ["ANTHROPIC_API_KEY"] = ANTHROPIC_API_KEY
# claudette_client = Client(model="claude-3-haiku-20240307")
# chat = Chat(claudette_client)

app.post("/generate-message")(chat.generate_message)

serve()
