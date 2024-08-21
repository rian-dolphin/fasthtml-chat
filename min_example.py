from claudette import Client
from fasthtml.common import *

from fh_chat import Chat

# os.environ["ANTHROPIC_API_KEY"] = "..."
claudette_client = Client(model="claude-3-haiku-20240307")
chat = Chat(claudette_client, sp="Respond with a haiku")

app = FastHTML()


@app.get("/")
def page():
    return Chat.chat_page(include_style_headers=True)


app.post("/generate-message")(chat.generate_message)

serve()
