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

Check out the examples [here](https://github.com/rian-dolphin/fasthtml-chat/tree/main/examples) to get started. As with any FastHTML app you can run them using python like:

```bash
python examples/min_example.py
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
