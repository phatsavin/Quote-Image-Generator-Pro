Quote Image Generator Pro

A Windows desktop application for automatically creating professional quote images.



Features and Version History

Version 1.7.0: Displays each generated image in the live preview during batch generation

Version 1.6.0: Added Double Line Frame - No Fill

Version 1.5.0: Added Corner Quote Frame - No Fill and Windows-style \ path display

Version 1.4.0: Added Decorative Quote Frame - No Fill

Version 1.3.3: Made the Luxury Noir 2 border thicker and more visible

Version 1.3.2: Added an isolated settings profile and a version-aware launcher

Version 1.3.1: Fixed a startup error caused by legacy watermark preferences

Version 1.3.0: Added Luxury Noir 2, which preserves the original image colors, and added an application icon

Version 1.2.0: Added professional background styles and top watermark positions

Version 1.1.0: Added compatibility with PyQt5 and Pillow 12 or later

Selects background images randomly or sequentially from a folder

Reads quotes from .txt, .csv, and .docx files

Supports Word quote collections that use the Quote Item style

Automatically wraps and resizes text to fit the image

Provides a preview before generation

Updates the live preview with each image during batch generation

Generates multiple images in a batch

Supports Facebook 4:5, Square 1:1, Story 9:16, and custom dimensions

Supports left, center, and right quote alignment

Includes background darkening and blur, text shadows, and translucent boxes

Offers quote backgrounds including Translucent Box, Decorative Quote Frame - No Fill,Corner Quote Frame - No Fill, and Double Line Frame - No Fill

Displays Image Folder, Quote File, and Output Folder paths with Windows-style \ separators

Includes Classic Photo, TikTok Blur Frame, TikTok Glass Gradient,Cinematic Vignette, Luxury Noir, and Luxury Noir 2 - Original Color background styles

Displays an icon in the title bar, Windows taskbar, and EXE file

Supports an optional page name or watermark

Offers Top Left, Top Center, Top Right, Bottom Left, Bottom Center, and Bottom Right watermark positions

Prevents duplicate images or quotes within a batch

Creates generation_log.csv to record the images and quotes used

Supports Khmer OS Battambang or Kantumruy Pro for the user interface on Windows

1. Requirements

Windows 10 or Windows 11

Python 3.11 or later

An internet connection for the initial package installation

Download Python from https://www.python.org/downloads/.

During installation, select Add Python to PATH.

2. Launching the Application

For Version 1.7.0, double-click:

START_HERE_v1.7.0.bat

This launcher runs run_windows.bat, which:

Creates the .venv virtual environment

Installs PyQt5, Pillow, and python-docx

Launches the application

The first launch may take a few minutes while the required packages are installed. Future launches will be faster.

3. How to Use

Click Browse Folder and select the folder containing your background images.

Click Browse File and select a TXT, CSV, or DOCX file containing your quotes.

Click Browse Output and select the destination folder.

Choose an output size. For the Facebook Feed, 1440 × 1800 (4:5) is recommended.

Configure the font, quote position, text color, darkening, and watermark.

Choose a Background Style in the Background and Readability section.

Click Preview Random to review a sample.

Set the number of images, then click Generate Batch.

The application creates a new folder with a name such as:

Quote_Images_20260723_153000

4. Quote File Formats

TXT

Place one quote on each line:

Good morning; your next choice still has power.
Protecting your peace is productive.
My wallet has entered power-saving mode.

Numbering and outer quotation marks are removed automatically:

1. "First quote."
2. "Second quote."

CSV

Place each quote in the first column. You may include a Quote header:

Quote
"Good morning; your next choice still has power."
"Protecting your peace is productive."

DOCX

The application works best with paragraphs that use the Quote Item style. Previously created Category 1–12 Word quote collections can be selected and used directly.

5. Preparing the Image Folder

The application supports:

JPG, JPEG, PNG, WEBP, BMP, TIF, TIFF

For a left-aligned quote, use an image with the subject on the right and negative space on the left.

Example:

Facebook_Backgrounds/
├── morning_001.jpg
├── morning_002.jpg
├── night_001.jpg
├── healing_001.png
└── humor_001.webp

6. Fonts

The application automatically searches for Georgia, Calibri, or Arial in the Windows Fonts folder. Click Browse Font to use another .ttf or .otf font.

Recommended fonts for English quotes:

Georgia Bold

Playfair Display Bold

Libre Baskerville Bold

Montserrat SemiBold

7. Building the EXE

After successfully launching run_windows.bat, double-click:

build_exe_windows.bat

The EXE will be created at:

dist\QuoteImageGeneratorPro.exe

The build script automatically embeds assets\QuoteImageGeneratorPro.ico in the EXE.

If you previously built an older version, delete only the old build and dist folders and the old QuoteImageGeneratorPro.spec file. Then run build_exe_windows.bat again.

8. Testing the Core Engine

Run the following commands in Command Prompt:

cd Quote_Image_Generator_Pro
.venv\Scripts\python.exe -m unittest discover -s tests -v

9. Facebook Content Monetization Notes

Use only images that you have permission to use.

Use original quotes and avoid copying content from other pages.

Avoid generating too many nearly identical images by changing only the quote.

Vary the scene, color, crop, and composition.

Review the preview before generating a large batch.

Do not use brand logos or celebrity likenesses without permission.

10. Important Files

app.py                 Professional PyQt5 user interface
quote_engine.py        Image and quote processing engine
sample_quotes.txt      Sample quotes for testing
requirements.txt       Required Python packages
run_windows.bat        Installs dependencies and launches the application
START_HERE_v1.7.0.bat  Confirms and launches the correct application version
build_exe_windows.bat  Builds the Windows EXE
assets/                Application icons for the title bar, taskbar, and EXE
tests/                 Automated tests
![Quote Image Generator Pro Screenshot](https://raw.githubusercontent.com/phatsavin/Quote-Image-Generator-Pro/main/Screenshot%202026-07-23%20201734.png)
