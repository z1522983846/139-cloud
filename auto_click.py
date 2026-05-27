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
    
    # 第一步：访问云手机页面
    logger.info("访问云手机页面...")
    driver.get(CLOUD_PHONE_URL)
    time.sleep(5)
    
    # 截图：访问后
    driver.save_screenshot("01_before_cookie.png")
    logger.info("截图：01_before_cookie.png")
    
    # 第二步：设置 Cookie
    logger.info("设置 Cookie...")
    logger.info(f"COOKIE_SMID: {cookie_smid[:20]}...")
    logger.info(f"COOKIE_THUMBCACHE: {cookie_thumbcache[:20] if cookie_thumbcache else 'None'}...")
    
    # 删除可能存在的旧 Cookie
    driver.delete_all_cookies()
    time.sleep(1)
    
    # 设置新的 Cookie
    driver.add_cookie({
        'name': 'smidV2',
        'value': cookie_smid,
        'domain': '.139.com',
        'path': '/',
    })
    logger.info("✓ smidV2 Cookie 已设置")
    
    if cookie_thumbcache:
        driver.add_cookie({
            'name': '.thumbcache_5b7c44fefb14167545f4272c83419943',
            'value': cookie_thumbcache,
            'domain': '.139.com',
            'path': '/',
        })
        logger.info("✓ thumbcache Cookie 已设置")
    
    # 截图：设置 Cookie 后
    driver.save_screenshot("02_after_cookie.png")
    logger.info("截图：02_after_cookie.png")
    
    # 第三步：刷新页面让 Cookie 生效
    logger.info("刷新页面...")
    driver.refresh()
    time.sleep(5)
    
    # 截图：刷新后
    driver.save_screenshot("03_after_refresh.png")
    logger.info("截图：03_after_refresh.png")
    
    # 检查当前 Cookie
    current_cookies = driver.get_cookies()
    logger.info(f"当前 Cookie 数量：{len(current_cookies)}")
    for cookie in current_cookies:
        logger.info(f"  - {cookie['name']}: {cookie['value'][:30]}...")
    
    return driver

def save_screenshot(driver, name):
    try:
        filename = f"{name}.png"
        driver.save_screenshot(filename)
        logger.info(f"截图已保存：{filename}")
        return filename
    except Exception as e:
        logger.error(f"截图失败：{str(e)}")
        return None

def click_element_by_position(driver, x, y):
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

def click_by_partial_text(driver, text):
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
    except:
        return False

def automate_click():
    driver = None
    step = 0
    
    try:
        cookie_smid = os.getenv('COOKIE_SMID')
        cookie_thumbcache = os.getenv('COOKIE_THUMBCACHE')
        
        if not cookie_smid:
            logger.error("❌ COOKIE_SMID 缺失")
            raise ValueError("COOKIE_SMID 缺失")
        
        logger.info("=" * 60)
        logger.info("开始执行自动化任务")
        logger.info("=" * 60)
        
        driver = setup_driver(cookie_smid, cookie_thumbcache)
        
        # 步骤 1：点击小白点
        logger.info("步骤 1：点击小白点...")
        result = click_element_by_position(driver, WHITE_DOT_X, WHITE_DOT_Y)
        logger.info("✓ 小白点点击成功" if result else "✗ 小白点点击失败")
        step = 1
        save_screenshot(driver, f"{step:02d}_after_white_dot")
        time.sleep(2)
        
        # 步骤 2：点击"退出云机"
        logger.info("步骤 2：点击'退出云机'...")
        if not click_by_partial_text(driver, "退出云机"):
            click_by_partial_text(driver, "退出") or click_by_partial_text(driver, "关闭")
        step = 2
        save_screenshot(driver, f"{step:02d}_after_exit")
        time.sleep(3)
        
        # 步骤 3：点击"进入云手机"
        logger.info("步骤 3：点击'进入云手机'...")
        result = click_element_by_position(driver, ENTER_CLOUD_PHONE_X, ENTER_CLOUD_PHONE_Y)
        logger.info("✓ 进入云手机成功" if result else "✗ 进入云手机失败")
        step = 3
        save_screenshot(driver, f"{step:02d}_final_page")
        time.sleep(2)
        
        logger.info("=" * 60)
        logger.info("✓ 任务完成")
        logger.info("=" * 60)
        
    except Exception as e:
        logger.error(f"✗ 任务失败：{str(e)}")
        if driver:
            step += 1
            save_screenshot(driver, f"{step:02d}_error")
        raise
    finally:
        if driver:
            driver.quit()

if __name__ == "__main__":
    automate_click()
