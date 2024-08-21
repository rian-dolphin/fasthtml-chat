from claudette import Client
from fasthtml.common import *

from fh_chat import Chat, ChatPage

# os.environ["ANTHROPIC_API_KEY"] must be set
claudette_client = Client(model="claude-3-haiku-20240307")
chat = Chat(claudette_client, sp="You are a very very concise assistant.")

app = FastHTML()


@app.get("/")
def page():
    return ChatPage(include_style_headers=True)


app.post("/generate-message")(chat.generate_message)

serve()
