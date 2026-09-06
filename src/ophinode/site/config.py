import os

# These three groups are the single source of truth for build-configuration
# keys and their default values. Each configuration-bearing class (Site,
# RootBuildContext, PageGroup, BuildContext) composes its own key set and
# default values from whichever of these groups actually apply to it,
# instead of hand-duplicating the full set of keys/values itself.

# Keys that only matter once, at the level that decides how the whole site
# build is orchestrated (sync vs. parallel, how results are merged/written).
# Only Site and RootBuildContext need these.
ORCHESTRATION_CONFIG_DEFAULT_VALUES = {
    "build_strategy"                         : "sync",
    "parallel_build_workers"                 : os.cpu_count(),
    "parallel_build_chunksize"               : 1,
    "auto_write_exported_site_build_files"   : True,
    "gather_and_merge_page_build_results"    : True,
}

# The "should I deep-copy my children before handing them off" decision.
# It is consumed locally at the two points where that decision is made
# (Site, when creating a RootBuildContext; PageGroup, when creating a
# BuildContext) and never needs to travel any further down than that.
PRESERVE_CONFIG_DEFAULT_VALUES = {
    "preserve_site_definition_across_builds" : False,
}

# Keys that control the actual page-build/rendering behavior. These are
# universal: they flow unchanged from Site all the way down to BuildContext.
PAGE_BUILD_CONFIG_DEFAULT_VALUES = {
    "export_root_path"                       : "./ophinode_exported_files",
    "default_layout"                         : None,
    "page_default_file_name"                 : "index.html",
    "page_default_file_name_suffix"          : ".html",
    "auto_write_exported_page_build_files"   : False,
    "return_site_data_after_page_build"      : False,
    "return_page_data_after_page_build"      : False,
    "return_misc_data_after_page_build"      : True,
    "return_built_pages_after_page_build"    : False,
    "return_expanded_pages_after_page_build" : False,
    "return_rendered_pages_after_page_build" : False,
    "return_exported_files_after_page_build" : True,
    "html_default_escape_ampersands"         : False,
    "html_default_escape_tag_delimiters"     : True,
    "disable_auto_newline_when_rendering"    : False,
    "disable_auto_indent_when_rendering"     : False,
    "auto_indent_string_for_top_level"       : "  ",
    "append_newline_to_render_result"        : False,
}
