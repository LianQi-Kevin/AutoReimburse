import logging
from typing import Tuple

from flask import jsonify


def api_return(code: int, status: str, message: str = None, data: dict = None) -> Tuple[jsonify, int]:
    """
    :param code: http status code
    :param status: success | error | fail
    :param message: if status in ["error", "fail"], give the reason
    :param data: if status == "success", data
    :return: jsonify(code, status, message, data), code
    """
    if status not in ["success", "error", "fail"]:
        raise ValueError(f'{status} must in ["success", "error", "fail"]')
    if status != "success" and message is None:
        raise ValueError(f"status not 'success', must give reason")
    logging.debug(f"code: {code}, status: {status}, message: {message}, data: {data}")
    return jsonify(code=code, status=status, message=message, data=data), code
