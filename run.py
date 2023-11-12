import logging
import time

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager

from tools.QRcode_decode import decode_from_path
from tools.chaojiying import img_detect
from tools.logging_utils import log_set
from tools.utils import base64_to_image_raw, image_raw_to_base64
from tools.verify_code_tools import get_single_color

BASE_URL = "https://inv-veri.chinatax.gov.cn/"
OLD_YZM_B64 = ""


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
    while not check_element_exists(driver, "dialog-body", By.ID) and not check_element_exists(driver, "popup_container", By.ID):
        time.sleep(0.5)
    if check_element_exists(driver, "popup_message", By.ID):
        logging.info(f"Error code: {driver.find_element(By.ID, 'popup_message').text}")
        ActionChains(driver).move_to_element(driver.find_element(By.ID, "popup_ok")).click().perform()
        time.sleep(0.5)
        return fix_yzm(driver)


def get_fp(driver: webdriver.Chrome, invoice_msg: dict):
    """提取发票验证页信息"""
    # 进入iframe并截图
    driver.switch_to.frame(driver.find_element(By.ID, "dialog-body"))
    content = driver.find_element(By.ID, "content")

    verify_res = content.screenshot_as_base64

    # get other info


def set_driver(headless_mode: bool = False, auto_detach: bool = False) -> webdriver.Chrome:
    """
    Set up the driver
    :param auto_detach: whether to automatically detach the driver
    :param headless_mode: Whether to use headless mode
    """
    options = Options()
    if headless_mode:
        logging.info("Use headless mode")
        options.add_argument('headless')
    # 隐藏特征
    options.add_argument('ignore-certificate-errors')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-gpu')
    options.add_argument(
        'user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) '
        'Chrome/109.0.5414.74 Safari/537.36')
    options.add_experimental_option('excludeSwitches', ['enable-automation'])
    if not auto_detach:
        options.add_experimental_option("detach", True)   # 禁止进程结束后自动关闭浏览器
    options.add_experimental_option('useAutomationExtension', False)
    options.page_load_strategy = "normal"
    driver = webdriver.Chrome(options=options, service=ChromeService(ChromeDriverManager().install()))
    driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {"source": """
        Object.defineProperty(navigator, 'webdriver', {
          get: () => undefined
        })
      """})
    return driver


def decode_URL(invoice_msg: dict):
    logging.info(f"invoice_msg: {invoice_msg}")
    # open URL
    browser = set_driver(False)
    browser.get(BASE_URL)

    # 填充参数并获取验证码
    web_wait(browser, By.ID, "fpdm")
    ActionChains(browser).move_to_element(browser.find_element(By.ID, "fpdm")).click().perform()
    browser.find_element(By.ID, "fpdm").send_keys(invoice_msg["invoice_code"])
    ActionChains(browser).move_to_element(browser.find_element(By.ID, "fphm")).click().perform()
    browser.find_element(By.ID, "fphm").send_keys(invoice_msg["invoice_id"])
    ActionChains(browser).move_to_element(browser.find_element(By.ID, "kprq")).click().perform()
    browser.find_element(By.ID, "kprq").send_keys(invoice_msg["invoice_date"])
    ActionChains(browser).move_to_element(browser.find_element(By.ID, "kjje")).click().perform()
    browser.find_element(By.ID, "kjje").send_keys(invoice_msg["invoice_verify"][-6:])
    ActionChains(browser).move_to_element(browser.find_element(By.ID, "yzm")).click().perform()

    # 打码
    fix_yzm(browser)

    # 提取发票截图及信息
    get_fp(browser, invoice_msg)


if __name__ == '__main__':
    log_set(logging.INFO)

    decode_URL(decode_from_path("examples/发票/")[2])
    # for msg_dict in decode_from_path("examples/发票/"):
    #     print(decode_URL(msg_dict))
