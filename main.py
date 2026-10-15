from environments import APPLICATIONS
from run_all_test import run_application
from common import get_credentials
from console import *
from email_utils import send_consolidated_email
from getpass import getpass
import time


results = []

username, common_password = get_credentials()

# sjho92_username = input("Enter User ID for SJHO92: ")
# sjho92_password = getpass("Enter Password for SJHO92: ")

for app in APPLICATIONS:

    result = run_application(app, username, common_password)

    results.append(result)

# End total execution timer
# Calculate total execution time from environment execution times
total_seconds = 0

for result in results:
    h, m, s = map(int, result["ExecutionTime"].split(":"))
    total_seconds += (h * 3600) + (m * 60) + s

hours = total_seconds // 3600
minutes = (total_seconds % 3600) // 60
seconds = total_seconds % 60

overall_execution_time = (
    f"{hours:02d}:{minutes:02d}:{seconds:02d}"
)

print("\n")

heading("OVERALL IVT SUMMARY")

for result in results:

    if result["Status"] == "PASS":

        success(
            f"{result['Environment']:<10} "
            f"{result['ExecutionTime']}"
        )

    else:

        error(
            f"{result['Environment']:<10} "
            f"{result['ExecutionTime']}"
        )

print("")
info(f"TOTAL EXECUTION TIME : {overall_execution_time}")

try:

    send_consolidated_email(results, overall_execution_time)

except Exception as e:

    print(
        f"Email failed : {str(e)}"
    )