import argparse

EXAMPLE1 = """# Example program: create a page in a directory.
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
"""

EXAMPLE2 = """# Example program: render a page without defining a site.
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
"""

def main():
    parser = argparse.ArgumentParser(prog="ophinode")
    parser.add_argument("subcommand", choices=["examples"])
    parser.add_argument("arguments", nargs="*")
    args = parser.parse_args()
    if args.subcommand == "examples":
        if not args.arguments:
            print("available examples: basic_site, render_page")
        elif args.arguments[0] == "basic_site":
            print(EXAMPLE1)
        elif args.arguments[0] == "render_page":
            print(EXAMPLE2)
        else:
            print("available examples: basic_site")
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
