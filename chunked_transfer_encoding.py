import asyncio

from fasthtml.common import *
from starlette.responses import StreamingResponse

htmxlink = Script(
    src="https://unpkg.com/htmx-ext-transfer-encoding-chunked@0.2.0/transfer-encoding-chunked.js"
)
app = FastHTML(hdrs=(picolink, htmxlink), live=True)


async def message_generator():
    for i in range(10):
        yield to_xml(Div(f"chunk {i}"))
        await asyncio.sleep(0.15)


@app.route("/")
def get():
    page = Main(
        H1("transfer encoding chunked demo"),
        Button(
            "Get Message",
            hx_get="/get-message",
            hx_target="#message",
            hx_swap="beforeend",
            hx_ext="chunked-transfer",
        ),
        Div(id="message"),
    )
    return Title("Chunked Transfer Demo"), page


@app.get("/get-message")
async def get_message():
    async def streaming_content():
        async for chunk in message_generator():
            yield chunk

    response = StreamingResponse(streaming_content(), media_type="text/html")
    response.headers["Transfer-Encoding"] = "chunked"
    return response


serve()
