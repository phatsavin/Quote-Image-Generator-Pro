from __future__ import annotations

import ast
import unittest
from pathlib import Path


class FakeSettings:
    def __init__(self, values=None, error=None):
        self.values = values or {}
        self.error = error

    def value(self, key, default):
        if self.error:
            raise self.error
        return self.values.get(key, default)


def load_read_preference():
    app_path = Path(__file__).resolve().parents[1] / "app.py"
    tree = ast.parse(app_path.read_text(encoding="utf-8"))
    future_import = next(
        node
        for node in tree.body
        if isinstance(node, ast.ImportFrom) and node.module == "__future__"
    )
    function = next(
        node
        for node in tree.body
        if isinstance(node, ast.FunctionDef) and node.name == "read_preference"
    )
    module = ast.Module(body=[future_import, function], type_ignores=[])
    namespace = {}
    exec(compile(ast.fix_missing_locations(module), str(app_path), "exec"), namespace)
    return namespace["read_preference"]


def load_native_display_path():
    app_path = Path(__file__).resolve().parents[1] / "app.py"
    tree = ast.parse(app_path.read_text(encoding="utf-8"))
    future_import = next(
        node
        for node in tree.body
        if isinstance(node, ast.ImportFrom) and node.module == "__future__"
    )
    function = next(
        node
        for node in tree.body
        if isinstance(node, ast.FunctionDef)
        and node.name == "native_display_path"
    )
    module = ast.Module(body=[future_import, function], type_ignores=[])
    namespace = {"sys": __import__("sys")}
    exec(compile(ast.fix_missing_locations(module), str(app_path), "exec"), namespace)
    return namespace["native_display_path"]


class PreferenceCompatibilityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.read_preference = staticmethod(load_read_preference())
        cls.native_display_path = staticmethod(load_native_display_path())

    def test_legacy_integer_watermark_becomes_string(self):
        settings = FakeSettings({"watermark_position": 2})
        self.assertEqual(
            self.read_preference(
                settings,
                "watermark_position",
                "bottom-right",
            ),
            "2",
        )

    def test_current_string_watermark_stays_string(self):
        settings = FakeSettings({"watermark_position": "top-center"})
        self.assertEqual(
            self.read_preference(
                settings,
                "watermark_position",
                "bottom-right",
            ),
            "top-center",
        )

    def test_numeric_strings_are_converted_manually(self):
        settings = FakeSettings({"font_max": "104", "blur": "2.5"})
        self.assertEqual(
            self.read_preference(settings, "font_max", 80),
            104,
        )
        self.assertEqual(
            self.read_preference(settings, "blur", 0.0),
            2.5,
        )

    def test_invalid_or_unreadable_values_use_default(self):
        invalid = FakeSettings({"font_max": "not-a-number"})
        unreadable = FakeSettings(error=TypeError("QVariant mismatch"))
        self.assertEqual(
            self.read_preference(invalid, "font_max", 80),
            80,
        )
        self.assertEqual(
            self.read_preference(unreadable, "font_max", 80),
            80,
        )

    def test_version_170_uses_isolated_settings_profile(self):
        app_path = Path(__file__).resolve().parents[1] / "app.py"
        source = app_path.read_text(encoding="utf-8")
        self.assertIn('APP_VERSION = "1.7.0"', source)
        self.assertIn('SETTINGS_PROFILE = "QuoteImageGeneratorProV2"', source)
        self.assertIn(
            'QSettings("PuVinTools", SETTINGS_PROFILE)',
            source,
        )

    def test_windows_paths_use_backslashes(self):
        self.assertEqual(
            self.native_display_path(
                "E:/English Quote/1. Healing & Self-Worth",
                windows=True,
            ),
            r"E:\English Quote\1. Healing & Self-Worth",
        )
        self.assertEqual(
            self.native_display_path(
                r"C:\Users/phats/Downloads/quotes.docx",
                windows=True,
            ),
            r"C:\Users\phats\Downloads\quotes.docx",
        )

    def test_batch_progress_updates_live_preview(self):
        app_path = Path(__file__).resolve().parents[1] / "app.py"
        source = app_path.read_text(encoding="utf-8")
        self.assertIn("str(result.output_path)", source)
        self.assertIn("pixmap = QPixmap(str(output_path))", source)
        self.assertIn(
            "self.preview_label.set_source_pixmap(pixmap)",
            source,
        )


if __name__ == "__main__":
    unittest.main()
