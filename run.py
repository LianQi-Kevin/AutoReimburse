import logging

from tools.QRcode_decode import decode_from_path
from tools.logging_utils import log_set
from tools.tax_url_decode import get_verify_img

if __name__ == '__main__':
    log_set(logging.INFO)

    for index, msg_dict in enumerate(decode_from_path("examples/发票/")):
        get_verify_img(msg_dict)
