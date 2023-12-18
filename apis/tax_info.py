import os

from flask import Blueprint, request

from apis.API_utils import api_return
from tools.QRcode_decode import decode_single_path

info_bp = Blueprint("tax_info", __name__)


@info_bp.route("/upload", methods=["POST"])
def tax_upload():
    """接受发票文件并解析"""
    file = request.files.to_dict()["file"]
    os.makedirs("cache/tax", exist_ok=True)
    save_path = os.path.join("cache/tax", file.filename)
    file.save(save_path)
    return api_return(code=200, status="success", data={"save_path": save_path, "data": decode_single_path(save_path)})
