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

class Layout(ABC):
    @abstractmethod
    def build(self, page: Any, context: "ophinode.site.BuildContext"):
        pass

