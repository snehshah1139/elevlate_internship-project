import os
import re

def extract_resume_text(filepath):
    ext = os.path.splitext(filepath)[1].lower()
    if ext == '.pdf':
        return extract_pdf_text(filepath)
    elif ext == '.docx':
        return extract_docx_text(filepath)
    elif ext == '.doc':
        # Optional: Uncomment if you have textract installed
        # return extract_doc_text(filepath)
        raise NotImplementedError("DOC extraction requires textract. Please use PDF or DOCX.")
    else:
        raise ValueError("Unsupported file format: " + ext)

def extract_pdf_text(filepath):
    try:
        import pdfplumber
    except ImportError:
        raise ImportError("Please install pdfplumber: pip install pdfplumber")
    text = ""
    try:
        with pdfplumber.open(filepath) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
    except Exception:
        text = ""
    # If no text found, try OCR
    if not text.strip():
        try:
            from pdf2image import convert_from_path
            import pytesseract
        except ImportError:
            raise ImportError("Please install pdf2image and pytesseract for OCR support.")
        try:
            images = convert_from_path(filepath)
            ocr_text = ""
            for img in images:
                ocr_text += pytesseract.image_to_string(img)
            return ocr_text
        except Exception:
            return ""
    return text

def extract_docx_text(filepath):
    try:
        import docx
    except ImportError:
        raise ImportError("Please install python-docx: pip install python-docx")
    try:
        doc = docx.Document(filepath)
        text = "\n".join([para.text for para in doc.paragraphs])
        return text
    except Exception:
        return ""

# Optional: DOC support with textract
# def extract_doc_text(filepath):
#     try:
#         import textract
#     except ImportError:
#         raise ImportError("Please install textract: pip install textract")
#     try:
#         text = textract.process(filepath)
#         return text.decode('utf-8')
#     except Exception:
#         return ""

def clean_text(text):
    text = text.lower()
    text = re.sub(r'\s+', ' ', text)
    text = re.sub(r'[^\x20-\x7E]', '', text)
    return text.strip()