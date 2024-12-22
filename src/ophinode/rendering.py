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
        while stk:
            render_node, revisited = stk.pop()
            v, c = render_node._value, render_node._children
            if isinstance(v, OpenRenderable):
                if revisited:
                    depth -= 2
                    result.append(" "*depth + v.render_end(context))
                else:
                    result.append(" "*depth + v.render_start(context))
                    stk.append((render_node, True))
                    depth += 2
                    if c:
                        for i in reversed(c):
                            stk.append((i, False))
            elif isinstance(v, ClosedRenderable):
                if revisited:
                    depth -= 2
                else:
                    result.append(" "*depth + v.render(context))
                    if c:
                        stk.append((render_node, True))
                        depth += 2
                        for i in reversed(c):
                            stk.append((i, False))
            elif c:
                for i in reversed(c):
                    stk.append((i, False))

        return "\n".join(result)

