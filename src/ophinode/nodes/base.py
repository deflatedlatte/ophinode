from typing import Any
from abc import ABC, abstractmethod

class ClosedRenderable(ABC):
    @abstractmethod
    def render(self, context: "ophinode.site.BuildContext"):
        pass

    @property
    def prevent_auto_newline_before_me(self):
        "Disallow inserting auto newline before this renderable."
        return False

    @property
    def prevent_auto_newline_after_me(self):
        "Disallow inserting auto newline after this renderable."
        return False

class OpenRenderable(ABC):
    @abstractmethod
    def render_start(self, context: "ophinode.site.BuildContext"):
        pass

    @abstractmethod
    def render_end(self, context: "ophinode.site.BuildContext"):
        pass

    @property
    def auto_newline_for_children(self):
        """Whether auto newline insertion is enabled for children.

        If True, a newline is inserted between each two children when
        rendering.
        """

        return False

    @property
    def pad_newline_after_opening(self):
        """Insert newline after render_start().

        A newline is inserted only if the render result of children is
        a non-empty string, and auto newline is enabled in the current
        context.
        """

        return False

    @property
    def pad_newline_before_closing(self):
        """Insert newline before render_end().

        A newline is inserted only if the render result of children is
        a non-empty string, and auto newline is enabled in the current
        context.
        """

        return False

    @property
    def prevent_auto_newline_before_me(self):
        "Disallow inserting auto newline before this renderable."
        return False

    @property
    def prevent_auto_newline_after_me(self):
        "Disallow inserting auto newline after this renderable."
        return False

    @property
    def auto_indent_for_children(self):
        "Automatically insert indentation in front of each child."
        return False

    @property
    def auto_indent_string(self):
        """A string to use as indentation before each child.

        If None, the parent's indentation string is used instead.
        """

        return None

class Expandable(ABC):
    @abstractmethod
    def expand(self, context: "ophinode.site.BuildContext"):
        pass

class Preparable(ABC):
    @abstractmethod
    def prepare(self, context: "ophinode.site.BuildContext"):
        pass

