import unittest

import ophinode


class DemoPage(ophinode.HTML5Page):
    def head(self, context):
        return [
            ophinode.Meta(charset="utf-8"),
            ophinode.Title("Demo"),
        ]

    def body(self, context):
        return ophinode.Div(
            ophinode.H1("Hello"),
            ophinode.P("A < B & C"),
        )


class SmokeTests(unittest.TestCase):
    def test_public_api_imports(self):
        self.assertTrue(hasattr(ophinode, "Site"))
        self.assertTrue(hasattr(ophinode, "HTML5Page"))
        self.assertTrue(hasattr(ophinode, "render_page"))
        self.assertTrue(hasattr(ophinode, "render_html"))

    def test_page_rendering(self):
        result = ophinode.render_page(DemoPage())

        self.assertIn("<!doctype html>", result)
        self.assertIn('<meta charset="utf-8">', result)
        self.assertIn("<title>Demo</title>", result)
        self.assertIn("<h1>", result)
        self.assertIn("Hello", result)
        self.assertIn("A &lt; B & C", result)

    def test_html_rendering(self):
        result = ophinode.render_html(
            ophinode.Div("content", id="main")
        )

        self.assertIn('<div id="main">', result)
        self.assertIn("content", result)


if __name__ == "__main__":
    unittest.main()
