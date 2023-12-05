import json
import logging
import os

from tools.QRcode_decode import decode_from_path
from tools.logging_utils import log_set
from tools.retry_tools import task_retry
from tools.tax_url_decode import set_driver, add_tax_params, fix_yzm, get_fp_info, download_PDF

BASE_URL = "https://inv-veri.chinatax.gov.cn/"


@task_retry(max_retry_count=3, time_interval=2, max_timeout=150)
def decode_URL(invoice_msg: dict):
    logging.info(f"invoice_msg: {invoice_msg}")
    # open URL
    browser = set_driver(headless_mode=False, auto_detach=True)
    browser.get(BASE_URL)
    browser.maximize_window()

    # 填充参数并获取验证码
    add_tax_params(browser, invoice_msg)

    # 打码
    fix_yzm(browser)

    # 提取发票截图及信息
    info_dict = get_fp_info(browser, invoice_msg)
    os.makedirs("data/json", exist_ok=True)
    with open(os.path.join("data/json", info_dict["filename"]), mode="w", encoding="utf-8") as f:
        json.dump(info_dict, f, sort_keys=True, indent=4)

    # 下载版式PDF
    download_PDF(browser, os.path.join("data/pdf", info_dict["filename"].replace(".json", ".pdf")))


if __name__ == '__main__':
    log_set(logging.INFO)

    decode_URL(decode_from_path("examples/发票/")[2])
    # for index, msg_dict in enumerate(decode_from_path("examples/发票/")):
    #     decode_URL(msg_dict)
    #     if index >= 2:
    #         break
