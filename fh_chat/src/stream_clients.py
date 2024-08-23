import asyncio

from anthropic import Anthropic
from fasthtml.common import *

from fh_chat import ChatInput, ChatMessage


def validate_custom_input_ft(custom_input_ft: FT):
    if custom_input_ft.tag not in ["input", "textarea"]:
        raise ValueError("custom_input_ft must be an input or textarea element.")

    attributes: dict = custom_input_ft.attrs
    if "name" not in attributes:
        custom_input_ft.attrs["name"] = "msg"
    elif attributes.get("name") != "msg":
        raise ValueError("custom_input_ft must have 'name' attribute set to 'msg'.")
    if "id" not in attributes:
        custom_input_ft.attrs["id"] = "msg-input"
    if "hx_swap_oob" not in attributes:
        custom_input_ft.attrs["hx_swap_oob"] = "outerHTML"
    elif attributes.get("hx_swap_oob") != "outerHTML":
        raise ValueError(
            "custom_input_ft must have 'hx_swap_oob' attribute set to 'outerHTML'."
        )
    if "placeholder" not in attributes:
        custom_input_ft.attrs["placeholder"] = "Type a message..."


async def stream_response_anthropic(
    all_messages: list[dict],
    client: Anthropic,
    model_name: str,
    system_prompt: str,
    max_tokens: int = 1000,
    custom_input_ft: FT = None,
    **kwargs,
):
    if custom_input_ft is not None:
        validate_custom_input_ft(custom_input_ft)
    else:
        custom_input_ft = ChatInput()

    user_msg_id = len(all_messages) - 1
    assistant_msg_id = len(all_messages)

    user_message = ChatMessage("user", user_msg_id, all_messages[-1]["content"])
    yield to_xml(user_message.initial_render())

    assistant_message = ChatMessage("assistant", assistant_msg_id)
    yield to_xml(assistant_message.initial_render())

    with client.messages.stream(
        max_tokens=max_tokens,
        messages=all_messages,
        model=model_name,
        system=system_prompt,
        **kwargs,
    ) as stream:
        for text in stream.text_stream:
            content_update, hidden_update = assistant_message.update_content(text)
            yield to_xml(content_update)
            yield to_xml(hidden_update)
            await asyncio.sleep(0.05)

    yield to_xml(custom_input_ft)
