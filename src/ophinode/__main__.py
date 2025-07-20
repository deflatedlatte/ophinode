import argparse

EXAMPLE1 = """# Example program: render a page without defining a site.
#
# Running this program prints a HTML document to standard output.
#
from ophinode import *

class MainPage:
    def body(self):
        return Div(
            H1("Main Page"),
            P("Welcome to ophinode!")
        )

    def head(self):
        return [
            Meta(charset="utf-8"),
            Title("Main Page")
        ]

print(render_page(MainPage(), HTML5Layout()))
"""

EXAMPLE2 = """# Example program: create a page in a directory.
#
# Running this program creates "index.html" in "./out" directory.
#
from ophinode import *

class DefaultLayout(Layout):
    def build(self, page, context):
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

class MainPage:
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
        "page_output_default_filename": "index.html",
    }, [
        ("/", MainPage()),
    ])

    site.build_site()
"""

def main():
    parser = argparse.ArgumentParser(prog="ophinode")
    parser.add_argument("subcommand", choices=["examples"])
    parser.add_argument("arguments", nargs="*")
    args = parser.parse_args()
    if args.subcommand == "examples":
        if not args.arguments:
            print("available examples: render_page, basic_site")
        elif args.arguments[0] == "render_page":
            print(EXAMPLE1)
        elif args.arguments[0] == "basic_site":
            print(EXAMPLE2)
        else:
            print("available examples: render_page, basic_site")
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
