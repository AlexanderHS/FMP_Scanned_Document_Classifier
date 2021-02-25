#!/bin/bash
python3 -m venv venv
source venv/bin/activate
sudo apt-get update
sudo apt-get install poppler-utils libleptonica-dev tesseract-ocr libtesseract-dev -y
pip install pdf2image PyPDF2 pytesseract ntpath poppler-utils tesseract tesseract-ocr unidecode glob

# tesseract install here
# https://stackoverflow.com/a/52231794/5977682
