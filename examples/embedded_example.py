"""Example of embedding a chat component in a larger application."""

from fasthtml.common import *
from keys import ANTHROPIC_API_KEY

from fh_chat import ChatApp, ChatTheme

# Set up FastHTML app
app, _ = fast_app(pico=False)

# Create a ChatApp instance
chat_app = ChatApp(
    app,
    model_provider="anthropic",
    api_key=ANTHROPIC_API_KEY,
    theme=ChatTheme.BUBBLE,
    base_route="/api/chat",
)

# Add default chat route for API endpoints
chat_app.add_chat_route()


# Product dashboard application with embedded chat
@app.get("/")
def dashboard():
    return Div(cls="container mx-auto bg-white shadow-lg rounded-lg overflow-hidden")(
        # Header
        Div(
            cls="flex items-center p-4 border-b",
        )(
            H1("Product Dashboard", cls="text-2xl font-bold"),
            Div(A("Logout", href="#", cls="text-sm text-gray-600"), cls="ml-auto"),
        ),
        # Main content area with sidebar and content
        Div(cls="flex min-h-screen")(
            # Sidebar
            Div(cls="w-1/4 p-4 border-r")(
                Div(cls="mb-6")(
                    H2("Navigation", cls="font-bold mb-4"),
                    Ul(cls="space-y-1")(
                        Li(
                            A(
                                "Dashboard",
                                href="#",
                                cls="block p-2 hover:bg-gray-100 rounded",
                            )
                        ),
                        Li(
                            A(
                                "Products",
                                href="#",
                                cls="block p-2 hover:bg-gray-100 rounded",
                            )
                        ),
                        Li(
                            A(
                                "Analytics",
                                href="#",
                                cls="block p-2 hover:bg-gray-100 rounded",
                            )
                        ),
                        Li(
                            A(
                                "Settings",
                                href="#",
                                cls="block p-2 hover:bg-gray-100 rounded",
                            )
                        ),
                    ),
                ),
                # Embedded chat in sidebar
                Div(cls="mt-6")(
                    H2("Product Assistant", cls="font-bold mb-4"),
                    # Here we embed the chat component with custom configuration
                    chat_app.embed_chat(
                        element_id="product-assistant",
                        height="400px",
                        placeholder="Ask about products",
                        button_text="Ask",
                        container_class="border rounded-lg shadow-sm",
                        system_prompt="You are a product specialist who can answer questions about our product catalog.",
                    ),
                ),
            ),
            # Main content
            Div(cls="w-3/4 p-4")(
                H2("Recent Products", cls="text-xl font-bold mb-4"),
                # Product cards grid
                Div(cls="grid grid-cols-3 gap-4")(
                    *[
                        Div(
                            cls="border rounded-lg p-4 shadow-sm",
                        )(
                            Div(f"Product {i}", cls="font-bold"),
                            P(f"Description for product {i}"),
                            Div(f"${i * 10}.99", cls="font-bold mt-2"),
                        )
                        for i in range(1, 7)
                    ],
                ),
            ),
        ),
    )


# Product details page with a specific embedded chat
@app.get("/product/{product_id}")
def product_detail(product_id: int):
    return Titled(
        f"Product {product_id}",
        Div(cls="container mx-auto p-6 bg-white shadow-lg rounded-lg")(
            # Product header
            Div(cls="mb-6")(
                H1(f"Product {product_id}", cls="text-2xl font-bold"),
                Div(f"${product_id * 10}.99", cls="text-xl font-bold text-green-600"),
            ),
            # Main content with product details and embedded chat
            Div(cls="flex mt-8")(
                # Product details
                Div(cls="w-2/3 pr-8")(
                    H2("Description", cls="text-xl font-bold mb-2"),
                    P(
                        f"This is a detailed description of product {product_id}. It includes all the features and benefits you need to know."
                    ),
                    Div(
                        H2("Specifications", cls="text-xl font-bold mt-6 mb-2"),
                        Ul(cls="list-disc pl-6")(
                            Li("Dimension: 10x15x5 cm"),
                            Li("Weight: 250g"),
                            Li("Material: Premium quality"),
                            Li("Color: Various options"),
                        ),
                    ),
                ),
                # Product-specific chat
                Div(cls="w-1/3")(
                    chat_app.embed_chat(
                        element_id=f"product-{product_id}-chat",
                        theme=ChatTheme.MINIMAL,
                        height="350px",
                        title=f"Ask about Product {product_id}",
                        placeholder="Any questions about this product?",
                        button_text="Ask",
                        container_class="border rounded-lg p-4",
                        system_prompt=f"You are a product specialist for Product {product_id}. Provide helpful and accurate information about this specific product.",
                    ),
                ),
            ),
            # Navigation links
            Div(cls="flex")(
                A("Back to Dashboard", href="/", cls="btn btn-outline mt-8 mr-2"),
                A("Add to Cart", href="#", cls="btn btn-primary mt-8"),
            ),
        ),
    )


if __name__ == "__main__":
    serve()
