from pdfminer.high_level import extract_text as pdf_extract_text
import docx2txt
import pytesseract
from pdf2image import convert_from_path
from PIL import Image
import os
from typing import Optional
import signal

class TimeoutException(Exception):
    pass

def timeout_handler(signum, frame):
    raise TimeoutException("OCR operation timed out")

def extract_text_from_pdf(path: str, use_ocr_fallback: bool = True) -> str:
    text = pdf_extract_text(path)
    
    if use_ocr_fallback and len(text.strip()) < 100:
        print("Low text content detected, attempting OCR...")
        try:
            ocr_text = extract_text_from_pdf_with_ocr(path, timeout=60)
            
            if len(ocr_text.strip()) > len(text.strip()):
                print(f"OCR extracted {len(ocr_text)} chars (vs {len(text)} from direct extraction)")
                return ocr_text
        except TimeoutException:
            print("OCR timed out, using direct extraction")
        except Exception as e:
            print(f"OCR failed: {e}, using direct extraction")
    
    return text

def extract_text_from_pdf_with_ocr(path: str, timeout: int = 60) -> str:
    try:
        if os.name != 'nt':
            signal.signal(signal.SIGALRM, timeout_handler)
            signal.alarm(timeout)
        
        images = convert_from_path(path, dpi=300)
        
        text_parts = []
        for i, image in enumerate(images):
            print(f"OCR processing page {i+1}/{len(images)}...")
            page_text = pytesseract.image_to_string(image, lang='eng')
            text_parts.append(page_text)
        
        if os.name != 'nt':
            signal.alarm(0)
        
        return "\n\n".join(text_parts)
    
    except TimeoutException:
        raise
    except Exception as e:
        print(f"OCR failed: {e}")
        return ""
    finally:
        if os.name != 'nt':
            signal.alarm(0)

def extract_text_from_image(path: str) -> str:
    try:
        image = Image.open(path)
        text = pytesseract.image_to_string(image, lang='eng')
        return text
    except Exception as e:
        print(f"Image OCR failed: {e}")
        return ""

def extract_text_from_docx(path: str) -> str:
    return docx2txt.process(path)