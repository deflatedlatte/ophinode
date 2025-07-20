import sys
if sys.version_info.major == 3 and sys.version_info.minor < 9:
    from typing import Callable
else:
    from collections.abc import Callable

class PageGroup:
    def __init__(self, name):
        self._name = name
        self._config = {}
        self._pages_dict = {}
        self._pages = []
        self._dependency_group_of_pages = {}    # page path -> dependency group name
        self._dependencies = {}

        self._dependencies_in_page_build_preparation_stage = {}
        self._dependencies_in_page_build_stage = {}
        self._dependencies_in_page_expansion_preparation_stage = {}
        self._dependencies_in_page_expansion_stage = {}
        self._dependencies_in_page_rendering_stage = {}
        self._dependencies_in_page_exportation_stage = {}
        self._dependencies_in_page_build_finalization_stage = {}

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
        self._preprocessors_before_page_exportation_stage = []
        self._postprocessors_after_page_exportation_stage = []
        self._preprocessors_before_page_build_finalization_stage = []
        self._postprocessors_after_page_build_finalization_stage = []

    def add_page(self, page_definition):
        path = page_definition.path
        dependency_group = page_definition.dependency_group

        if dependency_group is None:
            dependency_group = path
        self._dependency_group_of_pages[path] = dependency_group

        self._pages_dict[page_definition.path] = page_definition
        self._pages.append(page_definition)

    def add_processor(
        self,
        stage: str,
        processor: Callable[["BuildContext"], None],
    ):
        if not isinstance(stage, str):
            raise ValueError("processor stage must be a str")
        if not callable(processor):
            raise TypeError("processor must be a callable")

        if stage == "pre_prepare_page_build":
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
        elif stage == "pre_export_pages":
            self._preprocessors_before_page_exportation_stage.append(processor)
        elif stage == "post_export_pages":
            self._postprocessors_after_page_exportation_stage.append(processor)
        elif stage == "pre_finalize_page_build":
            self._preprocessors_before_page_build_finalization_stage.append(processor)
        elif stage == "post_finalize_page_build":
            self._postprocessors_after_page_build_finalization_stage.append(processor)
        else:
            raise ValueError("invalid processor stage: '{}'".format(stage))
