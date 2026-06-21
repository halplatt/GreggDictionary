cd D:\HostGatorFiles\public_html\notes\extractor
pip install pymupdf pytesseract pillow opencv-python numpy
python extract_shorthand.py "5000_shorthand.pdf" out_dir ^
    --tesseract-cmd "C:\Program Files\Tesseract-OCR\tesseract.exe" ^
    --dpi 300 --start 3 --end 71
