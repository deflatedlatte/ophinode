from typing import Any
from abc import ABC, abstractmethod

class ClosedRenderable(ABC):
    @abstractmethod
    def render(self, context: "ophinode.site.BuildContext"):
        pass

class OpenRenderable(ABC):
    @abstractmethod
    def render_start(self, context: "ophinode.site.BuildContext"):
        pass

    @abstractmethod
    def render_end(self, context: "ophinode.site.BuildContext"):
        pass

    @property
    def auto_newline(self):
        return False

    @property
    def auto_indent(self):
        return False

class Expandable(ABC):
    @abstractmethod
    def expand(self, context: "ophinode.site.BuildContext"):
        pass

class Preparable(ABC):
    @abstractmethod
    def prepare(self, context: "ophinode.site.BuildContext"):
        pass

class Page:
    @property
    def layout(self):
        return None

    def export(self, context: "ophinode.site.BuildContext", page_path: str):
        export_path = page_path
        page_output_file_extension = context.get_config_value("page_output_file_extension")

        if export_path.endswith("/"):
            export_path += context.get_config_value("page_output_default_filename")
        elif page_output_file_extension:
            fname = export_path[export_path.rfind("/")+1:]
            dot_index = fname.rfind(".")
            if (
                (
                    # dot is not found at all,
                    dot_index == -1
                    # or default extension is already there
                    or fname[dot_index+1:]
                       != page_output_file_extension
                )
                and
                (
                    # the rightmost dot is not the first (or last) character
                    dot_index != 0
                    and (fname and dot_index != len(fname)-1)
                )
            ):
                export_path += "." + page_output_file_extension

        render_result = context.get_rendered_page(page_path)
        context.export_file(export_path, render_result)

class Layout(ABC):
    @abstractmethod
    def build(self, page: Page, context: "ophinode.site.BuildContext"):
        pass

