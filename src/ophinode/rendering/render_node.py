import collections
from typing import Union

from ophinode.nodes.base import *

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

    def render(self, context: "ophinode.site.BuildContext"):
        result = []
        depth = 0

        render_stk = collections.deque()
        current_render = []

        renderables_stk = collections.deque()
        renderables_stk.append((self, False))

        no_auto_newline_count = 0
        no_auto_indent_count = 0
        auto_indent_string_stk = collections.deque()
        auto_indent_string_stk.append("  ")

        first_child = True
        auto_newline_blocked = False
        auto_indent_string = auto_indent_string_stk[-1]
        while renderables_stk:
            render_node, revisited = renderables_stk.pop()
            v, c = render_node._value, render_node._children
            if isinstance(v, OpenRenderable):
                if revisited:
                    # flush the render result of children
                    children_content = "".join(current_render)
                    if (
                        children_content
                        and no_auto_newline_count == 0
                        and v.pad_newline_after_opening
                    ):
                        if no_auto_indent_count == 0:
                            prefix = "\n" + auto_indent_string*depth
                        else:
                            prefix = "\n"
                        children_content = prefix + children_content
                    depth -= 1
                    current_render = render_stk.pop()
                    current_render.append(children_content)

                    # render closing
                    text_content = v.render_end(context)
                    if (
                        text_content
                        and no_auto_newline_count == 0
                        and v.pad_newline_before_closing
                        and children_content
                    ):
                        text_content = "\n" + text_content
                    if not v.auto_newline_for_children:
                        no_auto_newline_count -= 1
                    if not v.auto_indent_for_children:
                        no_auto_indent_count -= 1
                    if no_auto_indent_count == 0 and text_content:
                        prefix = "\n" + auto_indent_string*depth
                        text_content = prefix.join(text_content.split("\n"))
                    current_render.append(text_content)
                    first_child = False
                    if v.prevent_auto_newline_after_me:
                        auto_newline_blocked = True
                    else:
                        auto_newline_blocked = False
                    auto_indent_string_stk.pop()
                    auto_indent_string = auto_indent_string_stk[-1]
                else:
                    # render opening
                    text_content = v.render_start(context)
                    if (
                        text_content
                        and not first_child
                        and no_auto_newline_count == 0
                        and not v.prevent_auto_newline_before_me
                        and not auto_newline_blocked
                    ):
                        text_content = "\n" + text_content
                    if no_auto_indent_count == 0 and text_content:
                        prefix = "\n" + auto_indent_string*depth
                        text_content = prefix.join(text_content.split("\n"))
                    current_render.append(text_content)
                    render_stk.append(current_render)
                    current_render = []
                    if not v.auto_newline_for_children:
                        no_auto_newline_count += 1
                    if not v.auto_indent_for_children:
                        no_auto_indent_count += 1
                    renderables_stk.append((render_node, True))
                    depth += 1
                    first_child = True
                    auto_newline_blocked = False
                    auto_indent_string = v.auto_indent_string
                    auto_indent_string_stk.append(auto_indent_string)
            elif isinstance(v, ClosedRenderable):
                text_content = v.render(context)
                if (
                    text_content
                    and not first_child
                    and no_auto_newline_count == 0
                    and not v.prevent_auto_newline_before_me
                    and not auto_newline_blocked
                ):
                    text_content = "\n" + text_content
                if no_auto_indent_count == 0 and text_content:
                    prefix = "\n" + auto_indent_string*depth
                    text_content = prefix.join(text_content.split("\n"))
                current_render.append(text_content)
                first_child = False
                if v.prevent_auto_newline_after_me:
                    auto_newline_blocked = True
                else:
                    auto_newline_blocked = False
            else:
                auto_newline_blocked = False
            if not revisited and c:
                for i in reversed(c):
                    renderables_stk.append((i, False))
        result.append("".join(current_render))
        return "".join(result)

