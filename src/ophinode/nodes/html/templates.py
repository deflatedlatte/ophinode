from ophinode.site.page import Page
from ophinode.site.layout import Layout
from .core import HTML5Doctype
from .elements import Html, Head, Body

class HTML5Page(Page):
    @property
    def layout(self):
        return HTML5Layout()

    def html_attributes(self, context: "ophinode.site.BuildContext") -> dict:
        return {}

    def head(self, context: "ophinode.site.BuildContext"):
        return []

    def body(self, context: "ophinode.site.BuildContext"):
        return []

class HTML5Layout(Layout):
    def build(self, page: HTML5Page, context: "ophinode.site.BuildContext"):
        return [
            HTML5Doctype(),
            Html(
                Head(
                    page.head(context)
                ),
                Body(
                    page.body(context)
                ),
                **page.html_attributes(context)
            )
        ]

