from selenium import webdriver
from selenium.webdriver.chrome.service import Service
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
WHITE_DOT_X = 237
WHITE_DOT_Y = 575
ENTER_CLOUD_PHONE_X = 629
ENTER_CLOUD_PHONE_Y = 735

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
        element = WebDriverWait(driver, 15).until(
            EC.element_to_be_clickable((By.XPATH, xpath))
        )
        driver.execute_script("arguments[0].scrollIntoView(true);", element)
        element.click()
        logger.info("Clicked: " + text)
        return True
    except Exception as e:
        logger.warning("Click failed: " + str(e))
        return False

def click_popup_menu_item(driver, index=1):
    """点击弹出菜单的第 index 项（从 1 开始）"""
    try:
        # 尝试点击弹出菜单的第一个按钮或链接
        script = """
        var buttons = document.querySelectorAll('button, a[role="button"], div[onclick]');
        if (arguments[0] < buttons.length) {
            buttons[arguments[0]].click();
            return true;
        }
        return false;
        """
        result = driver.execute_script(script, index - 1)
        if result:
            logger.info("Popup menu item " + str(index) + " clicked")
        return result
    except Exception as e:
        logger.warning("Click popup failed: " + str(e))
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
        
        # Step 1: 点击小白点
        logger.info("Step 1: Click white dot...")
        result = click_by_position(driver, WHITE_DOT_X, WHITE_DOT_Y)
        if result:
            logger.info("White dot clicked OK")
        else:
            logger.warning("White dot click failed")
        
        # 等待菜单弹出（增加到 5 秒）
        logger.info("Waiting for menu to appear...")
        time.sleep(5)
        
        # Step 2: 点击"退出云机"
        logger.info("Step 2: Try to click exit cloud phone...")
        
        # 尝试多种方式
        exit_clicked = False
        
        # 方式 1: 文字匹配
        exit_texts = ["退出云机", "退出", "关闭云机", "云机管理"]
        for text in exit_texts:
            if click_by_text(driver, text):
                exit_clicked = True
                logger.info("Exit button clicked using text: " + text)
                break
        
        # 方式 2: 如果文字都失败，尝试点击坐标
        if not exit_clicked:
            logger.info("Trying coordinate click for exit button...")
            # 尝试点击菜单第一个项目（大致位置）
            result = click_by_position(driver, 300, 600)
            if result:
                exit_clicked = True
                logger.info("Exit button clicked using coordinate")
        
        if exit_clicked:
            logger.info("Exit cloud phone step completed")
        else:
            logger.warning("Could not find exit button, skipping...")
        
        # 等待页面切换
        time.sleep(3)
        
        # Step 3: 点击"进入云手机"
        logger.info("Step 3: Click enter cloud phone...")
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
