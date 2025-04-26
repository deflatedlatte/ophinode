import json
import os.path
import pathlib
import collections
import collections.abc
from abc import ABC, abstractmethod
from typing import Any, Union, Iterable, Tuple, Callable

from .exceptions import *
from .constants import *
from .nodes.base import *
from .nodes.html import TextNode, HTML5Layout
from .rendering import BuildContext, RenderNode

class _StackDelimiter:
    pass

class Site:
    def __init__(
        self,
        options: Union[collections.abc.Mapping, None] = None,
        pages: Union[Iterable[Tuple[str, Any]], None] = None,
        processors: Union[
            Iterable[Tuple[str, Callable[["BuildContext"], None]]],
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
                self.add_page(path, page)

        self._preprocessors_before_site_preparation_stage = []
        self._postprocessors_after_site_preparation_stage = []
        self._preprocessors_before_page_build_preparation_stage = []
        self._postprocessors_after_page_build_preparation_stage = []
        self._preprocessors_before_page_build_stage = []
        self._postprocessors_after_page_build_stage = []
        self._preprocessors_before_page_expansion_preparation_stage = []
        self._postprocessors_after_page_expansion_preparation_stage = []
        self._preprocessors_before_page_expansion_stage = []
        self._postprocessors_after_page_expansion_stage = []
        self._preprocessors_before_page_rendering_stage = []
        self._postprocessors_after_page_rendering_stage = []
        self._preprocessors_before_site_finalization_stage = []
        self._postprocessors_after_site_finalization_stage = []
        if processors is not None:
            if not isinstance(processors, collections.abc.Iterable):
                raise TypeError("processors must be an iterable")
            for stage, processor in processors:
                self.add_processor(stage, processor)

    def update_options(
        self,
        options: collections.abc.Mapping,
        ignore_invalid_keys: bool = False
    ):
        if not isinstance(options, collections.abc.Mapping):
            raise TypeError("options must be a mapping")
        for k, v in options.items():
            if k == EXPORT_ROOT_PATH_OPTION_KEY:
                self.set_export_root_path(v)
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

    def set_export_root_path(self, export_root_path: str):
        if not isinstance(export_root_path, str):
            raise TypeError("export_root_path must be a str")
        self._options[EXPORT_ROOT_PATH_OPTION_KEY] = os.path.abspath(
            export_root_path
        )

    @property
    def export_root_path(self) -> str:
        return self._options.get(
            EXPORT_ROOT_PATH_OPTION_KEY,
            EXPORT_ROOT_PATH_OPTION_DEFAULT_VALUE
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

    def add_page(self, path: str, page: Any):
        if not isinstance(path, str):
            raise TypeError("path to a page must be a str")
        if path in self._pages_dict:
            raise ValueError("duplicate page path: " + path)
        self._pages_dict[path] = page
        self._pages.append((path, page))

    def add_processor(
        self,
        stage: str,
        processor: Callable[["BuildContext"], None]
    ):
        if not isinstance(stage, str):
            raise ValueError("processor stage must be a str")
        if not callable(processor):
            raise TypeError("processor must be a callable")
        if stage == "pre_prepare_site":
            self._preprocessors_before_site_preparation_stage.append(processor)
        elif stage == "post_prepare_site":
            self._postprocessors_after_site_preparation_stage.append(processor)
        elif stage == "pre_prepare_page_build":
            self._preprocessors_before_page_build_preparation_stage.append(processor)
        elif stage == "post_prepare_page_build":
            self._postprocessors_after_page_build_preparation_stage.append(processor)
        elif stage == "pre_build_pages":
            self._preprocessors_before_page_build_stage.append(processor)
        elif stage == "post_build_pages":
            self._postprocessors_after_page_build_stage.append(processor)
        elif stage == "pre_prepare_page_expansion":
            self._preprocessors_before_page_expansion_preparation_stage.append(processor)
        elif stage == "post_prepare_page_expansion":
            self._postprocessors_after_page_expansion_preparation_stage.append(processor)
        elif stage == "pre_expand_pages":
            self._preprocessors_before_page_expansion_stage.append(processor)
        elif stage == "post_expand_pages":
            self._postprocessors_after_page_expansion_stage.append(processor)
        elif stage == "pre_render_pages":
            self._preprocessors_before_page_rendering_stage.append(processor)
        elif stage == "post_render_pages":
            self._postprocessors_after_page_rendering_stage.append(processor)
        elif stage == "pre_finalize_site":
            self._preprocessors_before_site_finalization_stage.append(processor)
        elif stage == "post_finalize_site":
            self._postprocessors_after_site_finalization_stage.append(processor)
        else:
            raise ValueError("invalid processor stage: '{}'".format(stage))

    def add_preprocessor(
        self,
        stage: str,
        processor: Callable[["BuildContext"], None]
    ):
        if not isinstance(stage, str):
            raise ValueError("processor stage must be a str")
        if not callable(processor):
            raise TypeError("processor must be a callable")
        if stage == "prepare_site":
            self._preprocessors_before_site_preparation_stage.append(processor)
        elif stage == "prepare_page_build":
            self._preprocessors_before_page_build_preparation_stage.append(processor)
        elif stage == "build_pages":
            self._preprocessors_before_page_build_stage.append(processor)
        elif stage == "prepare_page_expansion":
            self._preprocessors_before_page_expansion_preparation_stage.append(processor)
        elif stage == "expand_pages":
            self._preprocessors_before_page_expansion_stage.append(processor)
        elif stage == "render_pages":
            self._preprocessors_before_page_rendering_stage.append(processor)
        elif stage == "finalize_site":
            self._preprocessors_before_site_finalization_stage.append(processor)
        else:
            raise ValueError("invalid build stage: '{}'".format(stage))

    def add_postprocessor(
        self,
        stage: str,
        processor: Callable[["BuildContext"], None]
    ):
        if not isinstance(stage, str):
            raise ValueError("processor stage must be a str")
        if not callable(processor):
            raise TypeError("processor must be a callable")
        if stage == "prepare_site":
            self._postprocessors_after_site_preparation_stage.append(processor)
        elif stage == "prepare_page_build":
            self._postprocessors_after_page_build_preparation_stage.append(processor)
        elif stage == "build_pages":
            self._postprocessors_after_page_build_stage.append(processor)
        elif stage == "prepare_page_expansion":
            self._postprocessors_after_page_expansion_preparation_stage.append(processor)
        elif stage == "expand_pages":
            self._postprocessors_after_page_expansion_stage.append(processor)
        elif stage == "render_pages":
            self._postprocessors_after_page_rendering_stage.append(processor)
        elif stage == "finalize_site":
            self._postprocessors_after_site_finalization_stage.append(processor)
        else:
            raise ValueError("invalid build stage: '{}'".format(stage))

    def create_build_context(self) -> BuildContext:
        return BuildContext(self)

    def prepare_site(self, context: BuildContext) -> BuildContext:
        for path, page in self._pages:
            context._page_data[path] = {}
            if hasattr(page, "prepare_site") and callable(page.prepare_site):
                context._current_page_path = path
                context._current_page = page
                page.prepare_site(context)
                context._current_page = None
                context._current_page_path = None
        return context

    def prepare_page_build(self, context: BuildContext) -> BuildContext:
        for path, page in self._pages:
            if hasattr(page, "prepare_page") and callable(page.prepare_page):
                context._current_page_path = path
                context._current_page = page
                page.prepare_page(context)
                context._current_page = None
                context._current_page_path = None
        return context

    def build_pages(self, context: BuildContext) -> BuildContext:
        for path, page in self._pages:
            context._current_page_path = path
            context._current_page = page
            context.built_pages[path] = self.build_page(path, page, context)
            context._current_page = None
            context._current_page_path = None
        return context

    def build_page(self, path: str, page: Any, context: BuildContext):
        layout = None
        if hasattr(page, "layout"):
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

    def prepare_page_expansion(self, context: BuildContext):
        for path, page in self._pages:
            node = context.built_pages[path]
            if isinstance(node, Preparable):
                context._current_page_path = path
                context._current_page = page
                node.prepare(context)
                context._current_page = None
                context._current_page_path = None

    def expand_pages(self, context: BuildContext):
        for path, page in self._pages:
            context._current_page_path = path
            context._current_page = page
            context.expanded_pages[path] = self.expand_nodes(
                context.built_pages[path], context
            )
            context._current_page = None
            context._current_page_path = None

    def expand_nodes(
        self,
        page_built: Iterable,
        context: BuildContext
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
            elif callable(node):
                r = node(context)
                stack.append(r)
            elif isinstance(node, collections.abc.Iterable):
                for n in reversed(node):
                    stack.append(n)
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

    def render_pages(self, context: BuildContext):
        for path, page in self._pages:
            context._current_page_path = path
            context._current_page = page
            context.rendered_pages[path] = self.render_page(path, page, context)
            context._current_page = None
            context._current_page_path = None

    def render_page(self, path: str, page: Any, context: BuildContext):
        root_node = context.expanded_pages[path]
        render_result = root_node.render(context)
        return render_result

    def finalize_site(self, context: BuildContext):
        for path, render_result in context.rendered_pages.items():
            page_path = path
            if path.endswith("/"):
                page_path += self.default_page_output_filename
            elif self.page_output_file_extension:
                fname = path[path.rfind("/")+1:]
                dot_index = fname.rfind(".")
                if (
                    (
                        dot_index == -1
                        or fname[dot_index+1:]
                           != self.page_output_file_extension
                    )
                    and
                    # the rightmost dot is not the first (or last) character
                    (
                        dot_index != 0
                        and (fname and dot_index != len(fname)-1)
                    )
                ):
                    page_path += "." + self.page_output_file_extension
            page_path = os.path.normpath(page_path)
            if page_path in context.exported_files:
                raise ExportPathCollisionError(
                    "attempted to export a page to '{}', but another file is "
                    "already exported to that path".format(page_path)
                )
            context.exported_files[page_path] = render_result

    def export_files(self, context: BuildContext):
        # Check if export_root_path has been set
        if not self.export_root_path:
            raise RootPathUndefinedError(
                "failed to export files because export_root_path is empty"
            )

        # Ensure export_root_path is a directory,
        # or if it does not exist, create one
        export_root_path = pathlib.Path(self.export_root_path)
        if not export_root_path.exists():
            if export_root_path.is_symlink():
                raise RootPathIsNotADirectoryError(
                    "failed to export files because export_root_path is a "
                    "broken symlink"
                )
            try:
                export_root_path.mkdir(parents=True)
            except NotADirectoryError as exc:
                raise RootPathIsNotADirectoryError(
                    "failed to export files because the parent of "
                    "export_root_path is not a directory, and thus "
                    "export_root_path cannot be a directory"
                ) from exc
        elif not export_root_path.is_dir():
            raise RootPathIsNotADirectoryError(
                "failed to export files because export_root_path is not a "
                "directory"
            )

        # Export files
        for path, file_content in context.exported_files.items():
            target_path = (
                pathlib.Path(self.export_root_path) / path.lstrip('/')
            )
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

    def build_site(self, context: Union[BuildContext, None] = None):
        if context is None:
            context = self.create_build_context()
        elif not isinstance(context, BuildContext):
            raise TypeError("context must be a BuildContext or None, not {}".format(context.__class__.__name__))
        elif context._site != self:
            raise ValueError("the context is not pointing to the site you are trying to build")

        for processor in self._preprocessors_before_site_preparation_stage:
            processor(context)
        self.prepare_site(context)
        for processor in self._postprocessors_after_site_preparation_stage:
            processor(context)

        for processor in self._preprocessors_before_page_build_preparation_stage:
            processor(context)
        self.prepare_page_build(context)
        for processor in self._postprocessors_after_page_build_preparation_stage:
            processor(context)

        for processor in self._preprocessors_before_page_build_stage:
            processor(context)
        self.build_pages(context)
        for processor in self._postprocessors_after_page_build_stage:
            processor(context)

        for processor in self._preprocessors_before_page_expansion_preparation_stage:
            processor(context)
        self.prepare_page_expansion(context)
        for processor in self._postprocessors_after_page_expansion_preparation_stage:
            processor(context)

        for processor in self._preprocessors_before_page_expansion_stage:
            processor(context)
        self.expand_pages(context)
        for processor in self._postprocessors_after_page_expansion_stage:
            processor(context)

        for processor in self._preprocessors_before_page_rendering_stage:
            processor(context)
        self.render_pages(context)
        for processor in self._postprocessors_after_page_rendering_stage:
            processor(context)

        for processor in self._preprocessors_before_site_finalization_stage:
            processor(context)
        self.finalize_site(context)
        for processor in self._postprocessors_after_site_finalization_stage:
            processor(context)

        if self.auto_export_files:
            self.export_files(context)
        return context

def render_page(page: Any, default_layout: Union[Layout, None] = None):
    options = {
        EXPORT_ROOT_PATH_OPTION_KEY: "/",
        AUTO_EXPORT_FILES_OPTION_KEY: False,
    }
    if default_layout is not None:
        options[DEFAULT_LAYOUT_OPTION_KEY] = default_layout
    site = Site(options, [("/", page)])
    context = site.build_site()
    return context.rendered_pages["/"]
