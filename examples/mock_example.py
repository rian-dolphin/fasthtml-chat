"""Example of using the mock provider for testing without API tokens."""

from fasthtml.common import *

from fh_chat import ChatApp, ChatTheme

# Set up FastHTML app
app, _ = fast_app(pico=False)

# Create a ChatApp instance with mock provider
chat_app = ChatApp(
    app,
    model_provider="mock",  # Use the mock provider
    theme=ChatTheme.DEFAULT,
    base_route="/chat",
)

# Add default chat route
chat_app.add_chat_route(title="Mock Chat")


@app.get("/")
def index():
    return Titled(
        "Mock Chat Demo",
        Div(cls="container mx-auto p-4")(
            H1("Mock Chat Demo", cls="text-2xl font-bold mb-4"),
            P(
                "This demo uses a mock provider that doesn't require API tokens.",
                cls="mb-4",
            ),
            Div(cls="mb-8")(
                A("Start Mock Chat", href="/chat", cls="btn btn-primary"),
            ),
        ),
    )


if __name__ == "__main__":
    serve()
