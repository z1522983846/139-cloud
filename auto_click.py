from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import logging
import os

# 设置工作目录
WORKDIR = os.getcwd()
logger = logging.getLogger(__name__)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

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
    
    logger.info("正在访问云手机页面...")
    driver.get(CLOUD_PHONE_URL)
    time.sleep(5)
    
    # 截图 1: 设置 Cookie 前
    screenshot_path = os.path.join(WORKDIR, "01_before_cookie.png")
    driver.save_screenshot(screenshot_path)
    logger.info(f"截图 1 已保存：{screenshot_path}")
    logger.info(f"工作目录：{WORKDIR}")
    
    # 删除旧 Cookie
    driver.delete_all_cookies()
    
    # 设置新 Cookie
    logger.info(f"设置 Cookie: smidV2={cookie_smid[:20]}...")
    driver.add_cookie({
        'name': 'smidV2',
        'value': cookie_smid,
        'domain': '.139.com',
        'path': '/',
    })
    
    if cookie_thumbcache:
        logger.info(f"设置 Cookie: thumbcache={cookie_thumbcache[:20]}...")
        driver.add_cookie({
            'name': '.thumbcache_5b7c44fefb14167545f4272c83419943',
            'value': cookie_thumbcache,
            'domain': '.139.com',
            'path': '/',
        })
    
    # 刷新页面
    logger.info("刷新页面让 Cookie 生效...")
    driver.refresh()
    time.sleep(5)
    
    # 截图 2: 刷新后
    screenshot_path = os.path.join(WORKDIR, "02_after_refresh.png")
    driver.save_screenshot(screenshot_path)
    logger.info(f"截图 2 已保存：{screenshot_path}")
    
    return driver

def save_screenshot(driver, name):
    try:
        screenshot_path = os.path.join(WORKDIR, f"{name}.png")
        driver.save_screenshot(screenshot_path)
        logger.info(f"截图已保存：{screenshot_path}")
        return screenshot_path
    except Exception as e:
        logger.error(f"截图失败：{str(e)}")
        return None

def click_by_position(driver, x, y):
    script = f"""
    var element = document.elementFromPoint({x}, {y});
    if (element) {{
        element.click();
        return true;
    }} else {{
        return false;
    }}
    """
    return driver.execute_script(script)

def click_by_text(driver, text):
    try:
        selectors = [
            f"//*[contains(text(), '{text}')]",
            f"//*[contains(@title, '{text}')]",
            f"//*[@aria-label='{text}']",
            f"//button[contains(., '{text}')]",
            f"//a[contains(., '{text}')]"
        ]
        for selector in selectors:
            elements = driver.find_elements(By.XPATH, selector)
            for element in elements:
                if element.is_displayed() and element.is_enabled():
                    driver.execute_script("arguments[0].scrollIntoView(true);", element)
                    element.click()
                    logger.info(f"成功点击：{text}")
                    return True
        return False
    except Exception as e:
        logger.warning(f"点击失败：{str(e)}")
        return False

def automate_click():
    driver = None
    
    try:
        cookie_smid = os.getenv('COOKIE_SMID')
        cookie_thumbcache = os.getenv('COOKIE_THUMBCACHE')
        
        if not cookie_smid:
            logger.error("❌ COOKIE_SMID 缺失")
            raise ValueError("COOKIE_SMID 缺失")
        
        logger.info("=" * 60)
        logger.info("开始执行")
        logger.info("=" * 60)
        
        driver = setup_driver(cookie_smid, cookie_thumbcache)
        
        # 步骤 1
        logger.info("步骤 1: 点击小白点...")
        click_by_position(driver, WHITE_DOT_X, WHITE_DOT_Y)
        save_screenshot(driver, "03_after_white_dot")
        time.sleep(2)
        
        # 步骤 2
        logger.info("步骤 2: 点击退出云机...")
        if not click_by_text(driver, "退出云机"):
            click_by_text(driver, "退出")
        save_screenshot(driver, "04_after_exit")
        time.sleep(3)
        
        # 步骤 3
        logger.info("步骤 3: 点击进入云手机...")
        click_by_position(driver, ENTER_CLOUD_PHONE_X, ENTER_CLOUD_PHONE_Y)
        save_screenshot(driver, "05_final_page")
        time.sleep(2)
        
        logger.info("=" * 60)
        logger.info("✓ 完成")
        logger.info("=" * 60)
        
    except Exception as e:
        logger.error(f"✗ 失败：{str(e)}")
        if driver:
            save_screenshot(driver, "06_error")
        raise
    finally:
        if driver:
            driver.quit()

if __name__ == "__main__":
    automate_click()
