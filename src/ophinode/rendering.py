import collections
from typing import Union

from .nodes.base import *

class RenderContext:
    def __init__(self, site: "ophinode.site.Site"):
        self._site = site
        self._current_page = None
        self._current_page_path = None
        self._data = {}
        self._page_nodes = {}

    @property
    def site(self):
        return self._site

    @property
    def current_page(self):
        return self._current_page

    @property
    def current_page_path(self):
        return self._current_page_path

    @property
    def data(self):
        return self._data

    @property
    def page_nodes(self):
        return self._page_nodes

class RenderNode:
    def __init__(self, value: Union[OpenRenderable, ClosedRenderable, None]):
        self._value = value
        self._children = []
        self._parent = None

    @property
    def value(self):
        return self._value

    @property
    def children(self):
        return self._children

    @property
    def parent(self):
        return self._parent

    def render(self, context: RenderContext):
        result = []
        depth = 0
        stk = collections.deque()
        stk.append((self, False))
        no_auto_newline_count = 0
        total_text_content_length = 0
        text_content_length_stk = collections.deque()
        while stk:
            render_node, revisited = stk.pop()
            v, c = render_node._value, render_node._children
            if isinstance(v, OpenRenderable):
                if revisited:
                    depth -= 1
                    if no_auto_newline_count > 0:
                        text_content = v.render_end(context)
                    if (
                        text_content_length_stk
                        and text_content_length_stk[-1]
                            == total_text_content_length
                    ):
                        text_content = v.render_end(context) + "\n"
                    else:
                        text_content = "  "*depth+v.render_end(context)+"\n"
                    result.append(text_content)
                    total_text_content_length += len(text_content)
                    text_content_length_stk.pop()
                    if not v.auto_newline:
                        no_auto_newline_count -= 1
                        if no_auto_newline_count == 0:
                            result.append("\n")
                            total_text_content_length += 1
                else:
                    if no_auto_newline_count > 0:
                        text_content = v.render_start(context)
                    elif (
                        text_content_length_stk
                        and text_content_length_stk[-1]
                            == total_text_content_length
                    ):
                        text_content = "\n"+"  "*depth+v.render_start(context)
                    else:
                        text_content = "  "*depth+v.render_start(context)
                    result.append(text_content)
                    total_text_content_length += len(text_content)
                    text_content_length_stk.append(total_text_content_length)
                    if not v.auto_newline:
                        no_auto_newline_count += 1
                    stk.append((render_node, True))
                    depth += 1
                    if c:
                        for i in reversed(c):
                            stk.append((i, False))
            elif isinstance(v, ClosedRenderable):
                if revisited:
                    depth -= 1
                else:
                    if no_auto_newline_count > 0:
                        text_content = v.render(context)
                    elif (
                        text_content_length_stk
                        and text_content_length_stk[-1]
                            == total_text_content_length
                    ):
                        text_content = "\n"+"  "*depth+v.render(context)+"\n"
                    else:
                        text_content = "  "*depth+v.render(context)+"\n"
                    result.append(text_content)
                    total_text_content_length += len(text_content)
                    if c:
                        stk.append((render_node, True))
                        depth += 1
                        for i in reversed(c):
                            stk.append((i, False))
            elif c:
                for i in reversed(c):
                    stk.append((i, False))

        return "".join(result)

