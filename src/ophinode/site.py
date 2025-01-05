import json
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
        pages: Union[Iterable[Tuple[str, Page]], None] = None,
        processors: Union[
            Iterable[Tuple[str, Callable[["RenderContext"], None]]],
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

        self._preprocessors_for_site_build = []
        self._postprocessors_for_site_build = []
        self._preprocessors_for_page_build_stage = []
        self._postprocessors_for_page_build_stage = []
        self._preprocessors_for_page_preparation_stage = []
        self._postprocessors_for_page_preparation_stage = []
        self._preprocessors_for_page_expansion_stage = []
        self._postprocessors_for_page_expansion_stage = []
        self._preprocessors_for_page_rendering_stage = []
        self._postprocessors_for_page_rendering_stage = []
        if processors is not None:
            if not isinstance(processors, collections.abc.Iterable):
                raise TypeError("processors must be an iterable")
            for stage, processor in processors:
                self.add_processor(stage, processor)

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
            elif k == DEFAULT_PAGE_OUTPUT_FILENAME_OPTION_KEY:
                self.set_default_page_output_filename(v)
            elif k == PAGE_OUTPUT_FILE_EXTENSION_OPTION_KEY:
                self.set_page_output_file_extension(v)
            elif k == AUTO_EXPORT_FILES_OPTION_KEY:
                self.set_auto_export_files(v)
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

    def set_default_page_output_filename(
        self,
        default_page_output_filename: str
    ):
        if not isinstance(default_page_output_filename, str):
            raise TypeError("default_page_output_filename must be a str")
        self._options[
            DEFAULT_PAGE_OUTPUT_FILENAME_OPTION_KEY
        ] = default_page_output_filename

    @property
    def default_page_output_filename(self) -> str:
        return self._options.get(
            DEFAULT_PAGE_OUTPUT_FILENAME_OPTION_KEY,
            DEFAULT_PAGE_OUTPUT_FILENAME_OPTION_DEFAULT_VALUE
        )

    def set_page_output_file_extension(
        self,
        page_output_file_extension: str
    ):
        if not isinstance(page_output_file_extension, str):
            raise TypeError("page_output_file_extension must be a str")
        self._options[
            PAGE_OUTPUT_FILE_EXTENSION_OPTION_KEY
        ] = page_output_file_extension

    @property
    def page_output_file_extension(self) -> str:
        return self._options.get(
            PAGE_OUTPUT_FILE_EXTENSION_OPTION_KEY,
            PAGE_OUTPUT_FILE_EXTENSION_OPTION_DEFAULT_VALUE
        )

    def set_auto_export_files(self, auto_export_files: bool):
        self._options[AUTO_EXPORT_FILES_OPTION_KEY] = bool(auto_export_files)

    @property
    def auto_export_files(self) -> bool:
        return self._options.get(
            AUTO_EXPORT_FILES_OPTION_KEY,
            AUTO_EXPORT_FILES_OPTION_DEFAULT_VALUE
        )

    def add_processor(
        self,
        stage: str,
        processor: Callable[["RenderContext"], None]
    ):
        if not isinstance(stage, str):
            raise ValueError("processor stage must be a str")
        if not callable(preprocessor):
            raise TypeError("processor must be a callable")
        if stage == "pre_site_build":
            self._preprocessors_for_site_build.append(processor)
        elif stage == "post_site_build":
            self._postprocessors_for_site_build.append(processor)
        elif stage == "pre_page_build":
            self._preprocessors_for_page_build_stage.append(processor)
        elif stage == "post_page_build":
            self._postprocessors_for_page_build_stage.append(processor)
        elif stage == "pre_page_preparation":
            self._preprocessors_for_page_preparation_stage.append(processor)
        elif stage == "post_page_preparation":
            self._postprocessors_for_page_preparation_stage.append(processor)
        elif stage == "pre_page_expansion":
            self._preprocessors_for_page_expansion_stage.append(processor)
        elif stage == "post_page_expansion":
            self._postprocessors_for_page_expansion_stage.append(processor)
        elif stage == "pre_page_rendering":
            self._preprocessors_for_page_rendering_stage.append(processor)
        elif stage == "post_page_rendering":
            self._postprocessors_for_page_rendering_stage.append(processor)
        else:
            raise ValueError("invalid rendering stage: '{}'".format(stage))

    def _prepare_site(self) -> RenderContext:
        context = RenderContext(self)
        for processor in self._preprocessors_for_site_build:
            processor(context)
        return context

    def _build_nodes(self, page: Page, context: RenderContext) -> Iterable:
        layout = None
        if isinstance(page, Page):
            layout = page.layout
            l_src = "layout property of page"
        if not layout:
            layout = self.default_layout
            l_src = "default_layout option of renderer"
        if not layout:
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

    def _build_page(self, path, page, context):
        context._current_page_path = path
        context._current_page = page
        context.built_pages[path] = self._build_nodes(page, context)
        context._current_page = None
        context._current_page_path = None

    def _build_pages(self, context):
        for processor in self._preprocessors_for_page_build_stage:
            processor(context)
        for path, page in self._pages:
            self._build_page(path, page, context)
        for processor in self._postprocessors_for_page_build_stage:
            processor(context)

    def _prepare_nodes(self, page_built: Iterable, context: RenderContext):
        for node in page_built:
            if isinstance(node, Preparable):
                node.prepare(context)

    def _prepare_page(self, path: str, page: Page, context: RenderContext):
        context._current_page_path = path
        context._current_page = page
        self._prepare_nodes(context.built_pages[path], context)
        context._current_page = None
        context._current_page_path = None

    def _prepare_pages(self, context: RenderContext):
        for processor in self._preprocessors_for_page_preparation_stage:
            processor(context)
        for path, page in self._pages:
            self._prepare_page(path, page, context)
        for processor in self._postprocessors_for_page_preparation_stage:
            processor(context)

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

    def _expand_page(self, path: str, page: Page, context: RenderContext):
        context._current_page_path = path
        context._current_page = page
        root_node = self._expand_nodes(context.built_pages[path], context)
        context.expanded_pages[path] = root_node
        context._current_page = None
        context._current_page_path = None

    def _expand_pages(self, context: RenderContext):
        for processor in self._preprocessors_for_page_expansion_stage:
            processor(context)
        for path, page in self._pages:
            self._expand_page(path, page, context)
        for processor in self._postprocessors_for_page_expansion_stage:
            processor(context)

    def _render_page(self, path: str, page: Page, context: RenderContext):
        context._current_page_path = path
        context._current_page = page
        root_node = context.expanded_pages[path]
        render_result = root_node.render(context)
        context.rendered_pages[path] = render_result
        context._current_page = None
        context._current_page_path = None

    def _render_pages(self, context: RenderContext):
        for processor in self._preprocessors_for_page_rendering_stage:
            processor(context)
        for path, page in self._pages:
            self._render_page(path, page, context)
        for processor in self._postprocessors_for_page_rendering_stage:
            processor(context)

    def _finalize_site(self, context: RenderContext):
        for path, render_result in context.rendered_pages.items():
            page_path = path
            if path.endswith("/"):
                page_path += self.default_page_output_filename
            elif not path.endswith(self.page_output_file_extension):
                page_path += "/" + self.default_page_output_filename
            if page_path in context.exported_files:
                raise ExportPathCollisionError(
                    "attempted to export a page to '{}', but another file is "
                    "already exported to that path".format(page_path)
                )
            context.exported_files[page_path] = render_result

        for processor in self._postprocessors_for_site_build:
            processor(context)

    def _export_files(self, context: RenderContext):
        # Check if root_path has been set
        if not self.root_path:
            raise RootPathUndefinedError(
                "failed to export files because root_path is empty"
            )

        # Ensure root_path is a directory, or if it does not exist, create one
        root_path = pathlib.Path(self.root_path)
        if not root_path.exists():
            if root_path.is_symlink():
                raise RootPathIsNotADirectoryError(
                    "failed to export files because root_path is a broken"
                    "symlink"
                )
            try:
                root_path.mkdir(parents=True)
            except NotADirectoryError as exc:
                raise RootPathIsNotADirectoryError(
                    "failed to export files because the parent of root_path "
                    "is not a directory, and thus root_path cannot be a "
                    "directory"
                ) from exc
        elif not root_path.is_dir():
            raise RootPathIsNotADirectoryError(
                "failed to export files because root_path is not a directory"
            )

        # Export files
        for path, file_content in context.exported_files.items():
            target_path = pathlib.Path(self.root_path) / path.lstrip('/')
            target_directory = target_path.parent
            if not target_directory.exists():
                target_directory.mkdir(parents=True)
            if isinstance(file_content, (bytes, bytearray)):
                with target_path.open(mode="wb") as f:
                    f.write(file_content)
            elif isinstance(file_content, str):
                with target_path.open(mode="w", encoding="utf-8") as f:
                    f.write(file_content)
            else:
                with target_path.open(mode="w", encoding="utf-8") as f:
                    json.dump(file_content, f, indent=2)

    def build_site(self):
        context = self._prepare_site()
        self._build_pages(context)
        self._prepare_pages(context)
        self._expand_pages(context)
        self._render_pages(context)
        self._finalize_site(context)
        if self.auto_export_files:
            self._export_files(context)
        return context

