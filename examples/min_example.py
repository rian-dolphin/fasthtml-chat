from anthropic import Anthropic
from fasthtml.common import *

from fh_chat import Chat, ChatPage

# os.environ["ANTHROPIC_API_KEY"] must be set
anthropic_client = Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
# You can pass any of the body parameters supported by the API (https://docs.anthropic.com/en/api/messages)
chat = Chat(
    anthropic_client,
    model="claude-3-haiku-20240307",
    system="You are a concise assistant.",
    max_tokens=50,
    temperature=0.5,
)

app = FastHTML()


@app.get("/")
def page():
    return ChatPage(include_style_headers=True)


app.post("/generate-message")(chat.generate_message)

serve()
