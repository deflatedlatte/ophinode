from abc import ABC, abstractmethod

from .page import Page

class Layout(ABC):
    @abstractmethod
    def build(self, page: Page, context: "ophinode.site.BuildContext"):
        pass

