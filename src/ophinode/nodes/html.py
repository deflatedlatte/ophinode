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
        self._escape_ampersands = True

    def render(self, context: "ophinode.rendering.RenderContext"):
        text_content = self._text_content
        if self._escape_ampersands:
            text_content = text_content.replace("&", "&amp;")
        text_content = text_content.replace("<", "&lt;").replace(">", "&gt;")
        return text_content

    def escape_ampersands(self, value: bool = True):
        self._escape_ampersands = bool(value)
        return self

class HTML5Doctype(Node, ClosedRenderable):
    def render(self, context: "ophinode.rendering.RenderContext"):
        return "<!doctype html>"

class CDATASection(Node, OpenRenderable, Expandable, Preparable):
    def __init__(self, *args):
        self.children = list(args)

    def prepare(self, context: "ophinode.rendering.RenderContext"):
        for c in self.children:
            if isinstance(c, Preparable):
                c.prepare(context)

    def expand(self, context: "ophinode.rendering.RenderContext"):
        return self.children.copy()

    def render_start(self, context: "ophinode.rendering.RenderContext"):
        return "<![CDATA[".format(self.tag)

    def render_end(self, context: "ophinode.rendering.RenderContext"):
        return "]]>".format(self.tag)

    @property
    def auto_newline(self):
        return False

    @property
    def auto_indent(self):
        return False

class Comment(Node, OpenRenderable, Expandable, Preparable):
    def __init__(self, *args):
        self.children = list(args)

    def prepare(self, context: "ophinode.rendering.RenderContext"):
        for c in self.children:
            if isinstance(c, Preparable):
                c.prepare(context)

    def expand(self, context: "ophinode.rendering.RenderContext"):
        return self.children.copy()

    def render_start(self, context: "ophinode.rendering.RenderContext"):
        return "<!--".format(self.tag)

    def render_end(self, context: "ophinode.rendering.RenderContext"):
        return "-->".format(self.tag)

    @property
    def auto_newline(self):
        return False

    @property
    def auto_indent(self):
        return False

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
            for c in k:
                if c in " \"'>/=":
                    raise InvalidAttributeNameError(k)
            v = self.attributes[k]
            if v is not None:
                escaped = str(v)
                if self._escape_ampersands:
                    escaped = escaped.replace("&", "&amp;")
                escaped = escaped.replace("\"", "&quot;")
                rendered.append("{}=\"{}\"".format(k, escaped))
            else:
                rendered.append("{}".format(k))

        return " ".join(rendered)

    def escape_ampersands(self, value: bool = True):
        self._escape_ampersands = bool(value)
        return self

class OpenElement(Element, OpenRenderable, Expandable, Preparable):
    tag = "div"
    render_mode = "hierarchy"

    def __init__(self, *args, **kwargs):
        self.children = list(args)
        self.attributes = dict(kwargs)
        self._escape_ampersands = True

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

    @property
    def auto_newline(self):
        return self.render_mode == "hierarchy"

    @property
    def auto_indent(self):
        return self.render_mode == "phrase" or self.render_mode == "hierarchy"

class ClosedElement(Element, ClosedRenderable):
    tag = "meta"

    def __init__(self, **kwargs):
        self.attributes = dict(kwargs)
        self._escape_ampersands = True

    def render(self, context: "ophinode.rendering.RenderContext"):
        rendered_attributes = self.render_attributes()
        if rendered_attributes:
            return "<{} {}>".format(self.tag, rendered_attributes)
        return "<{}>".format(self.tag)

# --- The document element ---

class HtmlElement(OpenElement):
    tag = "html"

Html = HtmlElement

# --- Document metadata ---

class HeadElement(OpenElement):
    tag = "head"

class TitleElement(OpenElement):
    tag = "title"
    render_mode = "inline"

class BaseElement(ClosedElement):
    tag = "base"

class LinkElement(ClosedElement):
    tag = "link"

class MetaElement(ClosedElement):
    tag = "meta"

class StyleElement(OpenElement):
    tag = "style"

Head = HeadElement
Title = TitleElement
Base = BaseElement
Link = LinkElement
Meta = MetaElement
Style = StyleElement

# --- Sections ---

class BodyElement(OpenElement):
    tag = "body"

class ArticleElement(OpenElement):
    tag = "article"

class SectionElement(OpenElement):
    tag = "section"

class NavigationElement(OpenElement):
    tag = "nav"

class AsideElement(OpenElement):
    tag = "aside"

class HeadingLevel1Element(OpenElement):
    tag = "h1"
    render_mode = "inline"

class HeadingLevel2Element(OpenElement):
    tag = "h2"
    render_mode = "inline"

class HeadingLevel3Element(OpenElement):
    tag = "h3"
    render_mode = "inline"

class HeadingLevel4Element(OpenElement):
    tag = "h4"
    render_mode = "inline"

class HeadingLevel5Element(OpenElement):
    tag = "h5"
    render_mode = "inline"

class HeadingLevel6Element(OpenElement):
    tag = "h6"
    render_mode = "inline"

class HeadingGroupElement(OpenElement):
    tag = "hgroup"

class HeaderElement(OpenElement):
    tag = "header"

class FooterElement(OpenElement):
    tag = "footer"

class AddressElement(OpenElement):
    tag = "address"

Body = BodyElement
Article = ArticleElement
Section = SectionElement
Nav = NavigationElement
Aside = AsideElement
H1 = HeadingLevel1Element
H2 = HeadingLevel2Element
H3 = HeadingLevel3Element
H4 = HeadingLevel4Element
H5 = HeadingLevel5Element
H6 = HeadingLevel6Element
HGroup = HeadingGroupElement
Header = HeaderElement
Footer = FooterElement
Address = AddressElement

# --- Grouping content ---

class ParagraphElement(OpenElement):
    tag = "p"
    render_mode = "phrase"

class HorizontalRuleElement(ClosedElement):
    tag = "hr"

class PreformattedTextElement(OpenElement):
    tag = "pre"
    render_mode = "pre"

class BlockQuotationElement(OpenElement):
    tag = "blockquote"

class OrderedListElement(OpenElement):
    tag = "ol"

class UnorderedListElement(OpenElement):
    tag = "ul"

class MenuElement(OpenElement):
    tag = "menu"

class ListItemElement(OpenElement):
    tag = "li"

class DescriptionListElement(OpenElement):
    tag = "dl"

class DescriptionTermElement(OpenElement):
    tag = "dt"
    render_mode = "inline"

class DescriptionDetailsElement(OpenElement):
    tag = "dd"
    render_mode = "inline"

class FigureElement(OpenElement):
    tag = "figure"

class FigureCaptionElement(OpenElement):
    tag = "figcaption"

class MainElement(OpenElement):
    tag = "main"

class SearchElement(OpenElement):
    tag = "search"

class DivisionElement(OpenElement):
    tag = "div"

P = ParagraphElement
HR = HorizontalRuleElement
Pre = PreformattedTextElement
BlockQuote = BlockQuotationElement
OL = OrderedListElement
UL = UnorderedListElement
Menu = MenuElement
LI = ListItemElement
DL = DescriptionListElement
DT = DescriptionTermElement
DD = DescriptionDetailsElement
Figure = FigureElement
FigCaption = FigureCaptionElement
Main = MainElement
Search = SearchElement
Div = DivisionElement

# --- Text-level semantics ---

class AnchorElement(OpenElement):
    tag = "a"

class EmphasisElement(OpenElement):
    tag = "em"
    render_mode = "inline"

class StrongImportanceElement(OpenElement):
    tag = "strong"
    render_mode = "inline"

class SmallPrintElement(OpenElement):
    tag = "small"
    render_mode = "inline"

class StrikethroughElement(OpenElement):
    tag = "s"
    render_mode = "inline"

class CitationElement(OpenElement):
    tag = "cite"
    render_mode = "inline"

class QuotationElement(OpenElement):
    tag = "q"
    render_mode = "inline"

class DefinitionElement(OpenElement):
    tag = "dfn"
    render_mode = "inline"

class AbbreviationElement(OpenElement):
    tag = "abbr"
    render_mode = "inline"

class RubyAnnotationElement(OpenElement):
    tag = "ruby"
    render_mode = "inline"

class RubyTextElement(OpenElement):
    tag = "rt"
    render_mode = "inline"

class RubyParenthesesElement(OpenElement):
    tag = "rp"
    render_mode = "inline"

class DataElement(OpenElement):
    tag = "data"
    render_mode = "inline"

class TimeElement(OpenElement):
    tag = "time"
    render_mode = "inline"

class CodeElement(OpenElement):
    tag = "code"
    render_mode = "inline"

class VariableElement(OpenElement):
    tag = "var"
    render_mode = "inline"

class SampleElement(OpenElement):
    tag = "samp"
    render_mode = "inline"

class KeyboardInputElement(OpenElement):
    tag = "kbd"
    render_mode = "inline"

class SubscriptElement(OpenElement):
    tag = "sub"
    render_mode = "inline"

class SuperscriptElement(OpenElement):
    tag = "sup"
    render_mode = "inline"

class ItalicTextElement(OpenElement):
    tag = "i"
    render_mode = "inline"

class BoldTextElement(OpenElement):
    tag = "b"
    render_mode = "inline"

class UnarticulatedAnnotationElement(OpenElement):
    tag = "u"
    render_mode = "inline"

class MarkedTextElement(OpenElement):
    tag = "mark"
    render_mode = "inline"

class MarkedTextElement(OpenElement):
    tag = "mark"
    render_mode = "inline"

class BidirectionalIsolateElement(OpenElement):
    tag = "bdi"
    render_mode = "inline"

class BidirectionalOverrideElement(OpenElement):
    tag = "bdo"
    render_mode = "inline"

class SpanElement(OpenElement):
    tag = "span"
    render_mode = "inline"

class LineBreakElement(ClosedElement):
    tag = "br"

class LineBreakOpportunityElement(ClosedElement):
    tag = "wbr"

A = AnchorElement
EM = EmphasisElement
Strong = StrongImportanceElement
Small = SmallPrintElement
S = StrikethroughElement
Cite = CitationElement
Q = QuotationElement
Dfn = DefinitionElement
Abbr = AbbreviationElement
Ruby = RubyAnnotationElement
RT = RubyTextElement
RP = RubyParenthesesElement
Data = DataElement
Time = TimeElement
Code = CodeElement
Var = VariableElement
Samp = SampleElement
Kbd = KeyboardInputElement
Sub = SubscriptElement
Sup = SuperscriptElement
I = ItalicTextElement
B = BoldTextElement
U = UnarticulatedAnnotationElement
Mark = MarkedTextElement
BDI = BidirectionalIsolateElement
BDO = BidirectionalOverrideElement
Span = SpanElement
BR = LineBreakElement
WBR = LineBreakOpportunityElement

# --- Edits ---

class InsertionElement(OpenElement):
    tag = "ins"

class DeletionElement(OpenElement):
    tag = "del"
    render_mode = "inline"

Ins = InsertionElement
Del = DeletionElement

# --- Embedded content ---

class PictureElement(OpenElement):
    tag = "picture"

class SourceElement(ClosedElement):
    tag = "source"

class ImageElement(ClosedElement):
    tag = "image"

class InlineFrameElement(OpenElement):
    tag = "iframe"

class EmbeddedContentElement(ClosedElement):
    tag = "embed"

class ExternalObjectElement(OpenElement):
    tag = "object"

class VideoElement(OpenElement):
    tag = "video"

class AudioElement(OpenElement):
    tag = "audio"

class TextTrackElement(ClosedElement):
    tag = "track"

class ImageMapElement(OpenElement):
    tag = "map"

class ImageMapAreaElement(ClosedElement):
    tag = "area"

Picture = PictureElement
Source = SourceElement
Image = ImageElement
IFrame = InlineFrameElement
Embed = EmbeddedContentElement
Object = ExternalObjectElement
Video = VideoElement
Audio = AudioElement
Track = TextTrackElement
Map = ImageMapElement
Area = ImageMapAreaElement

# --- Tabular data ---

class TableElement(OpenElement):
    tag = "table"

class TableCaptionElement(OpenElement):
    tag = "caption"

class TableColumnGroupElement(OpenElement):
    tag = "colgroup"

class TableColumnElement(ClosedElement):
    tag = "col"

class TableBodyElement(OpenElement):
    tag = "tbody"

class TableHeadElement(OpenElement):
    tag = "thead"

class TableFootElement(OpenElement):
    tag = "tfoot"

class TableRowElement(OpenElement):
    tag = "tr"

class TableDataCellElement(OpenElement):
    tag = "td"

class TableHeaderCellElement(OpenElement):
    tag = "th"

Table = TableElement
Caption = TableCaptionElement
ColGroup = TableColumnGroupElement
Column = TableColumnElement
TBody = TableBodyElement
THead = TableHeadElement
TFoot = TableFootElement
TR = TableRowElement
TD = TableDataCellElement
TH = TableHeaderCellElement

# --- Forms ---

class FormElement(OpenElement):
    tag = "form"

class LabelElement(OpenElement):
    tag = "label"

class InputElement(ClosedElement):
    tag = "input"

class ButtonElement(OpenElement):
    tag = "button"

class SelectElement(OpenElement):
    tag = "select"

class DataListElement(OpenElement):
    tag = "datalist"

class OptionGroupElement(OpenElement):
    tag = "optgroup"

class OptionElement(OpenElement):
    tag = "option"

class TextAreaElement(OpenElement):
    tag = "textarea"
    render_mode = "pre"

class OutputElement(OpenElement):
    tag = "output"

class ProgressElement(OpenElement):
    tag = "progress"
    render_mode = "inline"

class MeterElement(OpenElement):
    tag = "meter"
    render_mode = "inline"

class FieldSetElement(OpenElement):
    tag = "fieldset"

class FieldSetLegendElement(OpenElement):
    tag = "legend"
    render_mode = "inline"

Form = FormElement
Label = LabelElement
Input = InputElement
Button = ButtonElement
Select = SelectElement
DataList = DataListElement
OptGroup = OptionGroupElement
Option = OptionElement
Progress = ProgressElement
Meter = MeterElement
FieldSet = FieldSetElement
Legend = FieldSetLegendElement

# --- Interactive elements ---

class DetailsElement(OpenElement):
    tag = "details"

class SummaryElement(OpenElement):
    tag = "summary"
    render_mode = "inline"

class DialogElement(OpenElement):
    tag = "dialog"

Details = DetailsElement
Summary = SummaryElement
Dialog = DialogElement

# --- Scripting ---

class ScriptElement(OpenElement):
    tag = "script"

class NoScriptElement(OpenElement):
    tag = "noscript"

class TemplateElement(OpenElement):
    tag = "template"

class SlotElement(OpenElement):
    tag = "slot"

class CanvasElement(OpenElement):
    tag = "canvas"

Script = ScriptElement
NoScript = NoScriptElement
Template = TemplateElement
Slot = SlotElement
Canvas = CanvasElement

