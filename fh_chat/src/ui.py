from fasthtml.common import *

from fh_chat import ChatInput


def ChatInput():
    return Input(
        name="msg",
        id="msg-input",
        placeholder="Type a message",
        cls="input input-bordered w-full",
        hx_swap_oob="outerHTML",
    )
