from abc import ABC, abstractmethod
from typing import AsyncGenerator, List


class AIClient(ABC):
    def __init__(self, **kwargs):
        self.kwargs = kwargs

    @abstractmethod
    async def generate_stream(self, messages: List[dict]) -> AsyncGenerator[str, None]:
        pass


class AnthropicClient(AIClient):
    def __init__(self, client, **kwargs):
        super().__init__(**kwargs)
        self.client = client

    async def generate_stream(self, messages: List[dict]) -> AsyncGenerator[str, None]:
        try:
            with self.client.messages.stream(
                **self.kwargs, messages=messages
            ) as stream:
                for text in stream.text_stream:
                    yield text
        except Exception as e:
            print(f"Error in Anthropic stream generation: {str(e)}")
            yield f"An error occurred: {str(e)}"


class OpenAIClient(AIClient):
    def __init__(self, client, **kwargs):
        self.client = client
        self.system = kwargs.pop("system", "You are a helpful assistant.")
        super().__init__(**kwargs)

    async def generate_stream(self, messages: List[dict]) -> AsyncGenerator[str, None]:
        # Prepend the system message if a system prompt was provided
        # This is a workaround for OpenAI not supporting system prompts as a parameter
        if self.system:
            messages = [{"role": "system", "content": self.system}] + messages
        try:
            stream = self.client.chat.completions.create(
                messages=messages, stream=True, **self.kwargs
            )
            for chunk in stream:
                if chunk.choices[0].delta.content is not None:
                    yield chunk.choices[0].delta.content
        except Exception as e:
            print(f"Error in OpenAI stream generation: {str(e)}")
            yield f"An error occurred: {str(e)}"


class ClaudetteClient(AIClient):
    def __init__(self, client, **kwargs):
        super().__init__(**kwargs)
        self.client = client

    async def generate_stream(self, messages: List[dict]) -> AsyncGenerator[str, None]:
        try:
            response = self.client(messages, stream=True, **self.kwargs)
            for chunk in response:
                yield chunk
        except Exception as e:
            print(f"Error in Claudette stream generation: {str(e)}")
            yield f"An error occurred: {str(e)}"
