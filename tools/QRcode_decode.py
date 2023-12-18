import glob
import io
import os
from typing import Dict

import fitz
from PIL import Image
from pyzbar.pyzbar import decode

TAX_TYPE = {
    "10": "增值税电子普通发票",
    "04": "增值税普通发票",
    "01": "增值税专用发票",
}


def PDF2PNG(pdf_path: str) -> bytes:
    """Convert PDF to PNG(raw)"""
    pdf_doc = fitz.open(pdf_path)
    pdf_page = pdf_doc.load_page(0)
    pdf_pix = pdf_page.get_pixmap(matrix=fitz.Matrix(5, 5), alpha=False)
    return pdf_pix.tobytes(output="png", jpg_quality=98)


def decode_QRcode(png_raw: bytes) -> str:
    """Decode QRcode from PNG(raw)"""
    return decode(Image.open(io.BytesIO(png_raw)))[0].data.decode("UTF-8")


def decode_single_path(decode_path: str) -> Dict[str, str]:
    """Decode QRcode in single file"""
    if os.path.splitext(decode_path)[1] == ".pdf":
        code_data = decode_QRcode(PDF2PNG(decode_path)).split(",")
    elif os.path.splitext(decode_path)[1] == ".png":
        with open(decode_path, "rb") as f:
            code_data = decode_QRcode(f.read()).split(",")
            f.close()
    body = {"filename": os.path.basename(decode_path),
            "type": TAX_TYPE[code_data[1]] if code_data[1] in ["10", "04", "01"] else "未知类型",
            "code": code_data[2], "id": code_data[3], "money": code_data[4],
            "date": code_data[5], "verify": code_data[6]}
    return body


def decode_from_path(path: str) -> list:
    """Decode QRcode in folder
    暂时仅支持PDF和PNG格式
    """
    result = []

    # decode PDF QRcode
    for decode_path in glob.glob(os.path.join(path, "*[pdf, png]")):
        result.append(decode_single_path(decode_path))
    return result


if __name__ == '__main__':
    decode_from_path("../examples/发票/")
