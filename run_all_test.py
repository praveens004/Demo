from common import get_driver, login, run_travel_expense_page, run_health_and_benefits,fscm_process_monitor_page,hcm_process_monitor_page, run_logout, fmp, get_credentials,verify_session
from report_utils import save_report
from console import *
from getpass import getpass

import traceback
import time
import config


def run_application(app, username, common_password):
    results={}
    driver=None

    config.PIA_URL = app["url"]
    config.ENV_NAME = app["name"]

    start_time = time.time()

    info(f"\nStarting {app['name']}")
    
    if app["name"] == "SJHO92":
        current_username = sjho92_username
        current_password = sjho92_password
    else:
        current_username = username
        current_password = common_password
    info(f"Logged User : {current_username}")

    try:

        driver = get_driver()
        driver.maximize_window()

        try:

            results["Login Check"] = login(driver, current_username, current_password)
            if config.ENV_NAME in ["ESSPU", "ESSPX","ESSPV", "ESSPT", "ESSPG","ESSPPT"]:
                verify_session(driver, current_username, current_password)
                results["Travel and Expense WorkCenetr"]=run_travel_expense_page(driver)
                results["Health and Benefits WorkCenetr"]=run_health_and_benefits(driver)
            if config.ENV_NAME in ["ESSPI","ESSPG", "ESSPS", "ESSPL"]:
                verify_session(driver, current_username, current_password)
                results["FSCM Process Monitor"]=fscm_process_monitor_page(driver)
                results["HCM Process Monitor"]=hcm_process_monitor_page(driver)
            results["Logout Check"] = run_logout(driver)
            if config.ENV_NAME not in ["ESSPT"]:
                results["FMP Logout Check"] = fmp(driver)

        except Exception:

            traceback.print_exc()

            results["Login/Logout"] = False
            results["Travel and Expense WorkCenetr"]=False

        # =========================
        # COMBINED IVT SUMMARY
        # =========================

        end_time = time.time()

        total_seconds = int(end_time - start_time)

        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        seconds = total_seconds % 60

        execution_time = (
            f"{hours:02d}:"
            f"{minutes:02d}:"
            f"{seconds:02d}"
        )

        

        heading(f"{app['name']} - IVT SUMMARY")

        

        info(
            f"Execution Time : {execution_time}"
        )

        print("")

        overall_status = True

        for test_name, result in results.items():

            if result:
                success(f"{test_name:<30} PASSED")
            else:
                error(f"{test_name:<30} FAILED")
                overall_status = False

        # Build log text
        log_text = f"""
        {app['name']} - IVT SUMMARY
        Execution Time : {execution_time}

        """

        for test_name, result in results.items():
            log_text += f"{test_name} : {'PASSED' if result else 'FAILED'}\n"

        return {
            "Environment": app["name"],
            "Status": "PASS" if overall_status else "FAIL",
            "ExecutionTime": execution_time,
            "Results": results,
            "Log": log_text
        }
        
    finally:

        # save_report()

        if driver:
            driver.quit()