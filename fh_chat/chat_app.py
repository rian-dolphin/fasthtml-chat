"""Main ChatApp class for FastHTMLChat."""

from typing import Callable, Optional, Union

from fasthtml.common import Titled
from starlette.responses import StreamingResponse

from .components.chat import Chat, get_chat_headers
from .components.message import ChatTheme
from .models.registry import ModelProvider, get_model_provider
from .utils.history import ChatHistory
from .utils.streaming import stream_chat_response


class ChatApp:
    """
    Main class for setting up GenAI chat routes in a FastHTML application.
    """

    def __init__(
        self,
        app,
        model_provider: Union[str, ModelProvider] = "anthropic",
        system_prompt: str = "You are a helpful assistant.",
        model_name: Optional[str] = None,
        api_key: Optional[str] = None,
        max_tokens: int = 1000,
        theme: str = ChatTheme.DEFAULT,
        base_route: str = "/chat",
        chunked_transfer: bool = True,
        streaming_delay: float = 0.05,
        message_preprocessor: Optional[Callable[[str], str]] = None,
        setup_headers: bool = True,
        **model_kwargs,
    ):
        """
        Initialize a ChatApp instance.

        Args:
            app: FastHTML application
            model_provider: Model provider name or instance
            system_prompt: Default system prompt
            model_name: Default model name (provider-specific)
            api_key: API key for the model provider
            max_tokens: Maximum tokens to generate per response
            theme: UI theme to use
            base_route: Base route for chat endpoints
            chunked_transfer: Whether to use chunked transfer encoding
            streaming_delay: Delay between streaming chunks
            message_preprocessor: Optional function to preprocess messages
            setup_headers: Whether to automatically add required headers to app
            **model_kwargs: Additional arguments for the model provider
        """
        self.app = app
        self.theme = theme
        self.base_route = base_route.rstrip("/")
        self.chunked_transfer = chunked_transfer
        self.streaming_delay = streaming_delay
        self.message_preprocessor = message_preprocessor
        self.max_tokens = max_tokens
        self.system_prompt = system_prompt

        # Configure model provider
        if isinstance(model_provider, str):
            self.model_provider = get_model_provider(
                model_provider, api_key=api_key, **model_kwargs
            )
        else:
            self.model_provider = model_provider

        # Set default model
        self.model_name = model_name or self.model_provider.get_available_models()[0]

        # Dictionary to store additional chat configurations
        self.chat_configs = {}

        # Add required headers if requested
        if setup_headers:
            for header in get_chat_headers():
                if header not in app.hdrs:
                    app.hdrs = app.hdrs + [header]

    def add_chat_route(
        self,
        route_path: str = "",
        system_prompt: Optional[str] = None,
        model_name: Optional[str] = None,
        max_tokens: Optional[int] = None,
        theme: Optional[str] = None,
        title: Optional[str] = None,
        **route_kwargs,
    ):
        """
        Add a chat route with specific configuration.

        Args:
            route_path: Route path suffix (appended to base_route)
            system_prompt: System prompt for this route
            model_name: Model name for this route
            max_tokens: Max tokens for this route
            theme: Theme for this route
            title: Title for the chat page
            **route_kwargs: Additional route-specific configuration
        """
        full_path = f"{self.base_route}{route_path}"

        # Store configuration for this route
        self.chat_configs[full_path] = {
            "system_prompt": system_prompt or self.system_prompt,
            "model_name": model_name or self.model_name,
            "max_tokens": max_tokens or self.max_tokens,
            "theme": theme or self.theme,
            "title": title or f"AI Chat{' - ' + route_path if route_path else ''}",
            **route_kwargs,
        }

        # Register routes
        self._register_routes(full_path)

    def _register_routes(self, route_path: str):
        """Register all required routes for a chat endpoint."""
        config = self.chat_configs[route_path]

        # Main chat page route
        @self.app.get(route_path)
        def chat_page():
            return Titled(
                config["title"],
                Chat(
                    theme=config["theme"],
                    post_url=f"{route_path}/generate",
                    height=config.get("height", "70vh"),
                    button_text=config.get("button_text", "Send"),
                    placeholder=config.get("placeholder", "Type a message"),
                    container_class=config.get("container_class", ""),
                    title=config.get("display_title", config["title"]),
                ),
            )

        # Message generation route
        @self.app.post(f"{route_path}/generate")
        async def generate_message(
            msg: str,
            messages: list[str] = None,
        ):
            # Use the route-specific configuration
            system_prompt = config["system_prompt"]
            model_name = config["model_name"]
            max_tokens = config["max_tokens"]
            theme = config["theme"]

            # Parse and validate messages
            parsed_messages = ChatHistory.parse_messages(messages)

            # Add user message
            parsed_messages.append({"role": "user", "content": msg.rstrip()})

            # Limit history to prevent token overflow
            limited_messages = ChatHistory.limit_history(
                parsed_messages,
                max_messages=config.get("max_messages"),
                max_tokens=config.get("max_tokens_history"),
            )

            # Create stream generator from model provider
            model_stream = self.model_provider.generate_stream(
                messages=limited_messages,
                system_prompt=system_prompt,
                model_name=model_name,
                max_tokens=max_tokens,
                **config.get("model_kwargs", {}),
            )

            # Create response stream
            async def response_stream():
                async for chunk in stream_chat_response(
                    model_stream,
                    msg,
                    messages=parsed_messages,
                    theme=theme,
                    post_url=f"{route_path}/generate",
                    delay=self.streaming_delay,
                    message_preprocessor=self.message_preprocessor,
                ):
                    yield chunk

            # Set up chunked transfer encoding
            response = StreamingResponse(response_stream(), media_type="text/html")

            if self.chunked_transfer:
                response.headers["X-Transfer-Encoding"] = "chunked"

            return response

    def embed_chat(
        self,
        element_id: str = "embedded-chat",
        theme: Optional[str] = None,
        height: str = "400px",
        post_url: Optional[str] = None,
        system_prompt: Optional[str] = None,
        model_name: Optional[str] = None,
        title: Optional[str] = None,
        **kwargs,
    ):
        """
        Create a chat component that can be embedded in another page.

        Args:
            element_id: ID for the chat container
            theme: Theme to use (defaults to instance theme)
            height: Height of the chat area
            post_url: URL to post messages to (defaults to base_route/generate)
            system_prompt: System prompt for this embedded chat
            model_name: Model name for this embedded chat
            title: Title to display above the chat
            **kwargs: Additional arguments for the Chat component

        Returns:
            A FastHTML Chat component
        """
        # Use provided post_url or default
        if post_url is None:
            # Create a unique endpoint for this embedded chat
            post_url = f"{self.base_route}/embedded/{element_id}/generate"

            # Register the endpoint with specific configuration
            self.chat_configs[post_url] = {
                "system_prompt": system_prompt or self.system_prompt,
                "model_name": model_name or self.model_name,
                "max_tokens": kwargs.get("max_tokens", self.max_tokens),
                "theme": theme or self.theme,
                **kwargs,
            }

            # Register route for this embedded chat
            @self.app.post(post_url)
            async def generate_message_embedded(
                msg: str,
                messages: list[str] = None,
            ):
                config = self.chat_configs[post_url]
                system_prompt = config["system_prompt"]
                model_name = config["model_name"]
                max_tokens = config.get("max_tokens", self.max_tokens)
                theme = config["theme"]

                parsed_messages = ChatHistory.parse_messages(messages)
                parsed_messages.append({"role": "user", "content": msg.rstrip()})

                limited_messages = ChatHistory.limit_history(
                    parsed_messages,
                    max_messages=config.get("max_messages"),
                    max_tokens=config.get("max_tokens_history"),
                )

                model_stream = self.model_provider.generate_stream(
                    messages=limited_messages,
                    system_prompt=system_prompt,
                    model_name=model_name,
                    max_tokens=max_tokens,
                    **config.get("model_kwargs", {}),
                )

                async def response_stream():
                    async for chunk in stream_chat_response(
                        model_stream,
                        msg,
                        messages=parsed_messages,
                        theme=theme,
                        post_url=post_url,
                        delay=self.streaming_delay,
                        message_preprocessor=self.message_preprocessor,
                    ):
                        yield chunk

                response = StreamingResponse(response_stream(), media_type="text/html")

                if self.chunked_transfer:
                    response.headers["X-Transfer-Encoding"] = "chunked"

                return response

        return Chat(
            id=element_id,
            theme=theme or self.theme,
            height=height,
            post_url=post_url,
            title=title,
            **kwargs,
        )
