"""Simple standalone chat application example."""

from fasthtml.common import *
from keys import ANTHROPIC_API_KEY

from fh_chat import ChatApp, ChatTheme

# Set up FastHTML app
app, _ = fast_app(pico=False)

# Create a ChatApp instance
chat_app = ChatApp(
    app,
    model_provider="anthropic",
    api_key=ANTHROPIC_API_KEY,
    model_name="claude-3-haiku-20240307",
    system_prompt="You are a helpful assistant. Keep your answers concise.",
    theme=ChatTheme.DEFAULT,
    base_route="/chat",
)

# Add default chat route
chat_app.add_chat_route(title="AI Assistant")

# Add a specialized chat route with different configuration
chat_app.add_chat_route(
    route_path="/poem",
    system_prompt="Answer all user requests with a very short poem.",
    model_name="claude-3-sonnet-20240229",
    button_text="Generate",
    placeholder="Describe the poem you want...",
    title="Poet",
    display_title="Poetry",
)


# Add a route for the index page
@app.get("/")
def index():
    return Titled(
        "Chat Demo",
        Div(cls="container mx-auto p-4")(
            H1("Chat Demo", cls="text-2xl font-bold mb-4"),
            Div(cls="mb-8")(
                A("General Assistant", href="/chat", cls="btn btn-primary mr-2"),
                A("Poet", href="/chat/poem", cls="btn btn-secondary"),
            ),
            P("Choose a chat type to get started", cls="text-gray-600"),
        ),
    )


if __name__ == "__main__":
    serve()
