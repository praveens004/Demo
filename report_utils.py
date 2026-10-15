from docx import Document
from docx.shared import Inches
from docx.shared import RGBColor

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from PIL import Image

from datetime import datetime

import math
import os
import time

# ==========================================
# DOCUMENT
# ==========================================

doc = Document()

doc.add_heading(
    "PeopleSoft IVT Automation Report",
    level=1
)

doc.add_paragraph(
    f"Generated Time: {datetime.now()}"
)

# ==========================================
# SCREENSHOT DIRECTORY
# ==========================================

SCREENSHOT_DIR = "screenshots"

if not os.path.exists(SCREENSHOT_DIR):
    os.makedirs(SCREENSHOT_DIR)

# ==========================================
# WAIT FOR PAGE READY
# ==========================================

def wait_for_page_ready(driver):

    wait = WebDriverWait(driver, 30)

    wait.until(
        lambda d:
        d.execute_script(
            "return document.readyState"
        ) == "complete"
    )

    try:

        wait.until_not(
            EC.presence_of_element_located(
                (
                    By.ID,
                    "processing"
                )
            )
        )

    except:
        pass

    time.sleep(0.5)

# ==========================================
# STITCHED SCREENSHOT
# ==========================================

def take_stitched_screenshot(
        driver,
        screenshot_path
):

    wait_for_page_ready(driver)

    driver.switch_to.default_content()

    screenshots = []

    use_iframe = False

    try:

        iframe = driver.find_element(
            By.ID,
            "ptifrmtgtframe"
        )

        driver.switch_to.frame(
            iframe
        )

        use_iframe = True

        total_height = driver.execute_script(
            "return document.documentElement.scrollHeight;"
        )

        viewport_height = driver.execute_script(
            "return window.innerHeight;"
        )

        #print(
            #f"Iframe Height = {total_height}"
        #)

    except Exception:

        driver.switch_to.default_content()

        total_height = driver.execute_script(
            "return document.documentElement.scrollHeight;"
        )

        viewport_height = driver.execute_script(
            "return window.innerHeight;"
        )

        #print(
            #f"Page Height = {total_height}"
        #)

    scroll_position = 0

    shot_no = 0
    last_scroll = -1

    while True:

        driver.execute_script(
            "window.scrollTo(0, arguments[0]);",
            scroll_position
        )

        time.sleep(0.5)

        current_scroll = driver.execute_script(
            "return window.pageYOffset;"
        )

        temp_file = (
            f"{SCREENSHOT_DIR}/"
            f"{os.path.basename(screenshot_path)}_part_{shot_no}.png"
        )

        driver.save_screenshot(
            temp_file
        )

        screenshots.append(
            temp_file
        )

        #print(
            #f"Captured Screenshot {shot_no + 1}"
        #)

        #print(
            #f"Current Scroll Position = {current_scroll}"
        #)

        shot_no += 1

        if current_scroll == last_scroll:
            print("Reached bottom")
            break
        last_scroll = current_scroll

        if (
            current_scroll + viewport_height
        ) >= (total_height-10):

            break

        scroll_position += viewport_height

    if use_iframe:

        driver.switch_to.default_content()
        try:

            iframe = driver.find_element(
                By.ID,
                "ptifrmtgtframe"
            )

            driver.switch_to.frame(
                iframe
            )
        except:
            pass

    #print(
        #f"Total Screenshots Captured = {len(screenshots)}"
    #)

    return screenshots
# ==========================================
# ADD STEP TO REPORT
# ==========================================

def add_step(
        driver,
        title,
        status="INFO",
        full_page=False
):

    timestamp = datetime.now().strftime(
        "%Y%m%d_%H%M%S"
    )

    screenshot_path = (
        f"{SCREENSHOT_DIR}/"
        f"{title}_{timestamp}"
    )

    if full_page:

        screenshots = take_stitched_screenshot(
            driver,
            screenshot_path
        )

    else:

        screenshot_file = (
            f"{screenshot_path}.png"
        )

        wait_for_page_ready(driver)

        driver.save_screenshot(
            screenshot_file
        )

        screenshots = [screenshot_file]

    doc.add_heading(
        title,
        level=2
    )

    p = doc.add_paragraph()

    run = p.add_run(
        f"STATUS: {status}"
    )

    run.bold = True

    color_map = {

        "PASS":
        RGBColor(0, 128, 0),

        "FAIL":
        RGBColor(255, 0, 0),

        "WARN":
        RGBColor(255, 165, 0),

        "INFO":
        RGBColor(0, 0, 255)

    }

    run.font.color.rgb = color_map.get(
        status.upper(),
        RGBColor(0, 0, 0)
    )

    for index, shot in enumerate(screenshots, start=1):

        doc.add_paragraph(
            f"Screenshot {index}"
        )

        doc.add_picture(
            shot,
            width=Inches(6.5)
        )
    for shot in screenshots:
        try:
            os.remove(shot)
        except:
            pass

    print(
        f"Added Report Section: {title}"
    )
# ==========================================
# SAVE REPORT
# ==========================================

def save_report():

    report_name = (
        "IVT_Report_"
        +
        datetime.now().strftime(
            "%Y%m%d_%H%M%S"
        )
        +
        ".docx"
    )

    doc.save(
        report_name
    )

    print(
        f"REPORT SAVED: "
        f"{report_name}"
    )
