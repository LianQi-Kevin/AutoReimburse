import os
import hashlib
import base64


def calculate_md5(input_str: str) -> str:
    """Calculate md5 hash of input string"""
    md5_hash = hashlib.md5()
    md5_hash.update(input_str.encode('utf-8'))
    return md5_hash.hexdigest()


def image_raw_to_base64(img_raw: bytes) -> str:
    """Convert image to base64 string"""
    return base64.b64encode(img_raw).decode('utf-8')


def image_to_base64(img_path: str) -> str:
    """Convert image to base64 string"""
    with open(img_path, "rb") as image_file:
        return image_raw_to_base64(image_file.read())


def base64_to_image_raw(base64_str: str) -> bytes:
    """Convert base64 string to image raw"""
    return base64.b64decode(base64_str)


def base64_to_image(base64_str: str, img_path: str) -> None:
    """Convert base64 string to image"""
    os.makedirs(os.path.dirname(img_path), exist_ok=True) if os.path.dirname(img_path) != "" else None
    with open(img_path, "wb") as image_file:
        image_file.write(base64_to_image_raw(base64_str))
