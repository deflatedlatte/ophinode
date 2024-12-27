import os.path
import pathlib
import collections
import collections.abc
from abc import ABC, abstractmethod
from typing import Union, Iterable, Tuple, Callable

from .exceptions import *
from .constants import *
from .nodes.base import *
from .nodes.html import TextNode, HTML5Layout
from .rendering import RenderContext, RenderNode

class _StackDelimiter:
    pass

class Site:
    def __init__(
        self,
        options: Union[dict, None] = None,
        pages: Union[Iterable[Tuple[str, "Page"]], None] = None,
        preprocessors: Union[
            Iterable[Callable[["RenderContext"], None]],
            None
        ] = None,
        postprocessors: Union[
            Iterable[Callable[["RenderContext"], None]],
            None
        ] = None,
    ):
        self._options = {}
        if options is not None:
            self.update_options(options)

        self._pages_dict = {}
        self._pages = []
        if pages is not None:
            if not isinstance(pages, collections.abc.Iterable):
                raise TypeError("pages must be an iterable")
            for path, page in pages:
                if not isinstance(path, str):
                    raise ValueError("path to a page must be a str")
                self._pages_dict[path] = page
                self._pages.append((path, page))

        self._preprocessors = []
        if preprocessors is not None:
            if not isinstance(preprocessors, collections.abc.Iterable):
                raise TypeError("preprocessors must be an iterable")
            for preprocessor in preprocessors:
                self.add_preprocessor(preprocessor)

        self._postprocessors = []
        if postprocessors is not None:
            if not isinstance(postprocessors, collections.abc.Iterable):
                raise TypeError("postprocessors must be an iterable")
            for postprocessor in postprocessors:
                self.add_postprocessor(postprocessor)

    def update_options(
        self,
        options: dict,
        ignore_invalid_keys: bool = False
    ):
        if not isinstance(options, dict):
            raise TypeError("options must be a dict")
        for k, v in options.items():
            if k == ROOT_PATH_OPTION_KEY:
                self.set_root_path(v)
            elif k == DEFAULT_LAYOUT_OPTION_KEY:
                self.set_default_layout(v)
            elif not ignore_invalid_keys:
                raise ValueError("unknown option key: {}".format(k))

    def set_root_path(self, root_path: str):
        if not isinstance(root_path, str):
            raise TypeError("root_path must be a str")
        self._options[ROOT_PATH_OPTION_KEY] = os.path.abspath(root_path)

    @property
    def root_path(self) -> str:
        return self._options.get(
            ROOT_PATH_OPTION_KEY,
            ROOT_PATH_OPTION_DEFAULT_VALUE
        )

    def set_default_layout(self, default_layout: Layout):
        if not isinstance(default_layout, Layout):
            raise TypeError("default_layout must be a Layout")
        self._options[DEFAULT_LAYOUT_OPTION_KEY] = default_layout

    @property
    def default_layout(self) -> Union[Layout, None]:
        return self._options.get(
            DEFAULT_LAYOUT_OPTION_KEY,
            DEFAULT_LAYOUT_OPTION_DEFAULT_VALUE
        )

    def add_preprocessor(
        self,
        preprocessor: Callable[["RenderContext"], None]
    ):
        if not callable(preprocessor):
            raise TypeError("preprocessor must be a callable")
        self._preprocessors.append(preprocessor)

    def add_postprocessor(
        self,
        postprocessor: Callable[["RenderContext"], None]
    ):
        if not callable(postprocessor):
            raise TypeError("postprocessor must be a callable")
        self._postprocessors.append(postprocessor)

    def _prepare_site(self) -> RenderContext:
        # Check if root_path has been set
        if not self.root_path:
            raise RootPathUndefinedError(
                "failed to prepare site because the root_path is empty"
            )

        # Ensure root_path is a directory, or if it does not exist, create one
        root_path = pathlib.Path(self.root_path)
        if not root_path.exists():
            if root_path.is_symlink():
                raise RootPathIsNotADirectoryError(
                    "failed to prepare site because the root_path is a "
                    "broken symlink"
                )
            try:
                root_path.mkdir(parents=True)
            except NotADirectoryError as exc:
                raise RootPathIsNotADirectoryError(
                    "failed to prepare site because parents of root_path is "
                    "not a directory"
                ) from exc
        elif not root_path.is_dir():
            raise RootPathIsNotADirectoryError(
                "failed to prepare site because root_path is not a directory"
            )

        # Run site preparation tasks
        for preprocessor in self._preprocessors:
            preprocessor(context)

        return RenderContext(self)

    def _build_nodes(self, page: Page, context: RenderContext) -> Iterable:
        if isinstance(page, Page):
            layout = page.layout
            l_src = "layout property of page"
        elif "default_layout" in self._options:
            layout = self._options["default_layout"]
            l_src = "default_layout option of renderer"
        else:
            layout = HTML5Layout()
            l_src = "fallback layout (HTML5Layout)"

        if callable(layout):
            layout = layout(context)

        if not isinstance(layout, Layout):
            raise ValueError(
                "resolved layout (from {}) is not a Layout instance".format(
                    l_src
                )
            )

        return layout.build(page, context)

    def _prepare_nodes(self, page_built: Iterable, context: RenderContext):
        for node in page_built:
            if isinstance(node, Preparable):
                node.prepare(context)

    def _expand_nodes(
        self,
        page_built: Iterable,
        context: RenderContext
    ) -> RenderNode:
        root_node = RenderNode(None)
        curr = root_node

        stack = collections.deque()
        for node in reversed(page_built):
            stack.append(node)

        while stack:
            node = stack.pop()
            if isinstance(node, _StackDelimiter):
                curr = curr._parent
            elif isinstance(node, str):
                render_node = RenderNode(TextNode(node))
                render_node._parent = curr
                curr._children.append(render_node)
            elif isinstance(node, list) or isinstance(node, tuple):
                for n in reversed(node):
                    stack.append(n)
            elif callable(node):
                r = node(context)
                stack.append(r)
            elif isinstance(node, Expandable):
                r = node.expand(context)
                stack.append(_StackDelimiter())
                next_render_node = RenderNode(node)
                next_render_node._parent = curr
                curr._children.append(next_render_node)
                curr = next_render_node
                stack.append(r)
            else:
                next_render_node = RenderNode(node)
                next_render_node._parent = curr
                curr._children.append(next_render_node)

        return root_node

    def _finalize_site(self, context: RenderContext):
        # Run postprocessors
        for postprocessor in self._postprocessors:
            postprocessor(context)

        # Render pages
        for path, _ in self._pages:
            root_node = context.page_nodes[path]
            render_result = root_node.render(context)
            target_path = pathlib.Path(self.root_path) / path.lstrip('/')
            if path.endswith('/'):
                target_path /= "index.html"
            target_directory = target_path.parent
            if not target_directory.exists():
                target_directory.mkdir(parents=True)
            with target_path.open(mode="w", encoding="utf-8") as f:
                f.write(render_result)

    def build(self):
        context = self._prepare_site()

        # Build pages
        pages_built = {}
        for path, page in self._pages:
            context._current_page_path = path
            context._current_page = page
            page_built = self._build_nodes(page, context)
            pages_built[path] = page_built
            context._current_page_path = None
            context._current_page = None

        # Prepare pages
        for path, _ in self._pages:
            context._current_page_path = path
            context._current_page = page
            self._prepare_nodes(pages_built[path], context)
            context._current_page_path = None
            context._current_page = None

        # Expand pages
        for path, _ in self._pages:
            context._current_page_path = path
            context._current_page = page
            root_node = self._expand_nodes(pages_built[path], context)
            context._page_nodes[path] = root_node
            context._current_page_path = None
            context._current_page = None

        self._finalize_site(context)

