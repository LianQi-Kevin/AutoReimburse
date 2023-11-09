import json
import logging

import requests

from config import username, password, softid, softkey
from tools.logging_utils import log_set
from tools.utils import calculate_md5, image_to_base64

IMG_DETECT_URL = "http://upload.chaojiying.net/Upload/Processing.php"
WRONG_REPORT_URL = "http://upload.chaojiying.net/Upload/Report.php"
SCORE_QUERY_URL = "http://upload.chaojiying.net/Upload/GetScore.php"
# TYPE_ID = 1902
TYPE_ID = 5000

log_set(logging.DEBUG)


def img_detect(img_path: str):
    """验证码识别"""
    # create requests body
    body = json.dumps({"user": username, "pass2": calculate_md5(password), "softid": softid, "codetype": TYPE_ID,
                       "file_base64": image_to_base64(img_path)})
    headers = {"Content-Type": "application/json"}

    # request
    response = requests.request("POST", IMG_DETECT_URL, headers=headers, data=body)
    logging.debug(response.status_code)

    # response verify
    response_data = json.loads(response.text)
    logging.debug(f"response data: {response_data}")
    # verify response
    if response_data['err_no'] == 0:
        data_md5 = calculate_md5(f"{softid},{softkey},{response_data['pic_id']},{response_data['pic_str']}")
        if data_md5 != response_data['md5']:
            logging.error("response data md5 verify failed")
        else:
            logging.info(f"detect ans: {response_data['pic_str']}")
    else:
        logging.error(f"error message: {response_data['err_str']}")

    return response_data


def get_score():
    """查询超级鹰题分余额"""
    body = json.dumps({"user": username, "pass2": calculate_md5(password), })
    headers = {"Content-Type": "application/json"}
    response = requests.request("POST", SCORE_QUERY_URL, headers=headers, data=body)
    response_data = json.loads(response.text)
    logging.debug(f"response data: {response_data}")
    if response_data['err_no'] == 0:
        logging.info(f"query score: {response_data['tifen']}")
    else:
        logging.error(f"error message: {response_data['err_str']}")


def wrong_report(pic_id: str):
    """验证码错误回报"""
    body = json.dumps({"user": username, "pass2": calculate_md5(password), "id": pic_id, "softid": softid})
    headers = {"Content-Type": "application/json"}
    response = requests.request("POST", WRONG_REPORT_URL, headers=headers, data=body)
    response_data = json.loads(response.text)
    logging.debug(f"response data: {response_data}")


if __name__ == '__main__':
    img_detect("../examples/verify_codes/black.png")
    img_detect("../examples/verify_codes/black_write.png")
    get_score()
