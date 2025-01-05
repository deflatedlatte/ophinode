# ophinode
`ophinode` is a static site generator written in Python that focuses on being
a simple and flexible library for generating HTML documents.

This project is currently in the initial development stage, and the APIs may
change at any time.

## Example programs

You can also get these example programs by running
`python -m ophinode examples`.

```python
# Example program: create a page in a directory.
#
# Running this program creates "index.html" in "./out" directory.
#
from ophinode.site import Site
from ophinode.nodes.html import *

class DefaultLayout(Layout):
    def build(self, page: Page, context: "ophinode.rendering.RenderContext"):
        return [
            HTML5Doctype(),
            Html(
                Head(
                    Meta(charset="utf-8"),
                    Title(page.title()),
                    page.head()
                ),
                Body(
                    page.body()
                ),
            )
        ]

class MainPage(HTML5Page):
    @property
    def layout(self):
        return DefaultLayout()

    def body(self):
        return Div(
            H1("Main Page"),
            P("Welcome to ophinode!")
        )

    def head(self):
        return []

    def title(self):
        return "Main Page"

if __name__ == "__main__":
    site = Site({
        "default_layout": DefaultLayout(),
        "export_root_path": "./out",
    }, [
        ("/", MainPage()),
    ])

    site.build_site()

```

```python
# Example program: render a page without defining a site.
#
# Running this program prints a HTML document to standard output.
#
from ophinode.site import render_page
from ophinode.nodes.html import *

class MainPage(HTML5Page):
    def body(self):
        return Div(
            H1("Main Page"),
            P("Welcome to ophinode!")
        )

    def head(self):
        return []

if __name__ == "__main__":
    print(render_page(MainPage()))

```
