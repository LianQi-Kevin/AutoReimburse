import glob
import io
import os

import fitz
from PIL import Image
from pyzbar.pyzbar import decode


def PDF2PNG(pdf_path: str) -> bytes:
    """Convert PDF to PNG(raw)"""
    pdf_doc = fitz.open(pdf_path)
    pdf_page = pdf_doc.load_page(0)
    pdf_pix = pdf_page.get_pixmap(matrix=fitz.Matrix(5, 5), alpha=False)
    return pdf_pix.tobytes(output="png", jpg_quality=98)


def decode_QRcode(png_raw: bytes) -> str:
    """Decode QRcode from PNG(raw)"""
    return decode(Image.open(io.BytesIO(png_raw)))[0].data.decode("UTF-8")


def decode_from_path(path: str) -> list:
    """Decode QRcode in folder
    暂时仅支持PDF和PNG格式
    """
    result = []

    # decode PDF QRcode
    for decode_path in glob.glob(os.path.join(path, "*[pdf, png]")):
        if os.path.splitext(decode_path)[1] == ".pdf":
            code_data = decode_QRcode(PDF2PNG(decode_path)).split(",")
        elif os.path.splitext(decode_path)[1] == ".png":
            with open(decode_path, "rb") as f:
                code_data = decode_QRcode(f.read()).split(",")
                f.close()
        body = {"filename": os.path.basename(decode_path), "invoice_type": code_data[1], "invoice_code": code_data[2],
                "invoice_id": code_data[3], "invoice_amount": code_data[4], "invoice_data": code_data[5],
                "invoice_verify": code_data[6]}
        print(body)
        result.append(body)
    return result


if __name__ == '__main__':
    decode_from_path("../examples/发票/")
