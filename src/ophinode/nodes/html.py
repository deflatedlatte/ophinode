from .base import *

class HTML5Layout(Layout):
    def build(self, page: Page, context: "ophinode.rendering.RenderContext"):
        return [
            HTML5Doctype(),
            Html(
                Head(
                    page.head()
                ),
                Body(
                    page.body()
                )
            )
        ]

class HTML5Page(Page):
    @property
    def layout(self):
        return HTML5Layout()

    @abstractmethod
    def head(self):
        pass

    @abstractmethod
    def body(self):
        pass

class Node:
    pass

class TextNode(Node, ClosedRenderable):
    def __init__(self, text_content: str):
        self._text_content = text_content

    def render(self, context: "ophinode.rendering.RenderContext"):
        return self._text_content

class HTML5Doctype(Node, ClosedRenderable):
    def render(self, context: "ophinode.rendering.RenderContext"):
        return "<!doctype html>"

class Element(Node):
    def render_attributes(self):
        attribute_order = []
        keys = set(self.attributes)
        for k in ["id", "class", "style", "title"]:
            if k in keys:
                attribute_order.append(k)
                keys.remove(k)
        attribute_order += sorted(keys)

        rendered = []
        for k in attribute_order:
            v = self.attributes[k]
            if v is not None:
                rendered.append("{}=\"{}\"".format(k, v))
            else:
                rendered.append("{}".format(k))

        return " ".join(rendered)

class OpenElement(Element, OpenRenderable, Expandable, Preparable):
    display = "block"
    tag = "div"

    def __init__(self, *args, **kwargs):
        self.children = list(args)
        self.attributes = dict(kwargs)

    def prepare(self, context: "ophinode.rendering.RenderContext"):
        for c in self.children:
            if isinstance(c, Preparable):
                c.prepare(context)

    def expand(self, context: "ophinode.rendering.RenderContext"):
        return self.children.copy()

    def render_start(self, context: "ophinode.rendering.RenderContext"):
        rendered_attributes = self.render_attributes()
        if rendered_attributes:
            return "<{} {}>".format(self.tag, rendered_attributes)
        return "<{}>".format(self.tag)

    def render_end(self, context: "ophinode.rendering.RenderContext"):
        return "</{}>".format(self.tag)

class ClosedElement(Element, ClosedRenderable):
    tag = "meta"

    def __init__(self, **kwargs):
        self.attributes = dict(kwargs)

    def render(self, context: "ophinode.rendering.RenderContext"):
        rendered_attributes = self.render_attributes()
        if rendered_attributes:
            return "<{} {}>".format(self.tag, rendered_attributes)
        return "<{}>".format(self.tag)

class Html(OpenElement):
    tag = "html"

class Head(OpenElement):
    tag = "head"

class Body(OpenElement):
    tag = "body"

class Meta(ClosedElement):
    tag = "meta"

class Title(OpenElement):
    tag = "title"

class Paragraph(OpenElement):
    tag = "p"

class Division(OpenElement):
    tag = "div"

