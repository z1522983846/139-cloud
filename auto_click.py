from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import logging
import os

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

CLOUD_PHONE_URL = "https://cloud.139.com/#/instance?phoneId=32s2yvm9&lockStatus=0"

# 精确坐标
WHITE_DOT_X = 786
WHITE_DOT_Y = 993
EXIT_BUTTON_X = 1093
EXIT_BUTTON_Y = 758
ENTER_CLOUD_PHONE_X = 1733
ENTER_CLOUD_PHONE_Y = 423
RECONNECT_BUTTON_X = 1123
RECONNECT_BUTTON_Y = 954
ENTER_NOW_X = 971
ENTER_NOW_Y = 954

def setup_driver(cookie_smid, cookie_thumbcache):
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--window-size=1920,1080')
    chrome_options.binary_location = "/usr/bin/chromium-browser"
    
    driver = webdriver.Chrome(options=chrome_options)
    
    driver.get("https://cloud.139.com")
    time.sleep(2)
    
    driver.add_cookie({
        'name': 'smidV2',
        'value': cookie_smid,
        'domain': '.139.com',
        'path': '/',
        'secure': True
    })
    
    driver.add_cookie({
        'name': '.thumbcache_5b7c44fefb14167545f4272c83419943',
        'value': cookie_thumbcache,
        'domain': '.139.com',
        'path': '/',
        'secure': True
    })
    
    return driver

def save_screenshot(driver, step_name):
    """截图并保存到文件"""
    try:
        filename = f"screenshot_{step_name}.png"
        driver.save_screenshot(filename)
        logger.info(f"Screenshot saved: {filename}")
        return filename
    except Exception as e:
        logger.error(f"Screenshot failed: {str(e)}")
        return None

def click_by_position(driver, x, y):
    script = """
    var element = document.elementFromPoint(""" + str(x) + """, """ + str(y) + """);
    if (element) {
        element.click();
        return true;
    } else {
        return false;
    }
    """
    return driver.execute_script(script)

def click_by_text(driver, text):
    try:
        xpath = "//*[contains(text(), '" + text + "')]"
        element = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.XPATH, xpath))
        )
        driver.execute_script("arguments[0].scrollIntoView(true);", element)
        element.click()
        logger.info("Clicked: " + text)
        return True
    except:
        return False

def check_and_enter_now(driver):
    logger.info("Checking for idle prompt...")
    enter_texts = ["现在进入", "立即进入", "进入"]
    for text in enter_texts:
        if click_by_text(driver, text):
            logger.info("Enter now button clicked using text: " + text)
            return True
    logger.info("Trying coordinate click for enter now button...")
    result = click_by_position(driver, ENTER_NOW_X, ENTER_NOW_Y)
    if result:
        logger.info("Enter now button clicked using coordinate")
        return True
    logger.info("No idle prompt found, continuing...")
    return False

def check_and_reconnect(driver):
    logger.info("Checking for disconnection prompt...")
    reconnect_texts = ["重连", "重新连接", "连接异常"]
    for text in reconnect_texts:
        if click_by_text(driver, text):
            logger.info("Reconnect button clicked using text: " + text)
            return True
    logger.info("Trying coordinate click for reconnect button...")
    result = click_by_position(driver, RECONNECT_BUTTON_X, RECONNECT_BUTTON_Y)
    if result:
        logger.info("Reconnect button clicked using coordinate")
        return True
    logger.info("No disconnection prompt found, continuing...")
    return False

def automate_click():
    driver = None
    step = 0
    
    try:
        cookie_smid = os.getenv('COOKIE_SMID')
        cookie_thumbcache = os.getenv('COOKIE_THUMBCACHE')
        
        if not cookie_smid or not cookie_thumbcache:
            logger.error("Cookie missing")
            raise ValueError("Cookie missing")
        
        logger.info("Starting browser...")
        driver = setup_driver(cookie_smid, cookie_thumbcache)
        
        # 截图 1: 初始页面
        step = 1
        save_screenshot(driver, f"{step:02d}_initial_page")
        
        logger.info("Visiting URL...")
        driver.get(CLOUD_PHONE_URL)
        time.sleep(5)
        
        # 截图 2: 加载后
        step = 2
        save_screenshot(driver, f"{step:02d}_after_load")
        
        # Step 0a: 检查闲置提示
        logger.info("Step 0a: Check for idle prompt...")
        if check_and_enter_now(driver):
            logger.info("Clicked enter now, waiting...")
            time.sleep(5)
            step = 3
            save_screenshot(driver, f"{step:02d}_after_enter_now")
        
        # Step 0b: 检查连接异常
        logger.info("Step 0b: Check for disconnection...")
        if check_and_reconnect(driver):
            logger.info("Reconnected, waiting...")
            time.sleep(5)
            step = 4
            save_screenshot(driver, f"{step:02d}_after_reconnect")
        
        # Step 1: 点击小白点
        logger.info(f"Step 1: Click white dot at ({WHITE_DOT_X}, {WHITE_DOT_Y})...")
        result = click_by_position(driver, WHITE_DOT_X, WHITE_DOT_Y)
        logger.info("White dot clicked OK" if result else "White dot click FAILED")
        
        step = 5
        save_screenshot(driver, f"{step:02d}_after_white_dot")
        time.sleep(3)
        
        # Step 2: 点击"退出云机"
        logger.info(f"Step 2: Click exit cloud phone at ({EXIT_BUTTON_X}, {EXIT_BUTTON_Y})...")
        exit_clicked = False
        exit_texts = ["退出云机", "退出", "关闭云机"]
        for text in exit_texts:
            if click_by_text(driver, text):
                exit_clicked = True
                logger.info("Exit button clicked using text: " + text)
                break
        if not exit_clicked:
            result = click_by_position(driver, EXIT_BUTTON_X, EXIT_BUTTON_Y)
            logger.info("Exit button clicked using coordinate" if result else "Exit button click FAILED")
            exit_clicked = result
        
        step = 6
        save_screenshot(driver, f"{step:02d}_after_exit")
        time.sleep(3)
        
        # Step 3: 点击"进入云手机"
        logger.info(f"Step 3: Click enter cloud phone at ({ENTER_CLOUD_PHONE_X}, {ENTER_CLOUD_PHONE_Y})...")
        result = click_by_position(driver, ENTER_CLOUD_PHONE_X, ENTER_CLOUD_PHONE_Y)
        logger.info("Enter cloud phone clicked OK" if result else "Enter cloud phone click FAILED")
        
        step = 7
        save_screenshot(driver, f"{step:02d}_final_page")
        time.sleep(2)
        
        logger.info("=" * 50)
        logger.info("Task completed")
        logger.info("=" * 50)
        
    except Exception as e:
        logger.error(f"Task failed: {str(e)}")
        step += 1
        if driver:
            save_screenshot(driver, f"{step:02d}_error")
        raise
    finally:
        if driver:
            driver.quit()
            logger.info("Browser closed")

if __name__ == "__main__":
    automate_click()
