from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import config

from report_utils import add_step
from getpass import getpass
from console import *



def get_credentials():

    username = input(
        "Enter User ID: "
    )

    password = getpass(
        "Enter Password: "
    )

    return username, password

def get_driver():
    options = webdriver.ChromeOptions()

    options.add_argument("--start-maximized")
    options.add_argument("--force-device-scale-factor=1")

    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=options
    )

    driver.maximize_window()

    # Set webpage zoom to 100%
    driver.execute_script(
        "document.body.style.zoom='100%'"
    ) if driver.execute_script(
        "return document.body !== null"
    ) else None

    return driver

def login(driver, username_value, password_value):
    driver.delete_all_cookies()
    driver.get(config.PIA_URL)

    wait = WebDriverWait(driver, 30)

    username = wait.until(
        EC.presence_of_element_located((By.ID, "userid"))
    )

    password = driver.find_element(By.ID, "pwd")
    #add_step(
        #driver,
        #"Login Page",
        #"INFO"
    #)

    username.send_keys(username_value)
    password.send_keys(password_value)

    driver.find_element(By.NAME, "Submit").click()


    wait.until(
        EC.presence_of_element_located((By.ID, "PT_NAVBAR"))
    )

    heading("LOGIN PAGE")
    success("Login successful")
    return True
    #time.sleep(3)

def verify_session(driver, username, password):
    try:
        page_source = driver.page_source.lower()

        if (
            "your peoplesoft connection has expired" in page_source
            or "your peoplesoft session has expired" in page_source
            or "sign in to peoplesoft" in page_source
        ):

            print("Session expired detected. Logging in again...")

            driver.switch_to.default_content()

            try:
                signin_link = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable(
                        (
                            By.XPATH,
            '//*[@id="login"]/div/div/div/div/p[4]/a[1]'
                        )
                    )
                )
                signin_link.click()

            except:
                pass

            login(driver, username, password)

            print("Re-login successful")
            return True

    except Exception as e:
        print(f"Session verification failed: {e}")

    return False

def run_travel_expense_page(driver):
    if config.ENV_NAME in["ESSPU", "ESSPX","ESSPV", "ESSPT","ESSPG", "ESSPPT"]:
        try:
            wait=WebDriverWait(driver, 30)
            driver.switch_to.default_content()
            
            travel_expense_tile=wait.until(
                EC.element_to_be_clickable(
                    (
                        By.ID,
                        "win0divPTNUI_LAND_REC_GROUPLET$0"
                    )
                )
            )
            travel_expense_tile.click()
            #time.sleep(2)
            
            travel_expense_user_setup=wait.until(
                EC.element_to_be_clickable(
                    (
                        By.ID,
                        "win0groupletPTNUI_LAND_REC_GROUPLET$0"
                    )
                )
            )
            travel_expense_user_setup.click()
            #time.sleep(2)
            review_edit_profile_tile=wait.until(
                EC.element_to_be_clickable(
                    (
                        By.ID,
                        "win0divPTNUI_LAND_REC_GROUPLET$1"
                    )
                )
            )
            review_edit_profile_tile.click()
            EXPECTED_MESSAGE = "You are not authorized to access this component"
            #EXPECTED_MESSAGE = "You are not authorized to access this component"

            if EXPECTED_MESSAGE.lower() in driver.page_source.lower():
                success("Reached Travel and Expense WorkCenter Page")
                driver.switch_to.default_content()
                ok_button = wait.until(
                    EC.element_to_be_clickable(
                        (
                            By.XPATH,
                            "//input[@id='#ICOK']"
                        )
                    )
                )

                # Highlight OK button

                driver.execute_script(
                    "arguments[0].style.border='5px solid blue'",
                    ok_button
                )

                #time.sleep(1)

                ok_button.click()

                #time.sleep(1)
                driver.switch_to.default_content()
                home_button=wait.until(
                EC.element_to_be_clickable(
                    (
                        By.ID,
                        "pthdr2home"
                    )))
                home_button.click()
                heading("Travel and Expense WorkCenter Page")
                success(" Travel and Expense WorkCenter Page successful")
                
                return True

            return False
        except Exception as e:

            print(f"Travel and Expense Workcenter Page Failed: {str(e)}")

            return False

def run_health_and_benefits(driver):
    try:
        if config.ENV_NAME in["ESSPU", "ESSPX","ESSPV", "ESSPT", "ESSPG", "ESSPPT"]:
            wait=WebDriverWait(driver, 30)
            driver.switch_to.default_content()
            health_benefits_tile=wait.until(
                EC.element_to_be_clickable(
                    (
                        By.ID,
                        "win0divPTNUI_LAND_REC_GROUPLET$3"
                    )
                )
            )
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            #driver.execute_script("arguments[0].scrollIntoView({block:'center'});",health_benefits_tile)
            driver.execute_script("arguments[0].click();",health_benefits_tile)
            #time.sleep(2)
            
            health_care_summary=wait.until(
                EC.element_to_be_clickable(
                    (
                        By.ID,
                        "win0divPTNUI_LAND_REC_GROUPLET$1"
                    )
                )
            )
            health_care_summary.click() 
            EXPECTED_MESSAGE = "You are not authorized to access this component"
            #EXPECTED_MESSAGE = "Operator ID not assigned to an employee" if config.ENV_NAME in ["ESSPL", "ESSPS"] else "You are not authorized to access this component"
            if EXPECTED_MESSAGE.lower() in driver.page_source.lower():
                success("Reached Health and Benefits WorkCenter Page")
                driver.switch_to.default_content()
                        

                ok_button = wait.until(
                    EC.element_to_be_clickable(
                        (
                            By.XPATH,
                            "//input[@id='#ICOK']"
                        )
                    )
                )

                # Highlight OK button

                driver.execute_script(
                    "arguments[0].style.border='5px solid blue'",
                    ok_button
                )

                #time.sleep(1)

                ok_button.click()

                #time.sleep(1)

                driver.switch_to.default_content()
                home_button=wait.until(
                EC.element_to_be_clickable(
                    (
                        By.ID,
                        "pthdr2home"
                    )))
                home_button.click()
                heading("Health and Benefits WorkCenter Page")
                success(" Health and Benefits Page successful")
                
                return True

            return False
    except Exception as e:

        print(f"Travel and Expense Workcenter Page Failed: {str(e)}")

        return False
        
def fscm_process_monitor_page(driver):
    

    try:
        if config.ENV_NAME in["ESSPI","ESSPG", "ESSPS", "ESSPL"]:
            wait = WebDriverWait(driver, 30)

            driver.switch_to.default_content()

            #print("Opening NavBar...")
            nav_bar = wait.until(
                EC.element_to_be_clickable((By.ID, "PT_NAVBAR"))
            )
            nav_bar.click()

            #print("Switching to NavBar iframe...")
            wait.until(
                EC.frame_to_be_available_and_switch_to_it(
                    (By.ID, "psNavBarIFrame")
                )
            )

            #print("Opening Menu...")
            nav_menu = wait.until(
                EC.element_to_be_clickable(
                    (By.ID, "grouplet_PTNB$PTNUI_NB_MENU")
                )
            )
            driver.execute_script("arguments[0].click();", nav_menu)

            #print("Opening FSCM...")
            fscm_menu = wait.until(
                EC.element_to_be_clickable(
                    (By.ID, "PTMENU_CNTREC_PTNUI_LINK$0")
                )
            )
            driver.execute_script("arguments[0].click();", fscm_menu)

            #print("Opening PeopleTools...")
            peopletools = wait.until(
                EC.element_to_be_clickable(
                    (
                        By.ID,
                        "PTMENUITEM$4"
                    )
                )
            )
            driver.execute_script(
                "arguments[0].scrollIntoView(true);",
                peopletools
            )
            driver.execute_script(
                "arguments[0].click();",
                peopletools
            )

            time.sleep(1)

            #print("Opening Process Scheduler...")
            process_scheduler = wait.until(
                EC.element_to_be_clickable(
                    (
                        By.ID,
                        "PTMENUITEM$0"
                    )
                )
            )

            driver.execute_script(
                "arguments[0].scrollIntoView(true);",
                process_scheduler
            )
            driver.execute_script(
                "arguments[0].click();",
                process_scheduler
            )

            time.sleep(1)

            #print("Refreshing iframe after menu expansion...")

            driver.switch_to.default_content()

            wait.until(
                EC.frame_to_be_available_and_switch_to_it(
                    (By.ID, "psNavBarIFrame")
                )
            )

            #print("Opening Process Monitor...")

            process_monitor = wait.until(
                EC.element_to_be_clickable(
                    (
                        By.ID,
                        "PTMENUITEM$0"
                    )
                )
            )

            driver.execute_script(
                "arguments[0].scrollIntoView(true);",
                process_monitor
            )

            driver.execute_script(
                "arguments[0].click();",
                process_monitor
            )

            #print("Waiting for Process Monitor page...")

            driver.switch_to.default_content()
            EXPECTED_MESSAGE = "view process requests"

            if EXPECTED_MESSAGE.lower() in driver.page_source.lower():
                success("Reached FSCM Process Monitor Page")
                driver.switch_to.default_content()

            home_button = wait.until(
                EC.element_to_be_clickable(
                    (By.ID, "pthdr2home")
                )
            )

            home_button.click()
            heading("FSCM Process Monitor Page")
            success(" Successfully Validated FSCM Process Monitor Page")

            return True

    except Exception as e:
        print(f"Process Monitor Failed: {str(e)}")
        print("Current URL:", driver.current_url)
        print("Title:", driver.title)
        return False
    

def hcm_process_monitor_page(driver):
    #if config.ENV_NAME in["ESSPI", "ESSPPT","ESSPG", "ESSPS", "ESSPL"]:
    try:
        if config.ENV_NAME in["ESSPI","ESSPG", "ESSPS", "ESSPL"]:
            wait = WebDriverWait(driver, 30)

            driver.switch_to.default_content()

            # =====================================
            # OPEN NAVBAR
            # =====================================
            nav_bar = wait.until(
                EC.element_to_be_clickable(
                    (By.ID, "PT_NAVBAR")
                )
            )

            driver.execute_script(
                "arguments[0].click();",
                nav_bar
            )
            time.sleep(1)

            # =====================================
            # OPEN NAVBAR IFRAME
            # =====================================
            wait.until(
                EC.frame_to_be_available_and_switch_to_it(
                    (By.ID, "psNavBarIFrame")
                )
            )
            time.sleep(1)
        
            # =====================================
            # OPEN MENU
            # =====================================
            nav_menu = wait.until(
                EC.element_to_be_clickable(
                    (
                        By.ID,
                        "grouplet_PTNB$PTNUI_NB_MENU"
                    )
                )
            )

            driver.execute_script(
                "arguments[0].click();",
                nav_menu
            )
            time.sleep(1)
            
            # =====================================
            # CLICK MENU LINK
            # =====================================
            menu_link = wait.until(
                EC.element_to_be_clickable(
                    (
                        By.ID,
                        "bc0_PORTAL_ROOT_OBJECT"
                    )
                )
            )

            driver.execute_script(
                "arguments[0].click();",
                menu_link
            )
            time.sleep(1)
            
            
            # =====================================
            # SELECT HCM
            # =====================================
            hcm_menu = wait.until(
                EC.element_to_be_clickable(
                    (
                        By.ID,
                        "PTMENU_CNTREC_PTNUI_LINK$1"
                    )
                )
            )

            driver.execute_script(
                "arguments[0].click();",
                hcm_menu
            )
            time.sleep(1)

        

            # =====================================
            # PEOPLETOOLS
            # =====================================
            peopletools = wait.until(
                EC.element_to_be_clickable(
                    (
                        By.ID,
                        "PTMENUITEM$4"
                    )
                )
            )

            driver.execute_script(
                "arguments[0].scrollIntoView({block:'center'});",
                peopletools
            )

            driver.execute_script(
                "arguments[0].click();",
                peopletools
            )
            time.sleep(1)

            # =====================================
            # PROCESS SCHEDULER
            # =====================================
            process_scheduler = wait.until(
                EC.element_to_be_clickable(
                    (
                        By.ID,
                        "PTMENUITEM$0"
                    )
                )
            )

            driver.execute_script(
                "arguments[0].scrollIntoView({block:'center'});",
                process_scheduler
            )

            driver.execute_script(
                "arguments[0].click();",
                process_scheduler
            )
            time.sleep(1)

            # =====================================
            # PROCESS MONITOR
            # =====================================
            
            driver.switch_to.default_content()

            wait.until(
                EC.frame_to_be_available_and_switch_to_it(
                    (By.ID, "psNavBarIFrame")
                )
            )

            process_monitor = wait.until(
                EC.element_to_be_clickable(
                    (
                        By.ID,
                        "PTMENUITEM$0"
                    )
                )
            )

            driver.execute_script(
                "arguments[0].scrollIntoView({block:'center'});",
                process_monitor
            )

            driver.execute_script(
                "arguments[0].click();",
                process_monitor
            )

            # =====================================
            # VALIDATE PROCESS MONITOR
            # =====================================
            driver.switch_to.default_content()

            EXPECTED_MESSAGE = "view process requests"

            if EXPECTED_MESSAGE.lower() in driver.page_source.lower():
                success("Reached HCM Process Monitor Page")
                driver.switch_to.default_content()

            

            # =====================================
            # RETURN HOME
            # =====================================
            home_button = wait.until(
                EC.element_to_be_clickable(
                    (By.ID, "pthdr2home")
                )
            )

            home_button.click()
            heading("HCM Process Monitor Page")
            success(" Successfully Validated HCM Process Monitor Page")

            return True

    except Exception as e:
        print(
            f"HCM Process Monitor Failed: {str(e)}"
        )
        print("Current URL:", driver.current_url)
        print("Title:", driver.title)
        driver.switch_to.default_content()
        return False


def run_logout(driver):

    try:

        wait = WebDriverWait(driver, 30)
        
        driver.switch_to.default_content()
        actions_btn = wait.until(
            EC.element_to_be_clickable(
                (
                    By.ID,
                    "PT_ACTION_MENU$PIMG"
                )
            )
        )
        actions_btn.click()
        #print("Actions menu clicked")
        #time.sleep(2)
    
        logout_btn = wait.until(
            EC.element_to_be_clickable(
                (
                    By.ID,
                    "PT_LOGOUT_MENU"
                )
            )
        )
        heading("LOGOUT")
            
        logout_btn.click()
        success("Logout Successfully")
        return True

    except Exception as e:

        print(f"Logout Failed: {str(e)}")

        return False


def fmp(driver):
    if config.ENV_NAME not in ["ESSPT"]:
        try:
            
            wait = WebDriverWait(driver, 30)
            
            driver.switch_to.default_content()
            fmp_link = wait.until(
                EC.element_to_be_clickable(
                    (
                        By.XPATH, "//*[@id='localLoginSection']/div[5]/span/p/a"
                    )
                )
            )
            fmp_link.click()
            #print("Actions menu clicked")
            actions_btn = wait.until(
                EC.element_to_be_clickable(
                    (
                        By.ID,
                        "PT_ACTION_MENU$PIMG"
                    )
                )
            )
            actions_btn.click()
            #time.sleep(2)
            logout_btn = wait.until(
                EC.element_to_be_clickable(
                    (
                        By.ID,
                        "PT_LOGOUT_MENU"
                    )
                )
            )
            heading("FMP LOGOUT")
            
            logout_btn.click()
            success("FMP Logout Successfully")
            return True

        except Exception as e:

            print(f"FMP Logout Failed: {str(e)}")

            return False
