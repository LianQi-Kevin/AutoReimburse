import hashlib
import base64


def calculate_md5(input_str: str) -> str:
    """Calculate md5 hash of input string"""
    md5_hash = hashlib.md5()
    md5_hash.update(input_str.encode('utf-8'))
    return md5_hash.hexdigest()


def image_to_base64(img_path: str) -> str:
    """Convert image to base64 string"""
    with open(img_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')
