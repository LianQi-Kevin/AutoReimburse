from typing import Tuple

import cv2
import numpy as np


def cv_show(img):
    cv2.imshow("img", img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()


def __get_threshold(color: str = "black") -> Tuple[np.ndarray, np.ndarray]:
    """
    获取阈值
    https://blog.csdn.net/qq_40456669/article/details/93375709
    :param color: black|grey|white|red|orange|yellow|green|cyan|blue|purple
    """
    color_list = ("black", "grey", "white", "red", "orange", "yellow", "green", "cyan", "blue", "purple")
    H_min = (0, 0, 0, 0, 11, 26, 35, 78, 100, 125)
    H_max = (180, 180, 180, 10, 25, 34, 77, 99, 124, 155)
    # H_min = (0, 0, 0, 156, 11, 26, 35, 78, 100, 125)      # other red
    # H_max = (180, 180, 180, 180, 25, 34, 77, 99, 124, 155)    # other red
    S_min = (0, 0, 0, 43, 43, 43, 43, 43, 43, 43)
    S_max = (255, 43, 30, 255, 255, 255, 255, 255, 255, 255)
    V_min = (0, 46, 221, 46, 46, 46, 46, 46, 46, 46)
    V_max = (46, 220, 255, 255, 255, 255, 255, 255, 255, 255)
    if color not in color_list:
        print(f"not support {color}, return black threshold")
        color = "black"
    color_id = color_list.index(color)
    return np.array([H_min[color_id], S_min[color_id], V_min[color_id]]), np.array(
        [H_max[color_id], S_max[color_id], V_max[color_id]])


def delete_orphans(img_raw: bytes = None, img_path: str = None, fill_color: Tuple[int, int, int] = (0, 0, 0)):
    """删除孤立点"""
    if img_raw is None and img_path is None:
        raise ValueError("img_raw and img_path can't be None at the same time")
    if img_path is None:
        img = cv2.imdecode(np.frombuffer(img_raw, np.uint8), cv2.IMREAD_COLOR)
    else:
        img = cv2.imread(img_path, cv2.IMREAD_COLOR)
    grey = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    _, thresh = cv2.threshold(grey, 127, 255, cv2.THRESH_BINARY)
    contours, _ = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    cv_contours = []
    for contour in contours:
        area = cv2.contourArea(contour)
        if area <= 10:
            cv_contours.append(contour)
    cv2.fillPoly(img, cv_contours, fill_color)
    return cv2.imencode(".png", img)[1].tobytes()


def get_single_color(color: str = "blue", img_raw: bytes = None, img_path: str = None) -> bytes:
    """获取单色图片"""
    if img_raw is None and img_path is None:
        raise ValueError("img_raw and img_path can't be None at the same time")
    if img_path is None:
        img = cv2.imdecode(np.frombuffer(img_raw, np.uint8), cv2.IMREAD_COLOR)
    else:
        img = cv2.imread(img_path, cv2.IMREAD_COLOR)

    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    hsv_min, hsv_max = __get_threshold(color)
    mask = cv2.inRange(hsv, hsv_min, hsv_max)
    if color == "black":
        img = cv2.bitwise_not(img)
    res = cv2.bitwise_and(img, img, mask=mask)
    cv2.cvtColor(res, cv2.COLOR_HSV2BGR)
    return cv2.imencode(".png", res)[1].tobytes()
