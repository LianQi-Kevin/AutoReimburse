import logging
import os
import re
import time
from urllib.parse import parse_qs, urlparse, urlunparse, urlencode

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager

from tools.chaojiying import img_detect, wrong_report
from tools.download import download_File
from tools.img_utils import base64_to_image_raw, image_raw_to_base64
from tools.retry_tools import task_retry
from tools.verify_code_tools import get_single_color

OLD_YZM_B64 = ""


def set_driver(headless_mode: bool = False, auto_detach: bool = False, download_path: str = None) -> webdriver.Chrome:
    """
    Set up the driver
    :param download_path: if not None, change default download path
    :param auto_detach: whether to automatically detach the driver
    :param headless_mode: Whether to use headless mode
    """
    options = Options()
    # 无头模式
    if headless_mode:
        logging.info("Use headless mode")
        options.add_argument('headless')

    # 进程结束自动关闭浏览器
    if not auto_detach:
        options.add_experimental_option("detach", True)

    # 修改下载设置
    if download_path is not None:
        prefs = {'profile.default_content_settings.popups': 0,  # 防止保存弹窗
                 'download.default_directory': download_path,  # 设置默认下载路径
                 "profile.default_content_setting_values.automatic_downloads": 1  # 允许多文件下载
                 }
        options.add_experimental_option('prefs', prefs)

    # 隐藏特征
    options.add_argument('ignore-certificate-errors')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-gpu')
    options.add_argument(
        'user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) '
        'Chrome/109.0.5414.74 Safari/537.36')
    options.add_experimental_option('excludeSwitches', ['enable-automation'])
    options.add_experimental_option('useAutomationExtension', False)
    options.page_load_strategy = "normal"
    driver = webdriver.Chrome(options=options, service=ChromeService(ChromeDriverManager().install()))
    driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {"source": """
            Object.defineProperty(navigator, 'webdriver', {
              get: () => undefined
            })
          """})
    return driver


def web_wait(driver: webdriver, by: str, element: str, until_sec: int = 20):
    WebDriverWait(driver, until_sec).until(EC.presence_of_element_located((by, element)))


def check_element_exists(driver: webdriver.Chrome, element: str, find_model=By.CLASS_NAME) -> bool:
    """
    Check whether the element exists
    :param driver: browser drive
    :param element: WebElement
    :param find_model: The selenium locator, default By.CLASS_NAME
    :return: bool, whether the element exists
    """
    try:
        driver.find_element(find_model, element)
        return True
    except Exception:
        return False


def add_tax_params(driver: webdriver.Chrome, invoice_msg: dict):
    """add tax params"""
    web_wait(driver, By.ID, "fpdm")
    ActionChains(driver).move_to_element(driver.find_element(By.ID, "fpdm")).click().perform()
    driver.find_element(By.ID, "fpdm").send_keys(invoice_msg["code"])
    ActionChains(driver).move_to_element(driver.find_element(By.ID, "fphm")).click().perform()
    driver.find_element(By.ID, "fphm").send_keys(invoice_msg["id"])
    ActionChains(driver).move_to_element(driver.find_element(By.ID, "kprq")).click().perform()
    driver.find_element(By.ID, "kprq").send_keys(invoice_msg["date"])
    ActionChains(driver).move_to_element(driver.find_element(By.ID, "kjje")).click().perform()
    driver.find_element(By.ID, "kjje").send_keys(invoice_msg["verify"][-6:])
    ActionChains(driver).move_to_element(driver.find_element(By.ID, "yzm")).click().perform()


@task_retry(max_retry_count=3, time_interval=2, max_timeout=15)
def get_yzm_image_src(driver: webdriver.Chrome) -> str:
    """获取验证码图片"""
    logging.info("Start get yzm src")
    global OLD_YZM_B64
    web_wait(driver, By.ID, "yzm_img")
    while driver.find_element(By.ID, "yzminfo").text == "":
        time.sleep(1)

    yzm_src = driver.find_element(By.ID, "yzm_img").get_attribute("src")
    if yzm_src == OLD_YZM_B64:
        ActionChains(driver).move_to_element(driver.find_element(By.ID, "yzm_img")).click().perform()
        time.sleep(0.5)
        yzm_src = driver.find_element(By.ID, "yzm_img").get_attribute("src")
    while yzm_src == OLD_YZM_B64:
        yzm_src = driver.find_element(By.ID, "yzm_img").get_attribute("src")
        time.sleep(1)

    OLD_YZM_B64 = yzm_src
    if yzm_src[: 4] != "data":
        return get_yzm_image_src(driver)
    else:
        return yzm_src.replace("data:image/png;base64,", "")


def fix_yzm(driver: webdriver.Chrome, color: str = "black"):
    """验证码相关操作"""
    # 获取b64并提取color字段
    logging.info(f"Start to fix yzm")
    yzm_b64 = get_yzm_image_src(driver)
    if check_element_exists(driver, "#yzminfo > font", By.CSS_SELECTOR):
        color = driver.find_element(By.CSS_SELECTOR, "#yzminfo > font").get_attribute("color")

    # 打码
    captcha_response = img_detect(image_raw_to_base64(get_single_color(color, img_raw=base64_to_image_raw(yzm_b64))))
    logging.info(f"验证码识别结果: {captcha_response}")

    # 填充并提交
    driver.find_element(By.ID, "yzm").clear()
    driver.find_element(By.ID, "yzm").send_keys(captcha_response["pic_str"])
    time.sleep(1)
    ActionChains(driver).move_to_element(driver.find_element(By.ID, "checkfp")).perform()
    while not driver.find_element(By.ID, "checkfp").is_displayed():
        time.sleep(0.5)
    ActionChains(driver).move_to_element(driver.find_element(By.ID, "checkfp")).click().perform()

    # 处理验证码错误
    while not check_element_exists(driver, "dialog-body", By.ID) and not check_element_exists(driver, "popup_container",
                                                                                              By.ID):
        time.sleep(0.5)
    if check_element_exists(driver, "popup_message", By.ID):
        error_msg = driver.find_element(By.ID, 'popup_message').text
        logging.info(f"Error code: {error_msg}")
        # 回报验证码错误
        if "验证码错误" in error_msg:
            wrong_report(captcha_response["pic_id"])
        ActionChains(driver).move_to_element(driver.find_element(By.ID, "popup_ok")).click().perform()
        time.sleep(0.5)
        return fix_yzm(driver)


def get_fp_info(driver: webdriver.Chrome, invoice_msg: dict, html_cache_path: str = "data/html") -> dict:
    """提取发票验证页信息"""
    basename = f"{invoice_msg['id']}_{invoice_msg['date']}_{invoice_msg['money']}"
    # 进入iframe
    driver.switch_to.frame(driver.find_element(By.ID, "dialog-body"))
    os.makedirs(html_cache_path, exist_ok=True)
    with open(os.path.join(html_cache_path, f"{basename}.html"), "w", encoding="utf-8") as f:
        f.write(driver.page_source)
    # get info dict
    info_dict = {
        "code": invoice_msg["code"],
        "invoice_info": {
            "type": int(invoice_msg["type"]),
            "id": int(invoice_msg["id"]),
            "money": float(invoice_msg["money"]),
            "date": int(invoice_msg["date"]),
            "verify": int(invoice_msg["verify"]),
            "password": driver.find_element(By.ID, "password_dzfp").text,
            "total": float(re.findall(r"\d+\.?\d*", driver.find_element(By.ID, "jshjxx_dzfp").text)[0]),
        },
        "verify_info": {
            "machine_id": int(driver.find_element(By.ID, "sbbh_dzfp").text),
            "buyer_name": driver.find_element(By.ID, "gfmc_dzfp").text,
            "buyer_id": driver.find_element(By.ID, "gfsbh_dzfp").text,
            "buyer_address": driver.find_element(By.ID, "gfdzdh_dzfp").text,
            "buyer_account": driver.find_element(By.ID, "gfyhzh_dzfp").text,
            "seller_name": driver.find_element(By.ID, "xfmc_dzfp").text,
            "seller_id": driver.find_element(By.ID, "xfsbh_dzfp").text,
            "seller_address": driver.find_element(By.ID, "xfdzdh_dzfp").text,
            "seller_account": driver.find_element(By.ID, "xfyhzh_dzfp").text,
            "img_b64": driver.find_element(By.ID, "content").screenshot_as_base64
        },
        "filename": f"{basename}.json"
    }

    # todo: 待抽取具体税项
    # find_elements(By.CSS, "#tabPage-dzfp table.fppy_table")[1: -2]

    return info_dict


def get_tax_url(driver: webdriver.Chrome) -> str:
    """decode china.tax.gov.cn and get pdf url"""
    params = urlparse(driver.current_url)
    query = {
        "action": "getDoc",
        "code": parse_qs(params.query)["code"][0],
        "type": 12
    }
    return urlunparse((params.scheme, params.netloc, '/api', '', urlencode(query), ''))


def download_PDF(driver: webdriver.Chrome, filename: str):
    """下载版式PDF"""
    # 触发版式下载按钮
    ActionChains(driver).move_to_element(driver.find_element(By.ID, "pdfDownNow")).click().perform()
    # 获取所有窗口句柄
    # base_handle = driver.current_window_handle
    # 跳转到版式文件下载窗口并组装PDF下载地址
    tax_url = None
    for handle in driver.window_handles:
        driver.switch_to.window(handle)
        if driver.title == "版式文件下载":
            tax_url = get_tax_url(driver)
            break
    # 下载
    download_File(tax_url, filename)
