# fh-chat

fh-chat is a flexible library built for [FastHTML](https://fastht.ml/) applications, enabling easy integration of AI-powered chat functionality with support for multiple AI backends.

## Features

- Support for multiple AI backends: Anthropic, OpenAI, and Claudette
- Real-time streaming responses for a responsive chat experience
- Chat UI using DaisyUI and Tailwind CSS
- Message state stored client side in the HTML
- Easy-to-use API for quick implementation

## Installation

```bash
pip install fh-chat
```

## Quick Start

```python
from claudette import Client
from fasthtml.common import *
from fh_chat import Chat

# Set up your AI client (Claudette example)
# os.environ["ANTHROPIC_API_KEY"] = "..."
claudette_client = Client(model="claude-3-haiku-20240307")
chat = Chat(claudette_client, sp="Respond with a haiku")

# Create a FastHTML app
app = FastHTML()

# Add chat page route
@app.get("/")
def page():
    return Chat.chat_page(include_style_headers=True)

# Add message generation route
app.post("/generate-message")(chat.generate_message)

# Run the app
serve()
```

## Usage

1. Initialize a `Chat` object with the client from your chosen provider (Anthropic, OpenAI, Claudette):
   ```python
   chat = Chat(ai_client, **client_options)
   ```

2. Set up the chat page in your FastHTML app:
   ```python
   @app.get("/")
   def page():
       return Chat.chat_page(include_style_headers=True)
   ```
   If you are already using pico and daisyui in your app then you don't need to include the style headers.

3. Add a the generate-message route:
   ```python
   app.post("/generate-message")(chat.generate_message)
   ```

4. Customize the chat appearance with tailwind (optional):
   ```python
   custom_chat_page = Chat.chat_page(include_style_headers=False, cls="p-4 mx-auto bg-gray-400", view_height=75)
   ```

## Supported AI Clients

- Anthropic: Use the `anthropic` library
- OpenAI: Use the `openai` library
- Claudette: Use the `claudette` library

## How It Works

fh-chat uses FastHTML's HTMX integration to handle real-time updates. The chat interface is rendered server-side, and messages are streamed to the client using chunked transfer encoding. The state is stored in the HTML using hidden tags. This approach ensures a smooth chat experience without the need for complex client-side JavaScript.

## Customization

The chat interface uses DaisyUI and Tailwind CSS for styling. You can customise the Tailwind of the chat page and we plan to add more customisability options.

## License

[MIT License](LICENSE)

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## Support

If you encounter any problems or have any questions, please open an issue on the GitHub repository.
