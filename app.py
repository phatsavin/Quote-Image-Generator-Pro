from __future__ import annotations

import os
import sys
from pathlib import Path

from PyQt5.QtCore import QSettings, Qt, QThread, QUrl, pyqtSignal
from PyQt5.QtGui import (
    QColor,
    QDesktopServices,
    QFont,
    QFontDatabase,
    QIcon,
    QImage,
    QPixmap,
)
from PyQt5.QtWidgets import (
    QApplication,
    QCheckBox,
    QColorDialog,
    QComboBox,
    QDoubleSpinBox,
    QFileDialog,
    QFrame,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QProgressBar,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QSlider,
    QSpinBox,
    QSplitter,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from quote_engine import (
    GenerationItem,
    QuoteGeneratorError,
    RenderSettings,
    create_generation_items,
    generate_batch,
    list_images,
    load_quotes,
    render_quote_image,
)


APP_NAME = "Quote Image Generator Pro"
APP_VERSION = "1.7.0"
PROJECT_DIR = Path(__file__).resolve().parent
APP_ICON_PATH = PROJECT_DIR / "assets" / "QuoteImageGeneratorPro.ico"
SETTINGS_PROFILE = "QuoteImageGeneratorProV2"


def native_display_path(value: str | Path, windows: bool | None = None) -> str:
    """Display Windows paths consistently with backslash separators."""
    text = str(value).strip()
    if windows is None:
        windows = sys.platform.startswith("win")
    return text.replace("/", "\\") if windows else text


def read_preference(settings: QSettings, key: str, default):
    """Read old and current QSettings values without QVariant conversion errors."""
    try:
        value = settings.value(key, default)
    except (TypeError, ValueError):
        return default
    if value is None:
        return default
    try:
        if isinstance(default, bool):
            if isinstance(value, str):
                return value.strip().lower() in {"1", "true", "yes", "on"}
            return bool(value)
        if isinstance(default, int):
            return int(value)
        if isinstance(default, float):
            return float(value)
        if isinstance(default, str):
            return str(value)
    except (TypeError, ValueError):
        return default
    return value


STYLE_SHEET = """
QWidget {
    color: #172033;
    background: #F4F7FB;
    font-size: 10.5pt;
}
QMainWindow {
    background: #EEF3F9;
}
QGroupBox {
    background: #FFFFFF;
    border: 1px solid #D8E1EC;
    border-radius: 10px;
    margin-top: 16px;
    padding: 14px 10px 10px 10px;
    font-weight: 700;
    color: #173A5E;
}
QGroupBox::title {
    subcontrol-origin: margin;
    subcontrol-position: top left;
    left: 12px;
    padding: 0 6px;
    background: #FFFFFF;
}
QLineEdit, QComboBox, QSpinBox, QDoubleSpinBox, QTextEdit {
    background: #FFFFFF;
    border: 1px solid #C9D5E3;
    border-radius: 7px;
    padding: 7px;
    selection-background-color: #2E74B5;
}
QLineEdit:focus, QComboBox:focus, QSpinBox:focus,
QDoubleSpinBox:focus, QTextEdit:focus {
    border: 1px solid #2E74B5;
}
QPushButton {
    background: #E8EEF6;
    color: #173A5E;
    border: 1px solid #C8D6E5;
    border-radius: 7px;
    padding: 8px 13px;
    font-weight: 600;
}
QPushButton:hover {
    background: #DDE8F3;
}
QPushButton:pressed {
    background: #CCDDEC;
}
QPushButton#primaryButton {
    background: #1E6FB2;
    color: white;
    border: 1px solid #1E6FB2;
    padding: 10px 18px;
}
QPushButton#primaryButton:hover {
    background: #185E98;
}
QPushButton#dangerButton {
    background: #FFF1F0;
    color: #A63232;
    border: 1px solid #E7B8B5;
}
QPushButton:disabled {
    background: #EDF1F5;
    color: #8D98A6;
    border-color: #DDE3E9;
}
QProgressBar {
    background: #E7EDF4;
    border: none;
    border-radius: 7px;
    text-align: center;
    min-height: 20px;
}
QProgressBar::chunk {
    background: #2E74B5;
    border-radius: 7px;
}
QScrollArea {
    border: none;
    background: transparent;
}
QSlider::groove:horizontal {
    height: 6px;
    background: #D7E1EC;
    border-radius: 3px;
}
QSlider::handle:horizontal {
    background: #2E74B5;
    width: 17px;
    margin: -6px 0;
    border-radius: 8px;
}
QLabel#titleLabel {
    font-size: 22pt;
    font-weight: 800;
    color: #102A43;
}
QLabel#subtitleLabel {
    color: #61758A;
}
QLabel#sourceSummary {
    background: #EDF7FF;
    color: #1C5A87;
    border: 1px solid #CFE6F7;
    border-radius: 8px;
    padding: 9px;
}
QLabel#previewSurface {
    background: #0C1724;
    color: #9FB0C3;
    border: 1px solid #263A4E;
    border-radius: 12px;
}
QFrame#rightPanel {
    background: #FFFFFF;
    border: 1px solid #D8E1EC;
    border-radius: 12px;
}
"""


def apply_ui_font(app: QApplication) -> str:
    installed = set(QFontDatabase().families())
    for family in ("Segoe UI", "Arial", "Helvetica"):
        if family in installed:
            app.setFont(QFont(family, 10))
            return family
    return app.font().family()


class ColorButton(QPushButton):
    color_changed = pyqtSignal(str)

    def __init__(self, color: str, parent=None):
        super().__init__(parent)
        self._color = color.upper()
        self.clicked.connect(self.choose_color)
        self.refresh()

    @property
    def color(self) -> str:
        return self._color

    def set_color(self, value: str) -> None:
        color = QColor(value)
        if not color.isValid():
            return
        self._color = color.name().upper()
        self.refresh()
        self.color_changed.emit(self._color)

    def choose_color(self) -> None:
        color = QColorDialog.getColor(QColor(self._color), self, "Choose Color")
        if color.isValid():
            self.set_color(color.name())

    def refresh(self) -> None:
        color = QColor(self._color)
        text_color = "#FFFFFF" if color.lightness() < 145 else "#142033"
        self.setText(self._color)
        self.setStyleSheet(
            "QPushButton {"
            f"background: {self._color}; color: {text_color};"
            "border: 1px solid #8A98A8; border-radius: 7px; padding: 7px;"
            "}"
        )


class PreviewLabel(QLabel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("previewSurface")
        self.setAlignment(Qt.AlignCenter)
        self.setMinimumSize(420, 480)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.setText(
            "PREVIEW\n\nSelect an Image Folder and Quote File,\n"
            "then click Preview Random."
        )
        self._source_pixmap: QPixmap | None = None

    def set_source_pixmap(self, pixmap: QPixmap) -> None:
        self._source_pixmap = pixmap
        self._update_scaled()

    def clear_preview(self) -> None:
        self._source_pixmap = None
        self.setPixmap(QPixmap())
        self.setText("PREVIEW")

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._update_scaled()

    def _update_scaled(self) -> None:
        if not self._source_pixmap or self._source_pixmap.isNull():
            return
        scaled = self._source_pixmap.scaled(
            max(1, self.width() - 24),
            max(1, self.height() - 24),
            Qt.KeepAspectRatio,
            Qt.SmoothTransformation,
        )
        self.setPixmap(scaled)


def pil_image_to_qpixmap(image) -> QPixmap:
    """Convert a Pillow image to a detached PyQt5 pixmap.

    Pillow 12 removed PyQt5 support from PIL.ImageQt. Converting the pixel
    buffer directly keeps the app compatible with current Pillow releases.
    """
    rgba = image.convert("RGBA")
    width, height = rgba.size
    image_data = rgba.tobytes("raw", "RGBA")
    qimage = QImage(
        image_data,
        width,
        height,
        width * 4,
        QImage.Format_RGBA8888,
    )
    return QPixmap.fromImage(qimage.copy())


class GenerationWorker(QThread):
    progress = pyqtSignal(int, int, str)
    completed = pyqtSignal(str, int, bool)
    failed = pyqtSignal(str)

    def __init__(
        self,
        items: list[GenerationItem],
        output_folder: str,
        settings: RenderSettings,
        parent=None,
    ):
        super().__init__(parent)
        self.items = items
        self.output_folder = output_folder
        self.render_settings = settings
        self._cancel_requested = False

    def cancel(self) -> None:
        self._cancel_requested = True

    def run(self) -> None:
        try:
            folder, results = generate_batch(
                self.items,
                self.output_folder,
                self.render_settings,
                progress_callback=lambda current, total, result: self.progress.emit(
                    current, total, str(result.output_path)
                ),
                should_cancel=lambda: self._cancel_requested,
                create_timestamp_folder=True,
            )
            self.completed.emit(
                str(folder),
                len(results),
                self._cancel_requested,
            )
        except Exception as exc:
            self.failed.emit(str(exc))


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.settings_store = QSettings("PuVinTools", SETTINGS_PROFILE)
        self.images: list[Path] = []
        self.quotes: list[str] = []
        self.worker: GenerationWorker | None = None
        self.last_output_folder = ""
        self.setWindowTitle(f"{APP_NAME} {APP_VERSION}")
        if APP_ICON_PATH.is_file():
            self.setWindowIcon(QIcon(str(APP_ICON_PATH)))
        self.resize(1380, 880)
        self.setMinimumSize(1080, 700)
        self.build_ui()
        self.load_preferences()
        self.refresh_summary()

    def build_ui(self) -> None:
        central = QWidget()
        outer = QVBoxLayout(central)
        outer.setContentsMargins(18, 14, 18, 18)
        outer.setSpacing(10)

        title = QLabel(APP_NAME)
        title.setObjectName("titleLabel")
        subtitle = QLabel(
            "Create quote images using random backgrounds and quotes from "
            "TXT, CSV, or DOCX files."
        )
        subtitle.setObjectName("subtitleLabel")
        outer.addWidget(title)
        outer.addWidget(subtitle)

        splitter = QSplitter(Qt.Horizontal)
        splitter.setChildrenCollapsible(False)
        splitter.addWidget(self.build_controls_panel())
        splitter.addWidget(self.build_preview_panel())
        splitter.setSizes([580, 780])
        outer.addWidget(splitter, 1)
        self.setCentralWidget(central)

    def build_controls_panel(self) -> QWidget:
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        content = QWidget()
        layout = QVBoxLayout(content)
        layout.setContentsMargins(0, 0, 10, 0)
        layout.setSpacing(10)

        layout.addWidget(self.build_sources_group())
        layout.addWidget(self.build_output_group())
        layout.addWidget(self.build_text_group())
        layout.addWidget(self.build_effects_group())
        layout.addWidget(self.build_watermark_group())
        layout.addWidget(self.build_actions_group())
        layout.addStretch(1)
        scroll.setWidget(content)
        return scroll

    def build_sources_group(self) -> QGroupBox:
        group = QGroupBox("1. Image and Quote Sources")
        layout = QGridLayout(group)
        layout.setColumnStretch(1, 1)

        self.image_folder_edit = QLineEdit()
        self.image_folder_edit.setPlaceholderText(
            "Folder containing JPG, PNG, or WEBP images..."
        )
        image_button = QPushButton("Browse Folder")
        image_button.clicked.connect(self.choose_image_folder)
        layout.addWidget(QLabel("Image Folder"), 0, 0)
        layout.addWidget(self.image_folder_edit, 0, 1)
        layout.addWidget(image_button, 0, 2)

        self.quote_file_edit = QLineEdit()
        self.quote_file_edit.setPlaceholderText("Quote file: TXT, CSV, or DOCX")
        quote_button = QPushButton("Browse File")
        quote_button.clicked.connect(self.choose_quote_file)
        layout.addWidget(QLabel("Quote File"), 1, 0)
        layout.addWidget(self.quote_file_edit, 1, 1)
        layout.addWidget(quote_button, 1, 2)

        self.output_folder_edit = QLineEdit()
        self.output_folder_edit.setPlaceholderText(
            "Folder for saving generated images..."
        )
        output_button = QPushButton("Browse Output")
        output_button.clicked.connect(self.choose_output_folder)
        layout.addWidget(QLabel("Output Folder"), 2, 0)
        layout.addWidget(self.output_folder_edit, 2, 1)
        layout.addWidget(output_button, 2, 2)

        for path_edit in (
            self.image_folder_edit,
            self.quote_file_edit,
            self.output_folder_edit,
        ):
            path_edit.editingFinished.connect(
                lambda edit=path_edit: edit.setText(
                    native_display_path(edit.text())
                )
            )

        self.source_summary = QLabel()
        self.source_summary.setObjectName("sourceSummary")
        layout.addWidget(self.source_summary, 3, 0, 1, 3)
        return group

    def build_output_group(self) -> QGroupBox:
        group = QGroupBox("2. Output Size and Batch Order")
        layout = QGridLayout(group)

        self.preset_combo = QComboBox()
        self.preset_combo.addItem("Facebook 4:5 - 1440 x 1800", (1440, 1800))
        self.preset_combo.addItem("Square 1:1 - 1080 x 1080", (1080, 1080))
        self.preset_combo.addItem("Story 9:16 - 1080 x 1920", (1080, 1920))
        self.preset_combo.addItem("Custom", None)
        self.preset_combo.currentIndexChanged.connect(self.apply_size_preset)
        layout.addWidget(QLabel("Preset"), 0, 0)
        layout.addWidget(self.preset_combo, 0, 1, 1, 3)

        self.width_spin = self.make_spin(320, 8000, 1440)
        self.height_spin = self.make_spin(320, 8000, 1800)
        layout.addWidget(QLabel("Width"), 1, 0)
        layout.addWidget(self.width_spin, 1, 1)
        layout.addWidget(QLabel("Height"), 1, 2)
        layout.addWidget(self.height_spin, 1, 3)

        self.count_spin = self.make_spin(1, 10000, 10)
        self.format_combo = QComboBox()
        self.format_combo.addItems(["JPEG", "PNG"])
        layout.addWidget(QLabel("Image Count"), 2, 0)
        layout.addWidget(self.count_spin, 2, 1)
        layout.addWidget(QLabel("Format"), 2, 2)
        layout.addWidget(self.format_combo, 2, 3)

        self.random_images_check = QCheckBox("Random Images")
        self.random_images_check.setChecked(True)
        self.random_quotes_check = QCheckBox("Random Quotes")
        self.random_quotes_check.setChecked(False)
        self.no_repeat_images_check = QCheckBox("Avoid Repeating Images in Batch")
        self.no_repeat_images_check.setChecked(True)
        self.no_repeat_quotes_check = QCheckBox("Avoid Repeating Quotes in Batch")
        self.no_repeat_quotes_check.setChecked(True)
        layout.addWidget(self.random_images_check, 3, 0, 1, 2)
        layout.addWidget(self.random_quotes_check, 3, 2, 1, 2)
        layout.addWidget(self.no_repeat_images_check, 4, 0, 1, 2)
        layout.addWidget(self.no_repeat_quotes_check, 4, 2, 1, 2)
        return group

    def build_text_group(self) -> QGroupBox:
        group = QGroupBox("3. Quote Typography")
        layout = QGridLayout(group)

        self.font_edit = QLineEdit()
        self.font_edit.setPlaceholderText(
            "Leave blank to use the default font automatically"
        )
        font_button = QPushButton("Browse Font")
        font_button.clicked.connect(self.choose_font)
        layout.addWidget(QLabel("Font TTF/OTF"), 0, 0)
        layout.addWidget(self.font_edit, 0, 1, 1, 2)
        layout.addWidget(font_button, 0, 3)

        self.position_combo = QComboBox()
        self.position_combo.addItem("Left", "left")
        self.position_combo.addItem("Center", "center")
        self.position_combo.addItem("Right", "right")
        self.text_color_button = ColorButton("#FFFFFF")
        layout.addWidget(QLabel("Quote Position"), 1, 0)
        layout.addWidget(self.position_combo, 1, 1, 1, 2)
        layout.addWidget(self.text_color_button, 1, 3)

        self.font_min_spin = self.make_spin(10, 300, 42)
        self.font_max_spin = self.make_spin(12, 500, 104)
        layout.addWidget(QLabel("Min Font"), 2, 0)
        layout.addWidget(self.font_min_spin, 2, 1)
        layout.addWidget(QLabel("Max Font"), 2, 2)
        layout.addWidget(self.font_max_spin, 2, 3)

        self.safe_margin_spin = self.make_spin(2, 25, 8, "%")
        self.text_area_spin = self.make_spin(25, 90, 48, "%")
        layout.addWidget(QLabel("Safe Margin"), 3, 0)
        layout.addWidget(self.safe_margin_spin, 3, 1)
        layout.addWidget(QLabel("Text Area"), 3, 2)
        layout.addWidget(self.text_area_spin, 3, 3)

        self.vertical_slider = QSlider(Qt.Horizontal)
        self.vertical_slider.setRange(0, 100)
        self.vertical_slider.setValue(50)
        self.vertical_value_label = QLabel("50%")
        self.vertical_slider.valueChanged.connect(
            lambda value: self.vertical_value_label.setText(f"{value}%")
        )
        layout.addWidget(QLabel("Vertical Position"), 4, 0)
        layout.addWidget(self.vertical_slider, 4, 1, 1, 2)
        layout.addWidget(self.vertical_value_label, 4, 3)

        self.quote_marks_check = QCheckBox("Add quotation marks around each quote")
        self.quote_marks_check.setChecked(True)
        layout.addWidget(self.quote_marks_check, 5, 0, 1, 4)
        return group

    def build_effects_group(self) -> QGroupBox:
        group = QGroupBox("4. Background and Readability")
        layout = QGridLayout(group)

        self.background_style_combo = QComboBox()
        self.background_style_combo.addItem("Classic Photo", "classic")
        self.background_style_combo.addItem(
            "TikTok Blur Frame",
            "tiktok-blur-frame",
        )
        self.background_style_combo.addItem(
            "TikTok Glass Gradient",
            "tiktok-glass-gradient",
        )
        self.background_style_combo.addItem(
            "Cinematic Vignette",
            "cinematic-vignette",
        )
        self.background_style_combo.addItem("Luxury Noir", "luxury-noir")
        self.background_style_combo.addItem(
            "Luxury Noir 2 - Original Color",
            "luxury-noir-color",
        )
        self.background_style_combo.setToolTip(
            "Choose a professional background treatment. Preview Random uses "
            "the selected style."
        )
        layout.addWidget(QLabel("Background Style"), 0, 0)
        layout.addWidget(self.background_style_combo, 0, 1, 1, 3)

        self.darken_spin = self.make_spin(0, 85, 22, "%")
        self.blur_spin = QDoubleSpinBox()
        self.blur_spin.setRange(0.0, 30.0)
        self.blur_spin.setSingleStep(0.5)
        self.blur_spin.setValue(0.0)
        self.blur_spin.setSuffix(" px")
        layout.addWidget(QLabel("Darken"), 1, 0)
        layout.addWidget(self.darken_spin, 1, 1)
        layout.addWidget(QLabel("Blur"), 1, 2)
        layout.addWidget(self.blur_spin, 1, 3)

        self.box_style_combo = QComboBox()
        self.box_style_combo.addItem("Translucent Box", "translucent")
        self.box_style_combo.addItem(
            "Decorative Quote Frame - No Fill",
            "quote-frame",
        )
        self.box_style_combo.addItem(
            "Corner Quote Frame - No Fill",
            "corner-frame",
        )
        self.box_style_combo.addItem(
            "Double Line Frame - No Fill",
            "double-frame",
        )
        self.box_style_combo.setToolTip(
            "Choose a translucent filled box or one of the decorative quote "
            "frames with no fill."
        )
        layout.addWidget(QLabel("Quote Background"), 2, 0)
        layout.addWidget(self.box_style_combo, 2, 1, 1, 3)

        self.box_check = QCheckBox("Enable quote background / frame")
        self.box_check.setChecked(True)
        self.box_opacity_spin = self.make_spin(0, 255, 105)
        self.box_color_button = ColorButton("#06111F")
        layout.addWidget(self.box_check, 3, 0, 1, 2)
        layout.addWidget(QLabel("Opacity"), 3, 2)
        layout.addWidget(self.box_opacity_spin, 3, 3)
        layout.addWidget(QLabel("Box / Frame Color"), 4, 0)
        layout.addWidget(self.box_color_button, 4, 1)

        self.shadow_check = QCheckBox("Text Shadow")
        self.shadow_check.setChecked(True)
        self.focal_combo = QComboBox()
        self.focal_combo.addItem("Center", "center")
        self.focal_combo.addItem("Keep Left", "left")
        self.focal_combo.addItem("Keep Right", "right")
        layout.addWidget(self.shadow_check, 4, 2, 1, 2)
        layout.addWidget(QLabel("Photo Focus"), 5, 0)
        layout.addWidget(self.focal_combo, 5, 1, 1, 3)
        return group

    def build_watermark_group(self) -> QGroupBox:
        group = QGroupBox("5. Page Name / Watermark (Optional)")
        layout = QGridLayout(group)
        self.watermark_edit = QLineEdit()
        self.watermark_edit.setPlaceholderText("Example: Quiet Strength Daily")
        self.watermark_position_combo = QComboBox()
        self.watermark_position_combo.addItem("Top Left", "top-left")
        self.watermark_position_combo.addItem("Top Center", "top-center")
        self.watermark_position_combo.addItem("Top Right", "top-right")
        self.watermark_position_combo.addItem("Bottom Left", "bottom-left")
        self.watermark_position_combo.addItem("Bottom Center", "bottom-center")
        self.watermark_position_combo.addItem("Bottom Right", "bottom-right")
        self.watermark_color_button = ColorButton("#FFFFFF")
        layout.addWidget(QLabel("Page Name"), 0, 0)
        layout.addWidget(self.watermark_edit, 0, 1, 1, 3)
        layout.addWidget(QLabel("Position"), 1, 0)
        layout.addWidget(self.watermark_position_combo, 1, 1, 1, 2)
        layout.addWidget(self.watermark_color_button, 1, 3)
        return group

    def build_actions_group(self) -> QGroupBox:
        group = QGroupBox("6. Generate Images")
        layout = QVBoxLayout(group)

        row = QHBoxLayout()
        self.preview_button = QPushButton("Preview Random")
        self.preview_button.clicked.connect(self.preview_random)
        self.generate_button = QPushButton("Generate Batch")
        self.generate_button.setObjectName("primaryButton")
        self.generate_button.clicked.connect(self.start_generation)
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.setObjectName("dangerButton")
        self.cancel_button.setEnabled(False)
        self.cancel_button.clicked.connect(self.cancel_generation)
        row.addWidget(self.preview_button)
        row.addWidget(self.generate_button, 1)
        row.addWidget(self.cancel_button)
        layout.addLayout(row)

        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        layout.addWidget(self.progress_bar)
        return group

    def build_preview_panel(self) -> QWidget:
        panel = QFrame()
        panel.setObjectName("rightPanel")
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(14, 14, 14, 14)

        heading_row = QHBoxLayout()
        preview_title = QLabel("Image Preview")
        preview_title.setStyleSheet(
            "font-size: 15pt; font-weight: 700; color: #173A5E;"
        )
        self.open_output_button = QPushButton("Open Output Folder")
        self.open_output_button.setEnabled(False)
        self.open_output_button.clicked.connect(self.open_last_output)
        heading_row.addWidget(preview_title)
        heading_row.addStretch(1)
        heading_row.addWidget(self.open_output_button)
        layout.addLayout(heading_row)

        self.preview_label = PreviewLabel()
        layout.addWidget(self.preview_label, 1)

        log_label = QLabel("Activity Log")
        log_label.setStyleSheet("font-weight: 700; color: #173A5E;")
        layout.addWidget(log_label)
        self.log_edit = QTextEdit()
        self.log_edit.setReadOnly(True)
        self.log_edit.setMaximumHeight(145)
        self.log_edit.setPlaceholderText("Activity will appear here...")
        layout.addWidget(self.log_edit)
        return panel

    @staticmethod
    def make_spin(
        minimum: int,
        maximum: int,
        value: int,
        suffix: str = "",
    ) -> QSpinBox:
        spin = QSpinBox()
        spin.setRange(minimum, maximum)
        spin.setValue(value)
        if suffix:
            spin.setSuffix(f" {suffix}")
        return spin

    def append_log(self, message: str) -> None:
        self.log_edit.append(message)

    def choose_image_folder(self) -> None:
        start = self.image_folder_edit.text() or str(Path.home())
        folder = QFileDialog.getExistingDirectory(
            self, "Choose Image Folder", start
        )
        if not folder:
            return
        try:
            images = list_images(folder)
        except QuoteGeneratorError as exc:
            self.show_error(str(exc))
            return
        self.images = images
        display_folder = native_display_path(folder)
        self.image_folder_edit.setText(display_folder)
        self.append_log(
            f"[OK] Loaded {len(images)} images from {display_folder}"
        )
        self.refresh_summary()

    def choose_quote_file(self) -> None:
        start = self.quote_file_edit.text() or str(PROJECT_DIR)
        path, _ = QFileDialog.getOpenFileName(
            self,
            "Choose Quote File",
            start,
            "Quote files (*.txt *.csv *.docx);;Text (*.txt);;CSV (*.csv);;Word (*.docx)",
        )
        if not path:
            return
        try:
            quotes = load_quotes(path)
        except QuoteGeneratorError as exc:
            self.show_error(str(exc))
            return
        self.quotes = quotes
        self.quote_file_edit.setText(native_display_path(path))
        self.append_log(
            f"[OK] Loaded {len(quotes)} unique quotes from {Path(path).name}"
        )
        self.refresh_summary()

    def choose_output_folder(self) -> None:
        start = self.output_folder_edit.text() or str(
            Path.home() / "Pictures"
        )
        folder = QFileDialog.getExistingDirectory(
            self, "Choose Output Folder", start
        )
        if folder:
            self.output_folder_edit.setText(native_display_path(folder))

    def choose_font(self) -> None:
        start = self.font_edit.text() or "C:/Windows/Fonts"
        path, _ = QFileDialog.getOpenFileName(
            self,
            "Choose Font",
            start,
            "Font files (*.ttf *.otf *.ttc)",
        )
        if path:
            self.font_edit.setText(path)

    def apply_size_preset(self) -> None:
        value = self.preset_combo.currentData()
        custom = value is None
        self.width_spin.setEnabled(custom)
        self.height_spin.setEnabled(custom)
        if value:
            self.width_spin.setValue(value[0])
            self.height_spin.setValue(value[1])

    def refresh_summary(self) -> None:
        image_count = len(self.images)
        quote_count = len(self.quotes)
        self.source_summary.setText(
            f"Images: {image_count:,}  |  Quotes: {quote_count:,}  |  "
            f"Unique pairs available: {min(image_count, quote_count):,}"
        )
        if image_count and quote_count:
            self.count_spin.setMaximum(max(10000, image_count, quote_count))

    def reload_typed_paths(self) -> None:
        image_folder = self.image_folder_edit.text().strip()
        quote_file = self.quote_file_edit.text().strip()
        if image_folder:
            self.images = list_images(image_folder)
        if quote_file:
            self.quotes = load_quotes(quote_file)
        self.refresh_summary()

    def current_render_settings(self) -> RenderSettings:
        return RenderSettings(
            width=self.width_spin.value(),
            height=self.height_spin.value(),
            output_format=self.format_combo.currentText(),
            font_path=self.font_edit.text().strip(),
            font_min_size=self.font_min_spin.value(),
            font_max_size=self.font_max_spin.value(),
            text_color=self.text_color_button.color,
            quote_position=self.position_combo.currentData(),
            vertical_position=self.vertical_slider.value(),
            safe_margin_percent=self.safe_margin_spin.value(),
            text_area_percent=self.text_area_spin.value(),
            add_quote_marks=self.quote_marks_check.isChecked(),
            background_style=self.background_style_combo.currentData(),
            darken_percent=self.darken_spin.value(),
            blur_radius=self.blur_spin.value(),
            box_enabled=self.box_check.isChecked(),
            box_style=self.box_style_combo.currentData(),
            box_color=self.box_color_button.color,
            box_opacity=self.box_opacity_spin.value(),
            shadow_enabled=self.shadow_check.isChecked(),
            watermark=self.watermark_edit.text().strip(),
            watermark_color=self.watermark_color_button.color,
            watermark_position=self.watermark_position_combo.currentData(),
            focal_point=self.focal_combo.currentData(),
        )

    def current_items(self, count: int | None = None) -> list[GenerationItem]:
        self.reload_typed_paths()
        return create_generation_items(
            self.images,
            self.quotes,
            count or self.count_spin.value(),
            random_images=self.random_images_check.isChecked(),
            random_quotes=self.random_quotes_check.isChecked(),
            avoid_repeat_images=self.no_repeat_images_check.isChecked(),
            avoid_repeat_quotes=self.no_repeat_quotes_check.isChecked(),
        )

    def preview_random(self) -> None:
        try:
            self.reload_typed_paths()
            items = create_generation_items(
                self.images,
                self.quotes,
                1,
                random_images=True,
                random_quotes=True,
                avoid_repeat_images=True,
                avoid_repeat_quotes=True,
            )
            rendered = render_quote_image(
                items[0].image_path,
                items[0].quote,
                self.current_render_settings(),
            )
            pixmap = pil_image_to_qpixmap(rendered)
            self.preview_label.set_source_pixmap(pixmap)
            self.append_log(
                f"Preview: {items[0].image_path.name} + {items[0].quote[:60]}..."
            )
        except Exception as exc:
            self.show_error(str(exc))

    def start_generation(self) -> None:
        if self.worker and self.worker.isRunning():
            return
        output_folder = self.output_folder_edit.text().strip()
        if not output_folder:
            self.show_error("Please select an Output Folder first.")
            return
        try:
            items = self.current_items()
            settings = self.current_render_settings()
            settings.validate()
        except Exception as exc:
            self.show_error(str(exc))
            return

        self.save_preferences()
        self.progress_bar.setRange(0, len(items))
        self.progress_bar.setValue(0)
        self.set_busy(True)
        self.append_log(f"[START] Starting batch: {len(items)} images")
        self.worker = GenerationWorker(items, output_folder, settings, self)
        self.worker.progress.connect(self.on_generation_progress)
        self.worker.completed.connect(self.on_generation_completed)
        self.worker.failed.connect(self.on_generation_failed)
        self.worker.start()

    def cancel_generation(self) -> None:
        if self.worker and self.worker.isRunning():
            self.worker.cancel()
            self.cancel_button.setEnabled(False)
            self.append_log("Cancel requested. Finishing the current image...")

    def on_generation_progress(
        self, current: int, total: int, output_path_value: str
    ) -> None:
        output_path = Path(output_path_value)
        filename = output_path.name
        self.progress_bar.setMaximum(total)
        self.progress_bar.setValue(current)
        self.progress_bar.setFormat(f"{current}/{total} - {filename}")
        pixmap = QPixmap(str(output_path))
        if not pixmap.isNull():
            self.preview_label.set_source_pixmap(pixmap)
        self.append_log(f"[{current}/{total}] Generated: {filename}")

    def on_generation_completed(
        self, folder: str, count: int, canceled: bool
    ) -> None:
        self.set_busy(False)
        self.last_output_folder = folder
        self.open_output_button.setEnabled(True)
        if canceled:
            self.append_log(
                f"[CANCELED] Stopped after {count} images. Saved in: {folder}"
            )
        else:
            self.append_log(f"[OK] Completed {count} images. Saved in: {folder}")
            QMessageBox.information(
                self,
                "Generation Complete",
                f"Successfully generated {count} images.\n\n{folder}",
            )
        self.worker = None

    def on_generation_failed(self, message: str) -> None:
        self.set_busy(False)
        self.worker = None
        self.append_log(f"[ERROR] {message}")
        self.show_error(message)

    def set_busy(self, busy: bool) -> None:
        self.generate_button.setEnabled(not busy)
        self.preview_button.setEnabled(not busy)
        self.cancel_button.setEnabled(busy)

    def open_last_output(self) -> None:
        folder = self.last_output_folder
        if not folder or not Path(folder).is_dir():
            self.show_error("The Output Folder is not available.")
            return
        if sys.platform.startswith("win"):
            os.startfile(folder)  # type: ignore[attr-defined]
        else:
            QDesktopServices.openUrl(QUrl.fromLocalFile(folder))

    def show_error(self, message: str) -> None:
        QMessageBox.warning(self, "Unable to Continue", message)

    def save_preferences(self) -> None:
        values = {
            "image_folder": native_display_path(self.image_folder_edit.text()),
            "quote_file": native_display_path(self.quote_file_edit.text()),
            "output_folder": native_display_path(self.output_folder_edit.text()),
            "font_path": self.font_edit.text(),
            "preset_index": self.preset_combo.currentIndex(),
            "width": self.width_spin.value(),
            "height": self.height_spin.value(),
            "format": self.format_combo.currentText(),
            "position_index": self.position_combo.currentIndex(),
            "vertical": self.vertical_slider.value(),
            "font_min": self.font_min_spin.value(),
            "font_max": self.font_max_spin.value(),
            "safe_margin": self.safe_margin_spin.value(),
            "text_area": self.text_area_spin.value(),
            "background_style": self.background_style_combo.currentData(),
            "darken": self.darken_spin.value(),
            "blur": self.blur_spin.value(),
            "box_enabled": self.box_check.isChecked(),
            "box_style": self.box_style_combo.currentData(),
            "box_opacity": self.box_opacity_spin.value(),
            "quote_marks": self.quote_marks_check.isChecked(),
            "text_shadow": self.shadow_check.isChecked(),
            "focal_point": self.focal_combo.currentData(),
            "watermark": self.watermark_edit.text(),
            "watermark_position": self.watermark_position_combo.currentData(),
            "text_color": self.text_color_button.color,
            "box_color": self.box_color_button.color,
            "watermark_color": self.watermark_color_button.color,
        }
        for key, value in values.items():
            self.settings_store.setValue(key, value)

    def load_preferences(self) -> None:
        sample_file = PROJECT_DIR / "sample_quotes.txt"
        default_output = Path.home() / "Pictures" / "Quote Image Generator"
        default_output.mkdir(parents=True, exist_ok=True)

        self.image_folder_edit.setText(
            native_display_path(
                read_preference(self.settings_store, "image_folder", "")
            )
        )
        self.quote_file_edit.setText(
            native_display_path(
                read_preference(
                    self.settings_store,
                    "quote_file",
                    str(sample_file),
                )
            )
        )
        self.output_folder_edit.setText(
            native_display_path(
                read_preference(
                    self.settings_store,
                    "output_folder",
                    str(default_output),
                )
            )
        )
        self.font_edit.setText(
            read_preference(self.settings_store, "font_path", "")
        )
        self.preset_combo.setCurrentIndex(
            read_preference(self.settings_store, "preset_index", 0)
        )
        self.width_spin.setValue(
            read_preference(self.settings_store, "width", 1440)
        )
        self.height_spin.setValue(
            read_preference(self.settings_store, "height", 1800)
        )
        self.format_combo.setCurrentText(
            read_preference(self.settings_store, "format", "JPEG")
        )
        self.position_combo.setCurrentIndex(
            read_preference(self.settings_store, "position_index", 0)
        )
        self.vertical_slider.setValue(
            read_preference(self.settings_store, "vertical", 50)
        )
        self.font_min_spin.setValue(
            read_preference(self.settings_store, "font_min", 42)
        )
        self.font_max_spin.setValue(
            read_preference(self.settings_store, "font_max", 104)
        )
        self.safe_margin_spin.setValue(
            read_preference(self.settings_store, "safe_margin", 8)
        )
        self.text_area_spin.setValue(
            read_preference(self.settings_store, "text_area", 48)
        )
        background_style = read_preference(
            self.settings_store,
            "background_style",
            "classic",
        )
        background_style_index = self.background_style_combo.findData(
            background_style
        )
        self.background_style_combo.setCurrentIndex(
            max(0, background_style_index)
        )
        self.darken_spin.setValue(
            read_preference(self.settings_store, "darken", 22)
        )
        self.blur_spin.setValue(
            read_preference(self.settings_store, "blur", 0.0)
        )
        self.box_check.setChecked(
            read_preference(self.settings_store, "box_enabled", True)
        )
        box_style = read_preference(
            self.settings_store,
            "box_style",
            "translucent",
        )
        box_style_index = self.box_style_combo.findData(box_style)
        self.box_style_combo.setCurrentIndex(max(0, box_style_index))
        self.box_opacity_spin.setValue(
            read_preference(self.settings_store, "box_opacity", 105)
        )
        self.quote_marks_check.setChecked(
            read_preference(self.settings_store, "quote_marks", True)
        )
        self.shadow_check.setChecked(
            read_preference(self.settings_store, "text_shadow", True)
        )
        focal_point = read_preference(
            self.settings_store,
            "focal_point",
            "center",
        )
        focal_index = self.focal_combo.findData(focal_point)
        self.focal_combo.setCurrentIndex(max(0, focal_index))
        self.watermark_edit.setText(
            read_preference(self.settings_store, "watermark", "")
        )
        saved_watermark_position = read_preference(
            self.settings_store,
            "watermark_position",
            "bottom-right",
        )
        legacy_watermark_positions = {
            "0": "bottom-right",
            "1": "bottom-center",
            "2": "bottom-left",
        }
        saved_watermark_position = legacy_watermark_positions.get(
            saved_watermark_position,
            saved_watermark_position,
        )
        watermark_position_index = self.watermark_position_combo.findData(
            saved_watermark_position
        )
        if watermark_position_index < 0:
            watermark_position_index = self.watermark_position_combo.findData(
                "bottom-right"
        )
        self.watermark_position_combo.setCurrentIndex(watermark_position_index)
        self.text_color_button.set_color(
            read_preference(self.settings_store, "text_color", "#FFFFFF")
        )
        self.box_color_button.set_color(
            read_preference(self.settings_store, "box_color", "#06111F")
        )
        self.watermark_color_button.set_color(
            read_preference(self.settings_store, "watermark_color", "#FFFFFF")
        )
        self.apply_size_preset()

        quote_path = Path(self.quote_file_edit.text())
        if quote_path.is_file():
            try:
                self.quotes = load_quotes(quote_path)
            except QuoteGeneratorError:
                self.quotes = []
        image_path = Path(self.image_folder_edit.text())
        if image_path.is_dir():
            try:
                self.images = list_images(image_path)
            except QuoteGeneratorError:
                self.images = []

    def closeEvent(self, event):
        if self.worker and self.worker.isRunning():
            answer = QMessageBox.question(
                self,
                "Generation in Progress",
                "Images are still being generated. Stop generation and close "
                "the application?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No,
            )
            if answer != QMessageBox.Yes:
                event.ignore()
                return
            self.worker.cancel()
            self.worker.wait(2500)
        self.save_preferences()
        event.accept()


def main() -> int:
    if hasattr(Qt, "AA_EnableHighDpiScaling"):
        QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    if hasattr(Qt, "AA_UseHighDpiPixmaps"):
        QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
    app = QApplication(sys.argv)
    app.setApplicationName(APP_NAME)
    app.setOrganizationName("PuVinTools")
    if APP_ICON_PATH.is_file():
        app.setWindowIcon(QIcon(str(APP_ICON_PATH)))
    apply_ui_font(app)
    app.setStyleSheet(STYLE_SHEET)
    window = MainWindow()
    window.show()
    return app.exec_()


if __name__ == "__main__":
    raise SystemExit(main())
