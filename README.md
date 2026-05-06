# Image to Word Converter

This is an application that extracts text from images and saves it as a Word document while keeping the formatting. It detects things like bold text, italic text, and paragraph alignment from the image and applies them in the output file.

Built as the Phase 1 project for PPIT at FAST NUCES.

## What It Does

The app takes an image of a document (like a scanned page or a screenshot) and converts it into an editable Word file. It goes through the following steps:

1. Preprocesses the image to clean it up (removes noise, fixes rotation, improves contrast)
2. Runs OCR using Tesseract to extract the text
3. Analyzes the image to detect bold, italic, font size, and alignment
4. Generates a .docx file with all the detected formatting applied

There are two versions of this app. A desktop version built with Tkinter and a web version built with Streamlit. The web version can be deployed online so anyone can use it through a browser.

## How to Set It Up

### Step 1: Install Python

You need Python 3.8 or higher. You can download it from https://www.python.org/downloads/

### Step 2: Install Tesseract OCR

Tesseract is the OCR engine that reads text from images. Download and install it from here:

https://github.com/UB-Mannheim/tesseract/wiki

Install it to the default location (`C:\Program Files\Tesseract-OCR`) or add it to your system PATH.

### Step 3: Install Python Libraries

Open a terminal in the project folder and run:

```
pip install -r requirements.txt
```

## How to Run

### Desktop Version (Tkinter)

```
python image_to_word_converter.py
```

This opens a desktop window where you can browse for an image, convert it, and save the output as a Word file.

### Web Version (Streamlit)

```
streamlit run app.py
```

This starts a local web server. Open the link shown in the terminal (usually http://localhost:8501) to use the app in your browser. You can upload an image, convert it, and download the Word file directly.

### Steps to Convert

1. Select or upload your image file
2. Toggle preprocessing and formatting detection on or off if needed
3. Pick a language (default is English)
4. Click Convert to Word
5. Save or download the output .docx file

## Project Files

```
image_to_word_converter.py    Desktop app with Tkinter GUI
app.py                        Web app with Streamlit
image_preprocessor.py         Cleans up the image before OCR
ocr_engine.py                 Handles text extraction using Tesseract
formatting_detector.py        Detects bold, italic, font size, and alignment
docx_generator.py             Creates the Word document with formatting
requirements.txt              Python libraries needed
packages.txt                  System packages for Streamlit Cloud deployment
.streamlit/config.toml        Streamlit theme and settings
```

## How Each Module Works

### image_preprocessor.py

Takes the input image and prepares it for OCR. It converts the image to grayscale, removes noise, applies adaptive thresholding, fixes any tilt or rotation, and enhances sharpness and contrast.

### ocr_engine.py

Uses Tesseract OCR to extract text from the preprocessed image. It gets the text along with bounding boxes, confidence scores, and information about which word belongs to which line and paragraph.

### formatting_detector.py

Looks at each word in the image and checks if it is bold (by measuring stroke thickness) or italic (by measuring the slant angle). It also estimates font sizes and figures out paragraph alignment (left, center, right, or justified) by analyzing the margins.

### docx_generator.py

Takes all the extracted text and formatting data and creates a proper Word document. It sets the font, applies bold and italic where detected, and uses the correct paragraph alignment.

## Supported Image Formats

JPG, JPEG, PNG, BMP, TIFF

## Deployment

The web version (app.py) can be deployed to Streamlit Cloud so you get a shareable link. Here is how:

1. Push this project to a GitHub repository
2. Go to https://share.streamlit.io and sign in with your GitHub account
3. Click New App and select your repository
4. Set the main file path to `app.py`
5. Click Deploy

After a few minutes you will get a public link like `https://yourname-image-to-word-converter.streamlit.app` that you can share with anyone.

The `packages.txt` file in this project tells Streamlit Cloud to install Tesseract OCR on the server automatically.

## Limitations

This is an MVP (Phase 1), so it has some limitations:

- Works best with single page documents
- Works best with clear, well scanned or high quality images
- Primarily supports English (other languages need Tesseract language packs)
- Complex layouts like multi column pages or tables may not be handled well

## Future Enhancements (Phase 2)

- Multi page document support
- Table structure preservation
- Equation detection and conversion
- Better handling of complex layouts

## Team

- Ayyan Ahmad (i220540)
- Zain Raza (i220520)

## License

Academic Project, FAST NUCES
