import sys
if sys.version_info.major == 3 and sys.version_info.minor < 9:
    from typing import Mapping
else:
    from collections.abc import Mapping
import os.path
from typing import Any, Union
from enum import Enum

from ophinode.rendering import RenderNode
from .page_group import PageGroup

class BuildPhase(Enum):
    INIT                        = 0
    PRE_PREPARE_SITE_BUILD      = 1
    PREPARE_SITE_BUILD          = 2
    POST_PREPARE_SITE_BUILD     = 3
    PRE_PREPARE_PAGE_BUILD      = 4
    PREPARE_PAGE_BUILD          = 5
    POST_PREPARE_PAGE_BUILD     = 6
    PRE_BUILD_PAGES             = 7
    BUILD_PAGES                 = 8
    POST_BUILD_PAGES            = 9
    PRE_PREPARE_PAGE_EXPANSION  = 10
    PREPARE_PAGE_EXPANSION      = 11
    POST_PREPARE_PAGE_EXPANSION = 12
    PRE_EXPAND_PAGES            = 13
    EXPAND_PAGES                = 14
    POST_EXPAND_PAGES           = 15
    PRE_RENDER_PAGES            = 16
    RENDER_PAGES                = 17
    POST_RENDER_PAGES           = 18
    PRE_EXPORT_PAGES            = 19
    EXPORT_PAGES                = 20
    POST_EXPORT_PAGES           = 21
    PRE_FINALIZE_PAGE_BUILD     = 22
    FINALIZE_PAGE_BUILD         = 23
    POST_FINALIZE_PAGE_BUILD    = 24
    PRE_FINALIZE_SITE_BUILD     = 25
    FINALIZE_SITE_BUILD         = 26
    POST_FINALIZE_SITE_BUILD    = 27

BUILD_CONTEXT_CONFIG_DEFAULT_VALUES = {
    "export_root_path"                       : "",
    "default_layout"                         : None,
    "page_output_default_filename"           : "index.html",
    "page_output_file_extension"             : "html",
    "auto_write_exported_page_build_files"   : False,
    "return_site_data_after_page_build"      : False,
    "return_page_data_after_page_build"      : False,
    "return_misc_data_after_page_build"      : True,
    "return_built_pages_after_page_build"    : False,
    "return_expanded_pages_after_page_build" : False,
    "return_rendered_pages_after_page_build" : False,
    "return_exported_files_after_page_build" : False,
}
BUILD_CONTEXT_CONFIG_KEYS = set(BUILD_CONTEXT_CONFIG_DEFAULT_VALUES)

class BuildContext:
    def __init__(
        self,
        page_group: PageGroup,
        site_data: dict,
        page_data: dict,
        build_config: Union[dict, None] = None
    ):
        self._phase = BuildPhase.INIT

        self._config = {}
        if build_config is not None:
            self.update_config(build_config)

        self._current_page_path = None
        self._current_page = None
        self._page_group = page_group
        self._site_data = site_data
        self._page_data = page_data
        self._misc_data = {}
        self._built_pages = {}
        self._expanded_pages = {}
        self._rendered_pages = {}
        self._exported_files = {}

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

    @property
    def preprocessors_before_page_build_preparation_stage(self):
        return self._preprocessors_before_page_build_preparation_stage

    @property
    def postprocessors_after_page_build_preparation_stage(self):
        return self._postprocessors_after_page_build_preparation_stage

    @property
    def preprocessors_before_page_build_stage(self):
        return self._preprocessors_before_page_build_stage

    @property
    def postprocessors_after_page_build_stage(self):
        return self._postprocessors_after_page_build_stage

    @property
    def preprocessors_before_page_expansion_preparation_stage(self):
        return self._preprocessors_before_page_expansion_preparation_stage

    @property
    def postprocessors_after_page_expansion_preparation_stage(self):
        return self._postprocessors_after_page_expansion_preparation_stage

    @property
    def preprocessors_before_page_expansion_stage(self):
        return self._preprocessors_before_page_expansion_stage

    @property
    def postprocessors_after_page_expansion_stage(self):
        return self._postprocessors_after_page_expansion_stage

    @property
    def preprocessors_before_page_rendering_stage(self):
        return self._preprocessors_before_page_rendering_stage

    @property
    def postprocessors_after_page_rendering_stage(self):
        return self._postprocessors_after_page_rendering_stage

    @property
    def preprocessors_before_page_exportation_stage(self):
        return self._preprocessors_before_page_exportation_stage

    @property
    def postprocessors_after_page_exportation_stage(self):
        return self._postprocessors_after_page_exportation_stage

    @property
    def preprocessors_before_page_build_finalization_stage(self):
        return self._preprocessors_before_page_build_finalization_stage

    @property
    def postprocessors_after_page_build_finalization_stage(self):
        return self._postprocessors_after_page_build_finalization_stage

    def get_config_value(self, key: str):
        if not isinstance(key, str):
            raise TypeError("key must be a str")
        if key not in BUILD_CONTEXT_CONFIG_KEYS:
            raise ValueError("unknown config key: {}".format(k))
        if key in self._config:
            return self._config[key]
        return BUILD_CONTEXT_CONFIG_DEFAULT_VALUES[key]

    def update_config(
        self,
        config_values: Mapping,
        ignore_invalid_keys: bool = False
    ):
        if not isinstance(config_values, Mapping):
            raise TypeError("config_values must be a mapping")
        for k, v in config_values.items():
            if k not in BUILD_CONTEXT_CONFIG_KEYS:
                if ignore_invalid_keys:
                    continue
                raise ValueError("unknown config key: {}".format(k))
            self._config[k] = v

    def get_build_phase(self) -> BuildPhase:
        return self._phase

    def set_build_phase(self, phase: BuildPhase):
        if not isinstance(phase, BuildPhase):
            raise TypeError("phase must be a BuildPhase, not {}".format(phase.__class__.__name__))
        self._phase = phase

    def set_current_page(self, path, page):
        self._current_page_path = path
        self._current_page = page

    def unset_current_page(self):
        self._current_page_path = None
        self._current_page = None

    def get_current_page(self):
        """Get the current Page instance that is being processed.

        Returns a relevant Page instance, or None if no Page instance is
        appropriate.
        """
        return self._current_page

    def get_current_page_path(self):
        """Get path of the current Page instance that is being processed.

        Returns a string containing the path of the relevant Page
        instance, or None if no Page instance is appropriate.
        """
        return self._current_page_path

    def get_site_data(self, key: str) -> Any:
        """Get a global Site data whose name is 'key'.
        """
        data = self._site_data[key]
        return data

    def get_page_data(self, key: str, page_path: Union[str, None] = None):
        """Get a local data whose name is 'key' from Page 'page_path'.
        """
        page_data = self._page_data[page_path]
        data = page_data[key]
        return data

    def get_page(self, page_path: str):
        return self._site.get_page(page_path)

    def get_pages(self):
        return self._site.get_pages()

    def get_page_paths(self):
        return self._site.get_page_paths()

    def has_page(self, page_path: str):
        return self._site.has_page(page_path)

    def set_built_page(self, page_path: str, built_page: Any):
        self._built_pages[page_path] = built_page

    def get_built_page(self, page_path: str):
        return self._built_pages[page_path]

    def get_built_pages(self):
        return self._built_pages.copy()

    def get_built_page_paths(self):
        return list(self._built_pages.keys())

    def is_built_page_path(self, page_path: str):
        return page_path in self._built_pages

    def set_expanded_page(self, page_path: str, expanded_page: RenderNode):
        self._expanded_pages[page_path] = expanded_page

    def get_expanded_page(self, page_path: str):
        return self._expanded_pages[page_path]

    def get_expanded_pages(self):
        return self._expanded_pages.copy()

    def get_expanded_page_paths(self):
        return list(self._expanded_pages.keys())

    def is_expanded_page_path(self, page_path: str):
        return page_path in self._expanded_pages

    def set_rendered_page(self, page_path: str, rendered_page: str):
        self._rendered_pages[page_path] = rendered_page

    def get_rendered_page(self, page_path: str):
        return self._rendered_pages[page_path]

    def get_rendered_pages(self):
        return self._rendered_pages.copy()

    def get_rendered_page_paths(self):
        return list(self._rendered_pages.keys())

    def is_rendered_page_path(self, page_path: str):
        return page_path in self._rendered_pages

    def export_file(
        self,
        export_path: str,
        data: Union[str, bytes, bytearray, memoryview]
    ):
        normalized_export_path = os.path.normpath("/" + export_path)
        if normalized_export_path in self._exported_files:
            raise ExportPathCollisionError(
                "attempted to export a page to '{}', but another file is "
                "already exported to that path".format(normalized_export_path)
            )
        self._exported_files[normalized_export_path] = data

    def get_exported_file(self, export_path: str):
        return self._exported_files[export_path]

    def get_exported_files(self):
        return self._exported_files.copy()

    def get_exported_file_paths(self):
        return list(self._exported_files.keys())

    def is_exported_file_path(self, export_path: str):
        return export_path in self._exported_files

    def get_page_export_path(self, page_path: str):
        pass

    def get_page_url(
        self,
        page_path: str,
        relative_path: bool = True,
        relative_to: Union[str, None] = None,
    ):
        pass

    def get_file_url(
        self,
        export_path: str,
        relative_path: bool = True,
        relative_to: Union[str, None] = None,
    ):
        pass

ROOT_BUILD_CONTEXT_CONFIG_DEFAULT_VALUES = {
    "export_root_path"                       : "",
    "default_layout"                         : None,
    "build_strategy"                         : "sync",
    "parallel_build_workers"                 : os.cpu_count(),
    "parallel_build_chunksize"               : os.cpu_count() * 4,
    "page_output_default_filename"           : "index.html",
    "page_output_file_extension"             : "html",
    "auto_write_exported_page_build_files"   : False,
    "auto_write_exported_site_build_files"   : True,
    "return_site_data_after_page_build"      : False,
    "return_page_data_after_page_build"      : False,
    "return_misc_data_after_page_build"      : True,
    "return_built_pages_after_page_build"    : False,
    "return_expanded_pages_after_page_build" : False,
    "return_rendered_pages_after_page_build" : False,
    "return_exported_files_after_page_build" : False,
}
ROOT_BUILD_CONTEXT_CONFIG_KEYS = set(ROOT_BUILD_CONTEXT_CONFIG_DEFAULT_VALUES)

class RootBuildContext:
    def __init__(
        self,
        site: "ophinode.site.Site",
        build_config: Union[dict, None] = None
    ):
        self._phase = BuildPhase.INIT

        from ophinode.site import Site
        if not isinstance(site, Site):
            raise TypeError("site must be a Site, not {}".format(site.__class__.__name__))
        self._site = site

        self._config = {}
        if build_config is not None:
            self.update_config(build_config)

        self._page_groups = site._page_groups.copy()    # TODO: maybe deep copy?
        self._subcontexts = []
        self._site_data = {}
        self._page_data = {}

        self._preprocessors_before_site_build_preparation_stage = []
        self._postprocessors_after_site_build_preparation_stage = []
        self._preprocessors_before_site_build_finalization_stage = []
        self._postprocessors_after_site_build_finalization_stage = []

    @property
    def preprocessors_before_site_build_preparation_stage(self):
        return self._preprocessors_before_site_build_preparation_stage

    @property
    def postprocessors_after_site_build_preparation_stage(self):
        return self._postprocessors_after_site_build_preparation_stage

    @property
    def preprocessors_before_site_build_finalization_stage(self):
        return self._preprocessors_before_site_build_finalization_stage

    @property
    def postprocessors_after_site_build_finalization_stage(self):
        return self._postprocessors_after_site_build_finalization_stage

    def create_subcontext(self, page_group: PageGroup, build_config: dict):
        subcontext = BuildContext(
            page_group,
            self._site_data,
            self._page_data,
            build_config,
        )
        self._subcontexts.append(subcontext)

    @property
    def subcontexts(self):
        return self._subcontexts

    def get_config_value(self, key: str):
        if not isinstance(key, str):
            raise TypeError("key must be a str")
        if key not in ROOT_BUILD_CONTEXT_CONFIG_KEYS:
            raise ValueError("unknown config key: {}".format(k))
        if key in self._config:
            return self._config[key]
        return ROOT_BUILD_CONTEXT_CONFIG_DEFAULT_VALUES[key]

    def update_config(
        self,
        config_values: Mapping,
        ignore_invalid_keys: bool = False
    ):
        if not isinstance(config_values, Mapping):
            raise TypeError("config_values must be a mapping")
        for k, v in config_values.items():
            if k not in ROOT_BUILD_CONTEXT_CONFIG_KEYS:
                if ignore_invalid_keys:
                    continue
                raise ValueError("unknown config key: {}".format(k))
            self._config[k] = v

    def set_site(self, site: "ophinode.site.Site"):
        from ophinode.site import Site
        if not isinstance(site, Site):
            raise TypeError("site must be a Site, not {}".format(site.__class__.__name__))
        self._site = site

    def get_site(self):
        return self._site

    def get_build_phase(self) -> BuildPhase:
        return self._phase

    def set_build_phase(self, phase: BuildPhase):
        if not isinstance(phase, BuildPhase):
            raise TypeError("phase must be a BuildPhase, not {}".format(phase.__class__.__name__))
        self._phase = phase

    def get_site_data(self, key: str) -> Any:
        """Get a global Site data whose name is 'key'.
        """
        data = self._site_data[key]
        return data

    def get_page_data(self, key: str, page_path: Union[str, None] = None):
        """Get a local data whose name is 'key' from Page 'page_path'.
        """
        page_data = self._page_data[page_path]
        data = page_data[key]
        return data

    def get_page(self, page_path: str):
        return self._site.get_page(page_path)

    def get_pages(self):
        return self._site.get_pages()

    def get_page_paths(self):
        return self._site.get_page_paths()

    def has_page(self, page_path: str):
        return self._site.has_page(page_path)

    def set_built_page(self, page_path: str, built_page: Any):
        self._built_pages[page_path] = built_page

    def get_built_page(self, page_path: str):
        return self._built_pages[page_path]

    def get_built_pages(self):
        return self._built_pages.copy()

    def get_built_page_paths(self):
        return list(self._built_pages.keys())

    def is_built_page_path(self, page_path: str):
        return page_path in self._built_pages

    def set_expanded_page(self, page_path: str, expanded_page: RenderNode):
        self._expanded_pages[page_path] = expanded_page

    def get_expanded_page(self, page_path: str):
        return self._expanded_pages[page_path]

    def get_expanded_pages(self):
        return self._expanded_pages.copy()

    def get_expanded_page_paths(self):
        return list(self._expanded_pages.keys())

    def is_expanded_page_path(self, page_path: str):
        return page_path in self._expanded_pages

    def set_rendered_page(self, page_path: str, rendered_page: str):
        self._rendered_pages[page_path] = rendered_page

    def get_rendered_page(self, page_path: str):
        return self._rendered_pages[page_path]

    def get_rendered_pages(self):
        return self._rendered_pages.copy()

    def get_rendered_page_paths(self):
        return list(self._rendered_pages.keys())

    def is_rendered_page_path(self, page_path: str):
        return page_path in self._rendered_pages

    def export_file(
        self,
        export_path: str,
        data: Union[str, bytes, bytearray, memoryview]
    ):
        normalized_export_path = os.path.normpath("/" + export_path)
        if normalized_export_path in self._exported_files:
            raise ExportPathCollisionError(
                "attempted to export a page to '{}', but another file is "
                "already exported to that path".format(normalized_export_path)
            )
        self._exported_files[normalized_export_path] = data

    def get_exported_file(self, export_path: str):
        return self._exported_files[export_path]

    def get_exported_files(self):
        return self._exported_files.copy()

    def get_exported_file_paths(self):
        return list(self._exported_files.keys())

    def is_exported_file_path(self, export_path: str):
        return export_path in self._exported_files

    def get_page_url(
        self,
        page_path: str,
        relative_path: bool = True,
        relative_to: Union[str, None] = None,
    ):
        pass

    def get_file_url(
        self,
        export_path: str,
        relative_path: bool = True,
        relative_to: Union[str, None] = None,
    ):
        pass

