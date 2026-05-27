from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from webdriver_manager.chrome import ChromeDriverManager
import time
import logging
import os

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 配置参数
CLOUD_PHONE_URL = "https://cloud.139.com/#/instance?phoneId=32s2yvm9&lockStatus=0"

# 小白点坐标（根据截图分析）
# 相对于整个页面的近似坐标
WHITE_DOT_X = 237
WHITE_DOT_Y = 575

# "进入云手机"按钮坐标（蓝色正方形区域的中心点）
# 根据截图分析，蓝色区域中心点约 (629, 735)
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
    
    # 先访问目标域名，才能设置 Cookie
    driver.get("https://cloud.139.com")
    time.sleep(3)
    
    # 设置 smidV2 Cookie（主要认证）
    driver.add_cookie({
        'name': 'smidV2',
        'value': cookie_smid,
        'domain': 'cloud.139.com',
        'path': '/',
        'secure': True
    })
    
    # 设置 thumbcache Cookie（会话缓存）
    if cookie_thumbcache:
        driver.add_cookie({
            'name': '.thumbcache_5b7c44fefb14167545f4272c83419943',
            'value': cookie_thumbcache,
            'domain': 'cloud.139.com',
            'path': '/',
            'secure': True
        })
    
    # 设置完 Cookie 后刷新页面，让 Cookie 生效
    driver.refresh()
    time.sleep(3)
    
    return driver

def click_element_by_position(driver, x, y):
    """通过坐标点击元素（使用 JavaScript）"""
    script = f"""
    var element = document.elementFromPoint({x}, {y});
    if (element) {{
        element.click();
        return true;
    }} else {{
        return false;
    }}
    """
    result = driver.execute_script(script)
    return result

def click_by_partial_text(driver, text):
    """通过部分文字点击按钮（更灵活）"""
    try:
        # 尝试多种选择器
        selectors = [
            f"//*[contains(text(), '{text}')]",
            f"//*[contains(@title, '{text}')]",
            f"//*[@aria-label='{text}']",
            f"//button[contains(., '{text}')]",
            f"//a[contains(., '{text}')]"
        ]
        
        for selector in selectors:
            try:
                elements = driver.find_elements(By.XPATH, selector)
                for element in elements:
                    if element.is_displayed() and element.is_enabled():
                        driver.execute_script("arguments[0].scrollIntoView(true);", element)
                        element.click()
                        logger.info(f"成功点击：{text}")
                        return True
            except:
                continue
        
        logger.warning(f"未找到可点击的元素：{text}")
        return False
    except Exception as e:
        logger.error(f"点击失败：{str(e)}")
        return False

def automate_click():
    """执行自动化点击任务"""
    driver = None
    
    try:
        # 从环境变量获取 Cookie
        cookie_smid = os.getenv('COOKIE_SMID')
        cookie_thumbcache = os.getenv('COOKIE_THUMBCACHE')
        
        if not cookie_smid:
            logger.error("Cookie 配置缺失，请检查 GitHub Secrets")
            raise ValueError("Cookie 配置缺失")
        
        logger.info("正在启动浏览器...")
        driver = setup_driver(cookie_smid, cookie_thumbcache)
        
        logger.info(f"访问云手机页面：{CLOUD_PHONE_URL}")
        driver.get(CLOUD_PHONE_URL)
        time.sleep(5)  # 等待页面加载
        
        # 步骤 1：点击小白点（坐标点击）
        logger.info("步骤 1：点击小白点...")
        click_result = click_element_by_position(driver, WHITE_DOT_X, WHITE_DOT_Y)
        
        if click_result:
            logger.info("✓ 小白点点击成功")
        else:
            logger.warning("✗ 小白点点击失败，尝试备用方案...")
            # 备用方案：尝试查找小白点的元素
            try:
                # 小白点通常是固定 class 或 id
                white_dot = driver.find_element(By.CSS_SELECTOR, "[class*='assistive'], [id*='assistive'], .touch-assistant")
                driver.execute_script("arguments[0].click();", white_dot)
                logger.info("✓ 小白点点击成功（备用方案）")
            except Exception as e:
                logger.error(f"✗ 小白点点击失败：{str(e)}")
        
        time.sleep(2)  # 等待菜单弹出
        
        # 步骤 2：点击"退出云机"
        logger.info("步骤 2：点击'退出云机'...")
        if not click_by_partial_text(driver, "退出云机"):
            logger.warning("未找到'退出云机'，尝试其他关键词...")
            # 尝试其他可能的文字
            click_by_partial_text(driver, "退出") or \
            click_by_partial_text(driver, "关闭")
        
        time.sleep(3)  # 等待页面反应（云手机列表加载可能需要更长时间）
        
        # 步骤 3：点击"进入云手机"（固定坐标位置）
        logger.info("步骤 3：点击'进入云手机'按钮位置...")
        click_result = click_element_by_position(driver, ENTER_CLOUD_PHONE_X, ENTER_CLOUD_PHONE_Y)
        
        if click_result:
            logger.info("✓ 进入云手机按钮点击成功")
        else:
            logger.warning("✗ 坐标点击失败，尝试备用方案...")
            # 备用方案：尝试通过文字查找（测试页面可能有文字）
            if not click_by_partial_text(driver, "进入云手机"):
                logger.error("✗ 备用方案也失败了")
        
        time.sleep(2)
        
        logger.info("=" * 50)
        logger.info("✓ 任务执行完成")
        logger.info("=" * 50)
        
    except Exception as e:
        logger.error(f"✗ 执行失败：{str(e)}")
        raise
    finally:
        if driver:
            driver.quit()
            logger.info("浏览器已关闭")

if __name__ == "__main__":
    automate_click()
