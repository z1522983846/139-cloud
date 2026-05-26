from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
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
    
    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=chrome_options
    )
    
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
    script = f"""
    var element = document.elementFromPoint({x}, {y});
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
        xpath = f"//*[contains(text(), '{text}')]"
        element = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, xpath))
        )
        driver.execute_script("arguments[0].scrollIntoView(true);", element)
        element.click()
        logger.info(f"Clicked: {text}")
        return True
    except Exception as e:
        logger.warning(f"Click {text} failed: {str(e)}")
        return False

def automate_click():
    driver = None
    
    try:
        cookie_smid = os.getenv('COOKIE_SMID')
        cookie_thumbcache = os.getenv('COOKIE_THUMBCACHE')
        
        if not cookie_smid or not cookie_thumbcache:
            logger.error("Cookie missing, check GitHub Secrets")
            raise ValueError("Cookie missing")
        
        logger.info("Starting browser...")
        driver = setup_driver(cookie_smid, cookie_thumbcache)
        
        logger.info(f"Visiting: {CLOUD_PHONE_URL}")
        driver.get(CLOUD_PHONE_URL)
        time.sleep(5)
        
        logger.info("Step 1: Click white dot...")
        result = click_by_position(driver, WHITE_DOT_X, WHITE_DOT_Y)
        if result:
            logger.info("White dot clicked OK")
        
        time.sleep(2)
        
        logger.info("Step 2: Click exit cloud phone...")
        click_by_text(driver, "退出云机")
        
        time.sleep(3)
        
        logger.info("Step 3: Click enter cloud phone...")
        result = click_by_position(driver, ENTER_CLOUD_PHONE_X, ENTER_CLOUD_PHONE_Y)
        if result:
            logger.info("Enter cloud phone clicked OK")
        
        time.sleep(2)
        
        logger.info("=" * 50)
        logger.info("Task completed successfully")
        logger.info("=" * 50)
        
    except Exception as e:
        logger.error(f"Task failed: {str(e)}")
        raise
    finally:
        if driver:
            driver.quit()
            logger.info("Browser closed")

if __name__ == "__main__":
    automate_click()
