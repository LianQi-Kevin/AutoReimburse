import glob
import os
from typing import Dict

import cv2
import fitz
import numpy as np

TAX_TYPE = {
    "10": "增值税电子普通发票",
    "04": "增值税普通发票",
    "01": "增值税专用发票",
}

CV2_ALLOW = [".png", ".jpg", ".jpeg", ".jpe", ".jp2", ".bmp", ".dib", ".webp",
             ".pbm", ".pgm", ".ppm", ".pxm", ".pnm", ".tif", ".tiff"]


def PDF2PNG(pdf_path: str) -> bytes:
    """Convert PDF to PNG(raw)"""
    pdf_doc = fitz.open(pdf_path)
    pdf_page = pdf_doc.load_page(0)
    pdf_pix = pdf_page.get_pixmap(matrix=fitz.Matrix(5, 5), alpha=False)
    return pdf_pix.tobytes(output="png", jpg_quality=98)


def decode_QRcode(png_raw: bytes) -> str:
    """Decode QRcode from IMG(raw)"""
    cv2_img = cv2.imdecode(np.frombuffer(png_raw, np.uint8), cv2.IMREAD_ANYCOLOR)
    detector = cv2.wechat_qrcode_WeChatQRCode()
    barcodes, _ = detector.detectAndDecode(cv2_img)
    return barcodes[0]


def decode_single_path(decode_path: str) -> Dict[str, str]:
    """Decode QRcode in single file"""
    try:
        if os.path.splitext(decode_path)[1] == ".pdf":
            img_raw = PDF2PNG(decode_path)
        elif os.path.splitext(decode_path)[1] in CV2_ALLOW:
            with open(decode_path, "rb") as f:
                img_raw = f.read()
        else:
            raise TypeError("Unsupported file type!")
        code_data = decode_QRcode(img_raw).split(",")
        body = {"filename": os.path.basename(decode_path),
                "type": code_data[1],
                "type_zh": TAX_TYPE[code_data[1]] if code_data[1] in ["10", "04", "01"] else "未知类型",
                "code": code_data[2], "id": code_data[3], "money": code_data[4],
                "date": code_data[5], "verify": code_data[6]}
        return body
    except TypeError:
        return {"filename": "", "type": "", "type_zh": "未知类型", "code": "", "id": "", "money": "", "date": "", "verify": ""}


def decode_from_path(path: str) -> list:
    """Decode QRcode in folder
    暂时仅支持PDF和PNG格式
    """
    result = []
    # decode PDF QRcode
    for decode_path in glob.glob(os.path.join(path, f"*{['.pdf'] + CV2_ALLOW}")):
        result.append(decode_single_path(decode_path))
    return result


if __name__ == '__main__':
    decode_from_path("../examples/发票/")
