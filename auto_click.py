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

# 精确坐标（根据最新截图分析）
# Step 0a: 现在进入（闲置提示弹窗）
ENTER_NOW_X = 971
ENTER_NOW_Y = 954

# Step 0b: 重连（云机连接异常）
RECONNECT_BUTTON_X = 1123
RECONNECT_BUTTON_Y = 954

# Step 1: 小白点
WHITE_DOT_X = 786
WHITE_DOT_Y = 993

# Step 2: 退出云机（弹窗中间）
EXIT_BUTTON_X = 1093
EXIT_BUTTON_Y = 758

# Step 3: 进入云手机（蓝色区域）
ENTER_CLOUD_PHONE_X = 1733
ENTER_CLOUD_PHONE_Y = 423

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
    """检查是否有闲置提示，如果有就点击现在进入"""
    logger.info("Checking for idle prompt...")
    
    # 方式 1: 文字匹配
    enter_texts = ["现在进入", "立即进入", "进入"]
    for text in enter_texts:
        if click_by_text(driver, text):
            logger.info("Enter now button clicked using text: " + text)
            return True
    
    # 方式 2: 坐标点击
    logger.info("Trying coordinate click for enter now button...")
    result = click_by_position(driver, ENTER_NOW_X, ENTER_NOW_Y)
    if result:
        logger.info("Enter now button clicked using coordinate")
        return True
    
    logger.info("No idle prompt found, continuing...")
    return False

def check_and_reconnect(driver):
    """检查是否有云机连接异常提示，如果有就点击重连"""
    logger.info("Checking for cloud phone disconnection prompt...")
    
    # 方式 1: 文字匹配
    reconnect_texts = ["重连", "重新连接", "连接异常"]
    for text in reconnect_texts:
        if click_by_text(driver, text):
            logger.info("Reconnect button clicked using text: " + text)
            return True
    
    # 方式 2: 坐标点击
    logger.info("Trying coordinate click for reconnect button...")
    result = click_by_position(driver, RECONNECT_BUTTON_X, RECONNECT_BUTTON_Y)
    if result:
        logger.info("Reconnect button clicked using coordinate")
        return True
    
    logger.info("No disconnection prompt found, continuing...")
    return False

def automate_click():
    driver = None
    
    try:
        cookie_smid = os.getenv('COOKIE_SMID')
        cookie_thumbcache = os.getenv('COOKIE_THUMBCACHE')
        
        if not cookie_smid or not cookie_thumbcache:
            logger.error("Cookie missing")
            raise ValueError("Cookie missing")
        
        logger.info("Starting browser...")
        driver = setup_driver(cookie_smid, cookie_thumbcache)
        
        logger.info("Visiting URL...")
        driver.get(CLOUD_PHONE_URL)
        time.sleep(5)
        
        # Step 0a: 检查是否有闲置提示（现在进入）
        logger.info("Step 0a: Check for idle prompt...")
        if check_and_enter_now(driver):
            logger.info("Clicked enter now, waiting...")
            time.sleep(5)
        
        # Step 0b: 检查是否有连接异常（重连）
        logger.info("Step 0b: Check for disconnection prompt...")
        if check_and_reconnect(driver):
            logger.info("Reconnected, waiting...")
            time.sleep(5)
        
        # Step 1: 点击小白点
        logger.info("Step 1: Click white dot at (" + str(WHITE_DOT_X) + ", " + str(WHITE_DOT_Y) + ")...")
        result = click_by_position(driver, WHITE_DOT_X, WHITE_DOT_Y)
        if result:
            logger.info("White dot clicked OK")
        else:
            logger.warning("White dot click failed")
        
        time.sleep(3)
        
        # Step 2: 点击"退出云机"（弹窗中间）
        logger.info("Step 2: Click exit cloud phone at (" + str(EXIT_BUTTON_X) + ", " + str(EXIT_BUTTON_Y) + ")...")
        
        exit_clicked = False
        exit_texts = ["退出云机", "退出", "关闭云机"]
        for text in exit_texts:
            if click_by_text(driver, text):
                exit_clicked = True
                logger.info("Exit button clicked using text: " + text)
                break
        
        if not exit_clicked:
            result = click_by_position(driver, EXIT_BUTTON_X, EXIT_BUTTON_Y)
            if result:
                exit_clicked = True
                logger.info("Exit button clicked using coordinate")
        
        if exit_clicked:
            logger.info("Exit cloud phone step completed")
        else:
            logger.warning("Could not find exit button")
        
        time.sleep(3)
        
        # Step 3: 点击"进入云手机"
        logger.info("Step 3: Click enter cloud phone at (" + str(ENTER_CLOUD_PHONE_X) + ", " + str(ENTER_CLOUD_PHONE_Y) + ")...")
        result = click_by_position(driver, ENTER_CLOUD_PHONE_X, ENTER_CLOUD_PHONE_Y)
        if result:
            logger.info("Enter cloud phone clicked OK")
        else:
            logger.warning("Enter cloud phone click failed")
        
        time.sleep(2)
        
        logger.info("=" * 50)
        logger.info("Task completed")
        logger.info("=" * 50)
        
    except Exception as e:
        logger.error("Task failed: " + str(e))
        raise
    finally:
        if driver:
            driver.quit()
            logger.info("Browser closed")

if __name__ == "__main__":
    automate_click()
