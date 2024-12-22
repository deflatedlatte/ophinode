# ophinode
A static site generator written in Python

This project is currently in the initial development stage, and the APIs may change at any time.

## Example program

```python
from ophinode.site import Site
from ophinode.nodes.html import *

class MyHTML5Layout(Layout):
    def build(self, page: Page, context: "ophinode.rendering.RenderContext"):
        return [
            HTML5Doctype(),
            Html(
                Head(
                    Meta(charset="utf-8"),
                    Title("My first page"),
                    page.head()
                ),
                Body(
                    page.body()
                ),
                lang="en"
            )
        ]

class MainPage(HTML5Page):
    @property
    def layout(self):
        return MyHTML5Layout()

    def body(self):
        return Division(
            Paragraph(
                "Hello, nice to meet you!",
                id="first-paragraph",
            ),
            Paragraph(
                "This is a paragraph.",
                id="second-paragraph",
            ),
        )

    def head(self):
        return []

renderer = Site({
    "default_layout": MyHTML5Layout(),
    "root_path": "./out",
}, [
    ("/", MainPage()),
])

renderer.build()
```
