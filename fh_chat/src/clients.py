from abc import ABC, abstractmethod
from typing import AsyncGenerator, List


class AIClient(ABC):
    @abstractmethod
    async def generate_stream(
        self, messages: List[dict], **kwargs
    ) -> AsyncGenerator[str, None]:
        pass

    @staticmethod
    def get_system_prompt(keywor_args):
        sp = keywor_args.get("system_prompt")
        if not sp:
            raise ValueError("system_prompt is required")
        return sp


class AnthropicClient(AIClient):
    def __init__(self, client, model_name: str, max_tokens: int = 1000):
        self.client = client
        self.model_name = model_name
        self.max_tokens = max_tokens

    async def generate_stream(
        self, messages: List[dict], **kwargs
    ) -> AsyncGenerator[str, None]:
        with self.client.messages.stream(
            max_tokens=self.max_tokens,
            messages=messages,
            model=self.model_name,
            system=AIClient.get_system_prompt(kwargs),
        ) as stream:
            for text in stream.text_stream:
                yield text


class OpenAIClient(AIClient):
    def __init__(self, client, model_name: str):
        self.client = client
        self.model_name = model_name

    async def generate_stream(
        self, messages: List[dict], **kwargs
    ) -> AsyncGenerator[str, None]:
        messages = [
            {"role": "system", "content": AIClient.get_system_prompt(kwargs)}
        ] + messages
        stream = self.client.chat.completions.create(
            model=self.model_name,
            messages=messages,
            stream=True,
        )
        for chunk in stream:
            if chunk.choices[0].delta.content is not None:
                yield chunk.choices[0].delta.content


class ClaudetteClient(AIClient):
    def __init__(self, client):
        self.client = client

    async def generate_stream(
        self, messages: List[dict], **kwargs
    ) -> AsyncGenerator[str, None]:
        system_prompt = AIClient.get_system_prompt(kwargs)
        response = self.client(messages, sp=system_prompt, stream=True)
        for chunk in response:
            yield chunk
