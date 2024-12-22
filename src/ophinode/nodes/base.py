from abc import ABC, abstractmethod

class ClosedRenderable(ABC):
    @abstractmethod
    def render(self, context: "ophinode.rendering.RenderContext"):
        pass

class OpenRenderable(ABC):
    @abstractmethod
    def render_start(self, context: "ophinode.rendering.RenderContext"):
        pass

    @abstractmethod
    def render_end(self, context: "ophinode.rendering.RenderContext"):
        pass

class Expandable(ABC):
    @abstractmethod
    def expand(self, context: "ophinode.rendering.RenderContext"):
        pass

class Preparable(ABC):
    @abstractmethod
    def prepare(self, context: "ophinode.rendering.RenderContext"):
        pass

class Page(ABC):
    @property
    @abstractmethod
    def layout(self):
        pass

class Layout(ABC):
    @abstractmethod
    def build(self, page: Page, context: "ophinode.rendering.RenderContext"):
        pass

