__all__ = [
    "HtmlElement",
    "HeadElement",
    "TitleElement",
    "BaseElement",
    "LinkElement",
    "MetaElement",
    "StyleElement",
    "BodyElement",
    "ArticleElement",
    "SectionElement",
    "NavigationElement",
    "AsideElement",
    "HeadingLevel1Element",
    "HeadingLevel2Element",
    "HeadingLevel3Element",
    "HeadingLevel4Element",
    "HeadingLevel5Element",
    "HeadingLevel6Element",
    "HeadingGroupElement",
    "HeaderElement",
    "FooterElement",
    "AddressElement",
    "ParagraphElement",
    "HorizontalRuleElement",
    "PreformattedTextElement",
    "BlockQuotationElement",
    "OrderedListElement",
    "UnorderedListElement",
    "MenuElement",
    "ListItemElement",
    "DescriptionListElement",
    "DescriptionTermElement",
    "DescriptionDetailsElement",
    "FigureElement",
    "FigureCaptionElement",
    "MainElement",
    "SearchElement",
    "DivisionElement",
    "AnchorElement",
    "EmphasisElement",
    "StrongImportanceElement",
    "SmallPrintElement",
    "StrikethroughElement",
    "CitationElement",
    "QuotationElement",
    "DefinitionElement",
    "AbbreviationElement",
    "RubyAnnotationElement",
    "RubyTextElement",
    "RubyParenthesesElement",
    "DataElement",
    "TimeElement",
    "CodeElement",
    "VariableElement",
    "SampleElement",
    "KeyboardInputElement",
    "SubscriptElement",
    "SuperscriptElement",
    "ItalicTextElement",
    "BoldTextElement",
    "UnarticulatedAnnotationElement",
    "MarkedTextElement",
    "BidirectionalIsolateElement",
    "BidirectionalOverrideElement",
    "SpanElement",
    "LineBreakElement",
    "LineBreakOpportunityElement",
    "InsertionElement",
    "DeletionElement",
    "PictureElement",
    "SourceElement",
    "ImageElement",
    "InlineFrameElement",
    "EmbeddedContentElement",
    "ExternalObjectElement",
    "VideoElement",
    "AudioElement",
    "TextTrackElement",
    "ImageMapElement",
    "ImageMapAreaElement",
    "TableElement",
    "TableCaptionElement",
    "TableColumnGroupElement",
    "TableColumnElement",
    "TableBodyElement",
    "TableHeadElement",
    "TableFootElement",
    "TableRowElement",
    "TableDataCellElement",
    "TableHeaderCellElement",
    "FormElement",
    "LabelElement",
    "InputElement",
    "ButtonElement",
    "SelectElement",
    "DataListElement",
    "OptionGroupElement",
    "OptionElement",
    "TextAreaElement",
    "OutputElement",
    "ProgressElement",
    "MeterElement",
    "FieldSetElement",
    "FieldSetLegendElement",
    "DetailsElement",
    "SummaryElement",
    "DialogElement",
    "ScriptElement",
    "NoScriptElement",
    "TemplateElement",
    "SlotElement",
    "CanvasElement",
]

from ..core import OpenElement, ClosedElement

# --- The document element ---

class HtmlElement(OpenElement):
    tag = "html"

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

    def __init__(self, *args, escape_tag_delimiters = None, **kwargs):
        if escape_tag_delimiters is None:
            # stylesheets might contain angle brackets, so it is better to
            # disable tag delimiter escaping by default
            escape_tag_delimiters = False
        super().__init__(
            *args,
            escape_tag_delimiters=escape_tag_delimiters,
            **kwargs
        )

    def expand(self, context: "ophinode.site.BuildContext"):
        expansion = []
        for c in self._children:
            if isinstance(c, str):
                # Stylesheets might contain "</style", so it must be escaped
                content = c.replace("</script", "\\3C/script")
                node = TextNode(content)
                if self._escape_ampersands is not None:
                    node.escape_ampersands(self._escape_ampersands)
                if self._escape_tag_delimiters is not None:
                    node.escape_tag_delimiters(self._escape_tag_delimiters)
                expansion.append(node)
            else:
                expansion.append(c)
        return expansion

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

# --- Edits ---

class InsertionElement(OpenElement):
    tag = "ins"

class DeletionElement(OpenElement):
    tag = "del"
    render_mode = "inline"

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

# --- Interactive elements ---

class DetailsElement(OpenElement):
    tag = "details"

class SummaryElement(OpenElement):
    tag = "summary"
    render_mode = "inline"

class DialogElement(OpenElement):
    tag = "dialog"

# --- Scripting ---

class ScriptElement(OpenElement):
    tag = "script"

    def __init__(self, *args, escape_tag_delimiters = None, **kwargs):
        if escape_tag_delimiters is None:
            # javascript code might contain angle brackets,
            # so it is better to disable tag delimiter escaping by default
            escape_tag_delimiters = False
        super().__init__(
            *args,
            escape_tag_delimiters=escape_tag_delimiters,
            **kwargs
        )

    def expand(self, context: "ophinode.site.BuildContext"):
        expansion = []
        for c in self._children:
            if isinstance(c, str):
                # Due to restrictions for contents of script elements, some
                # sequences of characters must be replaced before constructing
                # a script element.
                # 
                # Unfortunately, correctly replacing such character sequences
                # require a full lexical analysis on the script content, but
                # ophinode is currently incapable of doing so.
                #
                # However, the sequences are expected to be rarely seen
                # outside literals, so replacements are done nonetheless.
                #
                # This behavior might change in the later versions of ophinode
                # when it starts to better support inline scripting.
                #
                # Read https://html.spec.whatwg.org/multipage/scripting.html#restrictions-for-contents-of-script-elements
                # for more information.
                #
                content = c.replace(
                    "<!--", "\\x3C!--"
                ).replace(
                    "<script", "\\x3Cscript"
                ).replace(
                    "</script", "\\x3C/script"
                )
                node = TextNode(content)
                if self._escape_ampersands is not None:
                    node.escape_ampersands(self._escape_ampersands)
                if self._escape_tag_delimiters is not None:
                    node.escape_tag_delimiters(self._escape_tag_delimiters)
                expansion.append(node)
            else:
                expansion.append(c)
        return expansion

class NoScriptElement(OpenElement):
    tag = "noscript"

class TemplateElement(OpenElement):
    tag = "template"

class SlotElement(OpenElement):
    tag = "slot"

class CanvasElement(OpenElement):
    tag = "canvas"

