import sys
import json
import os.path
import pathlib
import multiprocessing
import collections
from typing import Any
if sys.version_info.major == 3 and sys.version_info.minor < 9:
    from typing import Iterable
else:
    from collections.abc import Iterable

from ophinode.exceptions.site import (
    RootPathUndefinedError,
    RootPathIsNotADirectoryError,
)
from ophinode.nodes.base import Expandable, Preparable, Layout
from ophinode.nodes.html import TextNode, HTML5Layout
from ophinode.rendering.render_node import RenderNode
from .build_contexts import (
    RootBuildContext,
    BuildContext,
    BuildPhase,
    BUILD_CONTEXT_CONFIG_KEYS,
)

class _StackDelimiter:
    pass

# Page related builders
def run_preprocessors_for_prepare_page_build(context: BuildContext) -> BuildContext:
    context.set_build_phase(BuildPhase.PRE_PREPARE_PAGE_BUILD)
    for processor in context._preprocessors_before_page_build_preparation_stage:
        processor(context)
    return context

def prepare_page_build(context: BuildContext) -> BuildContext:
    context.set_build_phase(BuildPhase.PREPARE_PAGE_BUILD)
    for page_def in context._page_group._pages:
        path, page = page_def.path, page_def.page
        if not isinstance(page, Preparable):
            continue
        context.set_current_page(path, page)
        page.prepare(context)
        context.unset_current_page()
    return context

def run_postprocessors_for_prepare_page_build(context: BuildContext) -> BuildContext:
    context.set_build_phase(BuildPhase.POST_PREPARE_PAGE_BUILD)
    for processor in context._postprocessors_after_page_build_preparation_stage:
        processor(context)
    return context

def run_preprocessors_for_build_pages(context: BuildContext) -> BuildContext:
    context.set_build_phase(BuildPhase.PRE_BUILD_PAGES)
    for processor in context._preprocessors_before_page_build_stage:
        processor(context)
    return context

def build_pages(context: BuildContext) -> BuildContext:
    context.set_build_phase(BuildPhase.BUILD_PAGES)
    for page_def in context._page_group._pages:
        path, page = page_def.path, page_def.page
        layout = resolve_layout(path, page, context)
        context.set_current_page(path, page)
        context.set_built_page(path, layout.build(page, context))
        context.unset_current_page()
    return context

def resolve_layout(path: str, page: Any, context: BuildContext):
    layout = None
    if hasattr(page, "layout"):
        layout = page.layout
        l_src = "layout property of page"
    if not layout:
        layout = context.get_config_value("default_layout")
        l_src = "default_layout config of renderer"
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

    return layout

def run_postprocessors_for_build_pages(context: BuildContext) -> BuildContext:
    context.set_build_phase(BuildPhase.POST_BUILD_PAGES)
    for processor in context._postprocessors_after_page_build_stage:
        processor(context)
    return context

def run_preprocessors_for_prepare_page_expansion(context: BuildContext) -> BuildContext:
    context.set_build_phase(BuildPhase.PRE_PREPARE_PAGE_EXPANSION)
    for processor in context._preprocessors_before_page_expansion_preparation_stage:
        processor(context)
    return context

def prepare_page_expansion(context: BuildContext):
    context.set_build_phase(BuildPhase.PREPARE_PAGE_EXPANSION)
    for page_def in context._page_group._pages:
        path, page = page_def.path, page_def.page
        node = context.get_built_page(path)
        if not isinstance(node, Preparable):
            continue
        context.set_current_page(path, page)
        node.prepare(context)
        context.unset_current_page()
    return context

def run_postprocessors_for_prepare_page_expansion(context: BuildContext) -> BuildContext:
    context.set_build_phase(BuildPhase.POST_PREPARE_PAGE_EXPANSION)
    for processor in context._postprocessors_after_page_expansion_preparation_stage:
        processor(context)
    return context

def run_preprocessors_for_expand_pages(context: BuildContext) -> BuildContext:
    context.set_build_phase(BuildPhase.PRE_EXPAND_PAGES)
    for processor in context._preprocessors_before_page_expansion_stage:
        processor(context)
    return context

def expand_pages(context: BuildContext):
    context.set_build_phase(BuildPhase.EXPAND_PAGES)
    for page_def in context._page_group._pages:
        path, page = page_def.path, page_def.page
        context.set_current_page(path, page)
        context.set_expanded_page(path, expand_page(
            context.get_built_page(path), context
        ))
        context.unset_current_page()

def expand_page(
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
        elif isinstance(node, Iterable):
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

def run_postprocessors_for_expand_pages(context: BuildContext) -> BuildContext:
    context.set_build_phase(BuildPhase.POST_EXPAND_PAGES)
    for processor in context._postprocessors_after_page_expansion_stage:
        processor(context)
    return context

def run_preprocessors_for_render_pages(context: BuildContext) -> BuildContext:
    context.set_build_phase(BuildPhase.PRE_RENDER_PAGES)
    for processor in context._preprocessors_before_page_rendering_stage:
        processor(context)
    return context

def render_pages(context: BuildContext):
    context.set_build_phase(BuildPhase.RENDER_PAGES)
    for page_def in context._page_group._pages:
        path, page = page_def.path, page_def.page
        context.set_current_page(path, page)
        context.set_rendered_page(path, render_page(path, page, context))
        context.unset_current_page()

def render_page(path: str, page: Any, context: BuildContext):
    root_node = context.get_expanded_page(path)
    render_result = root_node.render(context)
    return render_result

def run_postprocessors_for_render_pages(context: BuildContext) -> BuildContext:
    context.set_build_phase(BuildPhase.POST_RENDER_PAGES)
    for processor in context._postprocessors_after_page_rendering_stage:
        processor(context)
    return context

def run_preprocessors_for_export_pages(context: BuildContext) -> BuildContext:
    context.set_build_phase(BuildPhase.PRE_EXPORT_PAGES)
    for processor in context._preprocessors_before_page_exportation_stage:
        processor(context)
    return context

def export_pages(context: BuildContext):
    context.set_build_phase(BuildPhase.EXPORT_PAGES)
    for page_def in context._page_group._pages:
        path, page = page_def.path, page_def.page
        context.set_current_page(path, page)
        page.export(context, path)
        context.unset_current_page()

def run_postprocessors_for_export_pages(context: BuildContext) -> BuildContext:
    context.set_build_phase(BuildPhase.POST_EXPORT_PAGES)
    for processor in context._postprocessors_after_page_exportation_stage:
        processor(context)
    return context

def run_preprocessors_for_finalize_page_build(context: BuildContext) -> BuildContext:
    context.set_build_phase(BuildPhase.PRE_FINALIZE_PAGE_BUILD)
    for processor in context._preprocessors_before_page_build_finalization_stage:
        processor(context)
    return context

def finalize_page_build(context: BuildContext):
    context.set_build_phase(BuildPhase.FINALIZE_PAGE_BUILD)
    # Check if export_root_path has been set
    if not context.get_config_value("export_root_path"):
        raise RootPathUndefinedError(
            "failed to export files because export_root_path is empty"
        )

    # Ensure export_root_path is a directory,
    # or if it does not exist, create one
    export_root_path = pathlib.Path(context.get_config_value("export_root_path"))
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
    for path, file_content in context.get_exported_files().items():
        target_path = (
            pathlib.Path(context.get_config_value("export_root_path")) / path.lstrip('/')
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

def run_postprocessors_for_finalize_page_build(context: BuildContext) -> BuildContext:
    context.set_build_phase(BuildPhase.POST_FINALIZE_PAGE_BUILD)
    for processor in context._postprocessors_after_page_build_finalization_stage:
        processor(context)
    return context

# Site related builders
def run_preprocessors_for_prepare_site_build(context: RootBuildContext) -> RootBuildContext:
    context.set_build_phase(BuildPhase.PRE_PREPARE_SITE_BUILD)
    for processor in context._preprocessors_before_site_build_preparation_stage:
        processor(context)
    return context

def prepare_site_build(context: RootBuildContext) -> RootBuildContext:
    context.set_build_phase(BuildPhase.PREPARE_SITE_BUILD)
    for page_group in context._page_groups.values():
        config = {}
        # TODO: respect configs of individual page groups
        for k in BUILD_CONTEXT_CONFIG_KEYS:
            config[k] = context.get_config_value(k)
        context.create_subcontext(page_group, config)
    return context

def run_postprocessors_for_prepare_site_build(context: RootBuildContext) -> RootBuildContext:
    context.set_build_phase(BuildPhase.POST_PREPARE_SITE_BUILD)
    for processor in context._postprocessors_after_site_build_preparation_stage:
        processor(context)
    return context

def run_preprocessors_for_finalize_site_build(context: RootBuildContext) -> RootBuildContext:
    context.set_build_phase(BuildPhase.PRE_FINALIZE_SITE_BUILD)
    for processor in context._preprocessors_before_site_build_finalization_stage:
        processor(context)
    return context

def finalize_site_build(context: RootBuildContext):
    context.set_build_phase(BuildPhase.FINALIZE_SITE_BUILD)

def run_postprocessors_for_finalize_site_build(context: RootBuildContext) -> RootBuildContext:
    context.set_build_phase(BuildPhase.POST_FINALIZE_SITE_BUILD)
    for processor in context._postprocessors_after_site_build_finalization_stage:
        processor(context)
    return context

def build_and_render_pages(context: BuildContext):
    run_preprocessors_for_prepare_page_build(context)
    prepare_page_build(context)
    run_postprocessors_for_prepare_page_build(context)

    run_preprocessors_for_build_pages(context)
    build_pages(context)
    run_postprocessors_for_build_pages(context)

    run_preprocessors_for_prepare_page_expansion(context)
    prepare_page_expansion(context)
    run_postprocessors_for_prepare_page_expansion(context)

    run_preprocessors_for_expand_pages(context)
    expand_pages(context)
    run_postprocessors_for_expand_pages(context)

    run_preprocessors_for_render_pages(context)
    render_pages(context)
    run_postprocessors_for_render_pages(context)

    run_preprocessors_for_export_pages(context)
    export_pages(context)
    run_postprocessors_for_export_pages(context)

    run_preprocessors_for_finalize_page_build(context)
    finalize_page_build(context)
    run_postprocessors_for_finalize_page_build(context)

    return {}

def build_and_render_page_groups(context: RootBuildContext):
    build_strategy = context.get_config_value("build_strategy")
    if build_strategy == "sync":
        for subcontext in context.subcontexts:
            result = build_and_render_pages(subcontext)
    elif build_strategy == "parallel":
        pool = multiprocessing.Pool(
            processes=context.get_config_value("parallel_build_workers")
        )
        for result in pool.imap_unordered(
            build_and_render_pages,
            context.subcontexts,
            context.get_config_value("parallel_build_chunksize")
        ):
            pass
        pool.close()
        pool.join()
    else:
        raise ValueError("unknown build strategy: {}".format(build_strategy))

    return context
