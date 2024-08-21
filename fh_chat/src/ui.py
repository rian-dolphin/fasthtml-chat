import json

from fasthtml.common import *


def ChatMessage(msg: str, user: bool, id: Optional[int] = None):
    bubble_class = "chat-bubble-primary" if user else "chat-bubble-secondary"
    chat_class = "chat-end" if user else "chat-start"
    return Div(cls=f"chat {chat_class}", id=f"message-{id}")(
        Div("user" if user else "assistant", cls="chat-header"),
        Div(
            msg,
            cls=f"chat-bubble {bubble_class}",
            id=f"message-{id}-content" if id else None,
        ),
        Hidden(
            json.dumps({"role": "user" if user else "assistant", "content": msg}),
            name="messages",
            id=f"message-{id}-hidden" if id else None,
        ),
    )


def ChatInput(
    swap_oob: bool = False,
    post_url: str = "/generate-message",
    placeholder: str = "Type a message",
    group_cls: Optional[str] = None,
    input_cls: str = "input-bordered",
    button_cls: str = "btn-primary",
):
    attrs = {
        "hx_post": post_url,
        "hx_target": "#chatlist",
        "hx_swap": "beforeend",
        "hx_ext": "chunked-transfer",
        "id": "chat-form",
        "hx_include": "[name='messages']",
        "hx_disabled_elt": "#msg-group",
    }
    if swap_oob:
        attrs["hx_swap_oob"] = "outerHTML"

    max_heights = {
        "default": "30vh",  # 30% of viewport height for smallest screens
        "sm": "35vh",  # 35% of viewport height for small screens
        "md": "40vh",  # 40% of viewport height for medium screens
        "lg": "45vh",  # 45% of viewport height for large screens
    }

    max_height_classes = (
        f"max-h-[{max_heights['default']}] "
        f"sm:max-h-[{max_heights['sm']}] "
        f"md:max-h-[{max_heights['md']}] "
        f"lg:max-h-[{max_heights['lg']}]"
    )

    auto_resize_script = """
function autoExpandTextarea() {
  const textarea = document.getElementById('msg-input');
  const form = document.getElementById('chat-form');
  if (!textarea || !form) return;

  function adjustHeight() {
    textarea.style.height = '2.5em';  // Reset height to minimum
    const maxHeight = window.innerHeight * getMaxHeightPercentage();
    let newHeight = Math.min(textarea.scrollHeight, maxHeight);
    textarea.style.height = newHeight + 'px';
    textarea.style.overflowY = textarea.scrollHeight > newHeight ? 'auto' : 'hidden';

    // Adjust the chat messages container
    const chatContainer = document.getElementById('chat-messages');
    if (chatContainer) {
      chatContainer.style.marginBottom = (form.offsetHeight + 16) + 'px';  // 16px for padding
    }
  }

  function getMaxHeightPercentage() {
    const width = window.innerWidth;
    if (width >= 1024) return 0.45;
    if (width >= 768) return 0.40;
    if (width >= 640) return 0.35;
    return 0.30;
  }

  textarea.addEventListener('input', adjustHeight);
  window.addEventListener('resize', adjustHeight);

  // Initial call to set the correct height
  adjustHeight();

  // Add event listener for Enter key
  textarea.addEventListener('keydown', function(e) {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      form.dispatchEvent(new Event('submit'));
    }
  });
}

// Call the function when the DOM is loaded
document.addEventListener('DOMContentLoaded', autoExpandTextarea);
// For HTMX: re-run the function after content is swapped
document.body.addEventListener('htmx:afterSwap', autoExpandTextarea);
    """

    component = Form(
        **attrs, cls="fixed bottom-0 left-0 right-0 bg-base-100 p-4 flex justify-center"
    )(
        Group(
            id="msg-group",
            cls=f"{group_cls} flex items-end w-3/4 sm:w-full md:w-2/3 lg:w-1/3",
        )(
            Textarea(
                name="msg",
                id="msg-input",
                placeholder=placeholder,
                cls=f"{input_cls} input flex-grow min-h-[3em] {max_height_classes} overflow-y-auto resize-none p-2",
            ),
            Button("Send", cls=f"btn {button_cls} flex-shrink-0"),
        )
    )
    return component, Script(auto_resize_script)


def ChatPage(
    include_style_headers: bool = False,
    title: Optional[str] = None,
    cls: str = "p-4 max-w-3xl mx-auto",
    view_height: str = 73,
):
    page = Div(cls=cls)(
        Div(id="chatlist", cls=f"chat-box h-[{view_height}vh] overflow-y-auto"),
        ChatInput(),
    )
    style_headers = [
        picolink,
        Script(src="https://cdn.tailwindcss.com"),
        Link(
            rel="stylesheet",
            href="https://cdn.jsdelivr.net/npm/daisyui@4.11.1/dist/full.min.css",
        ),
    ]
    return tuple(
        ([Title(title)] if title else [])
        + [
            page,
            Script(
                src="https://unpkg.com/htmx-ext-transfer-encoding-chunked@0.4.0/transfer-encoding-chunked.js"
            ),
        ]
        + (style_headers if include_style_headers else [])
    )
