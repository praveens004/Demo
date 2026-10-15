import os
import re
import html
import smtplib
 
from email.message import EmailMessage
from dotenv import load_dotenv
 
 
load_dotenv()
 
 
# ============================================================
# REMOVE ANSI COLOR CODES
# ============================================================
 
def remove_ansi_codes(text):
 
    """
    Remove terminal ANSI color/control sequences
    before displaying console output in email.
    """
 
    if not text:
        return ""
 
    ansi_escape = re.compile(
        r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])'
    )
 
    return ansi_escape.sub("", text)
 
 
# ============================================================
# SEND IVT EMAIL
# ============================================================
 
def send_ivt_email(
    environment,
    results,
    execution_time,
    console_output="",
    validation_details=None
):
 
    # ========================================================
    # SMTP CONFIGURATION
    # ========================================================
 
    SMTP_HOST = os.getenv("SMTP_HOST")
    SMTP_PORT = int(os.getenv("SMTP_PORT", "25"))
    FROM_EMAIL = os.getenv("FROM_EMAIL")
    TO_EMAIL = os.getenv("TO_EMAIL")
 
    # ========================================================
    # VALIDATE SMTP CONFIGURATION
    # ========================================================
 
    if not SMTP_HOST:
        raise Exception(
            "SMTP_HOST is not configured"
        )
 
    if not FROM_EMAIL:
        raise Exception(
            "FROM_EMAIL is not configured"
        )
 
    if not TO_EMAIL:
        raise Exception(
            "TO_EMAIL is not configured"
        )
 
    recipients = [
        email.strip()
        for email in TO_EMAIL.split(",")
        if email.strip()
    ]
 
    if not recipients:
        raise Exception(
            "No valid TO_EMAIL recipients configured"
        )
 
    # ========================================================
    # VALIDATION DETAILS
    # ========================================================
 
    if validation_details is None:
 
        validation_details = []
 
        for test_name, result in results.items():
 
            validation_details.append({
                "Environment": test_name,
                "Duration": execution_time,
                "Status": result
            })
 
    # ========================================================
    # CALCULATE SUMMARY
    # ========================================================
 
    passed_tests = [
        test_name
        for test_name, result in results.items()
        if result
    ]
 
    failed_tests = [
        test_name
        for test_name, result in results.items()
        if not result
    ]
 
    total_tests = len(results)
 
    passed_count = len(passed_tests)
 
    failed_count = len(failed_tests)
 
    overall_passed = failed_count == 0
 
    # ========================================================
    # PASS RATE
    # ========================================================
 
    if total_tests > 0:
 
        pass_rate = round(
            (passed_count / total_tests) * 100
        )
 
    else:
 
        pass_rate = 0
 
    # ========================================================
    # CLEAN CONSOLE OUTPUT
    # ========================================================
 
    clean_console = remove_ansi_codes(
        console_output
    )
 
    safe_console = html.escape(
        clean_console
        if clean_console
        else "Console output not available."
    )
 
    # ========================================================
    # OVERALL STATUS
    # ========================================================
 
    if overall_passed:
 
        overall_color = "#198754"
        overall_bg = "#e8f5e9"
        overall_status = "PASSED"
        overall_icon = "✓"
 
    else:
 
        overall_color = "#dc3545"
        overall_bg = "#fdecec"
        overall_status = "FAILED"
        overall_icon = "✕"
 
    # ========================================================
    # VALIDATION RESULT ROWS
    # ========================================================
 
    validation_rows = ""
 
    for item in validation_details:
 
        application_environment = item.get(
            "Environment",
            ""
        )
 
        duration = item.get(
            "Duration",
            ""
        )
 
        result = item.get(
            "Status",
            False
        )
 
        # ----------------------------------------------------
        # STATUS
        # ----------------------------------------------------
 
        if result:
 
            status = "PASSED"
            status_color = "#198754"
            status_bg = "#e8f5e9"
            icon = "✓"
 
        else:
 
            status = "FAILED"
            status_color = "#dc3545"
            status_bg = "#fdecec"
            icon = "✕"
 
        # ----------------------------------------------------
        # TABLE ROW
        # ----------------------------------------------------
 
        validation_rows += f"""
<tr>
 
            <!-- APPLICATION / ENVIRONMENT -->
 
            <td style="
                padding:14px 16px;
                border-bottom:1px solid #eef0f2;
                color:#111827;
                font-size:14px;
                font-weight:600;
                text-align:left;
            ">
 
                {html.escape(
                    str(application_environment)
                )}
 
            </td>
 
 
            <!-- DURATION -->
 
            <td style="
                padding:14px 16px;
                border-bottom:1px solid #eef0f2;
                color:#6b7280;
                font-size:13px;
                text-align:center;
                white-space:nowrap;
            ">
 
                {html.escape(
                    str(duration)
                )}
 
            </td>
 
 
            <!-- STATUS -->
 
            <td style="
                padding:14px 16px;
                border-bottom:1px solid #eef0f2;
                text-align:right;
            ">
 
                <span style="
                    display:inline-block;
                    padding:6px 13px;
                    border-radius:20px;
                    background:{status_bg};
                    color:{status_color};
                    font-weight:700;
                    font-size:12px;
                    white-space:nowrap;
                ">
 
                    {icon} {status}
 
                </span>
 
            </td>
 
        </tr>
        """
 
    # ========================================================
    # HTML EMAIL
    # ========================================================
 
    html_body = f"""
<!DOCTYPE html>
 
<html>
 
<head>
 
<meta charset="UTF-8">
 
<meta
    name="viewport"
    content="width=device-width, initial-scale=1.0"
>
 
<title>
    PeopleSoft IVT Automation Report
</title>
 
</head>
 
 
<body style="
    margin:0;
    padding:0;
    background:#f3f5f7;
    font-family:Arial,Helvetica,sans-serif;
">
 
 
<table
    width="100%"
    cellpadding="0"
    cellspacing="0"
    border="0"
    style="
        background:#f3f5f7;
        padding:30px 10px;
    "
>
 
<tr>
 
<td align="center">
 
 
<!-- ====================================================== -->
<!-- MAIN CONTAINER -->
<!-- ====================================================== -->
 
<table
    width="720"
    cellpadding="0"
    cellspacing="0"
    border="0"
    style="
        max-width:720px;
        width:100%;
        background:#ffffff;
        border-radius:12px;
        overflow:hidden;
        box-shadow:0 3px 12px rgba(0,0,0,0.08);
    "
>
 
 
<!-- ====================================================== -->
<!-- HEADER -->
<!-- ====================================================== -->
 
<tr>
 
<td style="
    background:#1f2937;
    padding:26px 30px;
    color:#ffffff;
">
 
    <div style="
        font-size:23px;
        font-weight:700;
        letter-spacing:-0.3px;
    ">
 
        PeopleSoft IVT Automation
 
    </div>
 
 
    <div style="
        margin-top:6px;
        font-size:13px;
        color:#d1d5db;
    ">
 
        Automated Validation Execution Report
 
    </div>
 
</td>
 
</tr>
 
 
<!-- ====================================================== -->
<!-- APPLICATION / ENVIRONMENT -->
<!-- ====================================================== -->
 
<tr>
 
<td style="
    padding:26px 30px 12px 30px;
">
 
 
<table
    width="100%"
    cellpadding="0"
    cellspacing="0"
>
 
 
<tr>
 
 
<td>
 
    <div style="
        font-size:11px;
        color:#6b7280;
        text-transform:uppercase;
        letter-spacing:0.5px;
    ">
 
        Application / Environment
 
    </div>
 
 
    <div style="
        margin-top:6px;
        font-size:19px;
        font-weight:700;
        color:#111827;
    ">
 
        {html.escape(str(environment))}
 
    </div>
 
</td>
 
 
<td align="right">
 
    <span style="
        display:inline-block;
        padding:7px 15px;
        border-radius:20px;
        background:{overall_bg};
        color:{overall_color};
        font-size:13px;
        font-weight:700;
        white-space:nowrap;
    ">
 
        {overall_icon} {overall_status}
 
    </span>
 
</td>
 
 
</tr>
 
 
</table>
 
</td>
 
</tr>
 
 
<!-- ====================================================== -->
<!-- SUMMARY CARDS -->
<!-- ====================================================== -->
 
<tr>
 
<td style="
    padding:10px 30px 26px 30px;
">
 
 
<table
    width="100%"
    cellpadding="0"
    cellspacing="8"
>
 
 
<tr>
 
 
<!-- TOTAL TESTS -->
 
<td
    width="25%"
    style="
        background:#f8fafc;
        border:1px solid #e5e7eb;
        border-radius:9px;
        padding:16px 8px;
        text-align:center;
    "
>
 
    <div style="
        font-size:27px;
        font-weight:700;
        color:#111827;
    ">
 
        {total_tests}
 
    </div>
 
 
    <div style="
        margin-top:5px;
        font-size:10px;
        font-weight:600;
        color:#6b7280;
        letter-spacing:0.4px;
    ">
 
        TOTAL TESTS
 
    </div>
 
</td>
 
 
<!-- PASSED -->
 
<td
    width="25%"
    style="
        background:#eaf7ee;
        border:1px solid #ccebd5;
        border-radius:9px;
        padding:16px 8px;
        text-align:center;
    "
>
 
    <div style="
        font-size:27px;
        font-weight:700;
        color:#198754;
    ">
 
        {passed_count}
 
    </div>
 
 
    <div style="
        margin-top:5px;
        font-size:10px;
        font-weight:600;
        color:#198754;
        letter-spacing:0.4px;
    ">
 
        PASSED
 
    </div>
 
</td>
 
 
<!-- FAILED -->
 
<td
    width="25%"
    style="
        background:#fff0f0;
        border:1px solid #f5cccc;
        border-radius:9px;
        padding:16px 8px;
        text-align:center;
    "
>
 
    <div style="
        font-size:27px;
        font-weight:700;
        color:#dc3545;
    ">
 
        {failed_count}
 
    </div>
 
 
    <div style="
        margin-top:5px;
        font-size:10px;
        font-weight:600;
        color:#dc3545;
        letter-spacing:0.4px;
    ">
 
        FAILED
 
    </div>
 
</td>
 
 
<!-- PASS RATE -->
 
<td
    width="25%"
    style="
        background:#eef4ff;
        border:1px solid #d7e3ff;
        border-radius:9px;
        padding:16px 8px;
        text-align:center;
    "
>
 
    <div style="
        font-size:27px;
        font-weight:700;
        color:#2563eb;
    ">
 
        {pass_rate}%
 
    </div>
 
 
    <div style="
        margin-top:5px;
        font-size:10px;
        font-weight:600;
        color:#2563eb;
        letter-spacing:0.4px;
    ">
 
        PASS RATE
 
    </div>
 
</td>
 
 
</tr>
 
</table>
 
</td>
 
</tr>
 
 
<!-- ====================================================== -->
<!-- EXECUTION INFORMATION -->
<!-- ====================================================== -->
 
<tr>
 
<td style="
    padding:0 30px 26px 30px;
">
 
 
<div style="
    font-size:17px;
    font-weight:700;
    color:#111827;
    margin-bottom:12px;
">
 
    Execution Details
 
</div>
 
 
<table
    width="100%"
    cellpadding="0"
    cellspacing="0"
    style="
        border:1px solid #e5e7eb;
        border-radius:9px;
        overflow:hidden;
    "
>
 
 
<tr>
 
 
<td style="
    padding:13px 16px;
    color:#6b7280;
    font-size:13px;
    border-bottom:1px solid #eef0f2;
">
 
    Execution Time
 
</td>
 
 
<td
    align="right"
    style="
        padding:13px 16px;
        color:#111827;
        font-size:13px;
        font-weight:700;
        border-bottom:1px solid #eef0f2;
    "
>
 
    {html.escape(str(execution_time))}
 
</td>
 
 
</tr>
 
 
<tr>
 
 
<td style="
    padding:13px 16px;
    color:#6b7280;
    font-size:13px;
">
 
    Overall Result
 
</td>
 
 
<td
    align="right"
    style="
        padding:13px 16px;
        color:{overall_color};
        font-size:13px;
        font-weight:700;
    "
>
 
    {overall_icon} {overall_status}
 
</td>
 
 
</tr>
 
 
</table>
 
</td>
 
</tr>
 
 
<!-- ====================================================== -->
<!-- VALIDATION RESULTS -->
<!-- ====================================================== -->
 
<tr>
 
<td style="
    padding:0 30px 26px 30px;
">
 
 
<div style="
    font-size:17px;
    font-weight:700;
    color:#111827;
    margin-bottom:12px;
">
 
    Validation Results
 
</div>
 
 
<table
    width="100%"
    cellpadding="0"
    cellspacing="0"
    border="0"
    style="
        border:1px solid #e5e7eb;
        border-radius:9px;
        overflow:hidden;
    "
>
 
 
<!-- TABLE HEADER -->
 
<tr style="
    background:#f8fafc;
">
 
 
<!-- APPLICATION / ENVIRONMENT HEADER -->
 
<th
    align="left"
    style="
        padding:12px 16px;
        font-size:10px;
        color:#6b7280;
        text-transform:uppercase;
    "
>
 
    Application / Environment
 
</th>
 
 
<!-- DURATION HEADER -->
 
<th
    align="center"
    style="
        padding:12px 16px;
        font-size:10px;
        color:#6b7280;
        text-transform:uppercase;
        width:120px;
    "
>
 
    Duration
 
</th>
 
 
<!-- STATUS HEADER -->
 
<th
    align="right"
    style="
        padding:12px 16px;
        font-size:10px;
        color:#6b7280;
        text-transform:uppercase;
        width:100px;
    "
>
 
    Status
 
</th>
 
 
</tr>
 
 
{validation_rows}
 
 
</table>
 
</td>
 
</tr>
 
 
<!-- ====================================================== -->
<!-- EXECUTION LOG -->
<!-- ====================================================== -->
 
<tr>
 
<td style="
    padding:0 30px 30px 30px;
">
 
 
<div style="
    font-size:17px;
    font-weight:700;
    color:#111827;
    margin-bottom:5px;
">
 
    Execution Log
 
</div>
 
 
<div style="
    font-size:11px;
    color:#6b7280;
    margin-bottom:12px;
">
 
    Detailed console output from the IVT execution
 
</div>
 
 
<pre style="
    margin:0;
    padding:18px;
    background:#111827;
    color:#d1d5db;
    border-radius:9px;
    font-family:Consolas,'Courier New',monospace;
    font-size:11px;
    line-height:1.55;
    white-space:pre-wrap;
    word-break:break-word;
    overflow-wrap:anywhere;
">{safe_console}</pre>
 
 
</td>
 
</tr>
 
 
<!-- ====================================================== -->
<!-- FOOTER -->
<!-- ====================================================== -->
 
<tr>
 
<td style="
    background:#f8fafc;
    border-top:1px solid #eef0f2;
    padding:18px 30px;
    text-align:center;
">
 
 
<div style="
    font-size:11px;
    color:#6b7280;
">
 
    This is an automated message generated by
 
</div>
 
 
<div style="
    margin-top:3px;
    font-size:11px;
    font-weight:600;
    color:#374151;
">
 
    PeopleSoft IVT Automation Framework
 
</div>
 
 
</td>
 
</tr>
 
 
</table>
 
</td>
 
</tr>
 
</table>
 
</body>
 
</html>
"""
 
    # ========================================================
    # PLAIN TEXT FALLBACK
    # ========================================================
 
    plain_body = f"""
 
PeopleSoft IVT Automation Execution Summary
 
Application / Environment : {environment}
 
Execution Time            : {execution_time}
 
Overall Status            : {overall_status}
 
Total Tests               : {total_tests}
 
Passed                    : {passed_count}
 
Failed                    : {failed_count}
 
Pass Rate                 : {pass_rate}%
 
==================================================
VALIDATION RESULTS
==================================================
 
"""
 
    for item in validation_details:
 
        application_environment = item.get(
            "Environment",
            ""
        )
 
        duration = item.get(
            "Duration",
            ""
        )
 
        result = item.get(
            "Status",
            False
        )
 
        status = (
            "PASSED"
            if result
            else "FAILED"
        )
 
        plain_body += (
            f"Application / Environment : "
            f"{application_environment}\n"
            f"Duration                  : "
            f"{duration}\n"
            f"Status                    : "
            f"{status}\n\n"
        )
 
    plain_body += """
 
==================================================
EXECUTION LOG
==================================================
 
"""
 
    plain_body += (
        clean_console
        if clean_console
        else "Console output not available."
    )
 
    # ========================================================
    # CREATE EMAIL
    # ========================================================
 
    message = EmailMessage()
 
    message["Subject"] = (
        f"PeopleSoft IVT Automation - "
        f"{environment} - "
        f"{overall_status}"
    )
 
    message["From"] = FROM_EMAIL
 
    message["To"] = ", ".join(
        recipients
    )
 
    # ========================================================
    # PLAIN TEXT VERSION
    # ========================================================
 
    message.set_content(
        plain_body
    )
 
    # ========================================================
    # HTML VERSION
    # ========================================================
 
    message.add_alternative(
        html_body,
        subtype="html"
    )
 
    # ========================================================
    # SEND EMAIL
    # ========================================================
 
    try:
 
        print(
            f"Connecting to SMTP server: "
            f"{SMTP_HOST}:{SMTP_PORT}"
        )
 
        with smtplib.SMTP(
            SMTP_HOST,
            SMTP_PORT,
            timeout=30
        ) as server:
 
            server.send_message(
                message
            )
 
        print(
            "IVT email sent successfully"
        )
 
    except Exception as e:
 
        print(
            f"Failed to send IVT email: {e}"
        )
 
        raise
 
 
# ============================================================
# CONSOLIDATED EMAIL
# ============================================================
 
def send_consolidated_email(
    all_results,overall_execution_time
):
 
    consolidated_results = {}
 
    validation_details = []
 
    all_logs = ""
 
    # ========================================================
    # COMBINE RESULTS
    # ========================================================
 
    for result in all_results:
 
        application_environment = result[
            "Environment"
        ]
 
        execution_time = result[
            "ExecutionTime"
        ]
 
        status = (
            result["Status"] == "PASS"
        )
 
        # ----------------------------------------------------
        # SUMMARY DATA
        # ----------------------------------------------------
 
        consolidated_results[
            application_environment
        ] = status
 
        # ----------------------------------------------------
        # DETAILED TABLE DATA
        # ----------------------------------------------------
 
        validation_details.append({
 
            "Environment":
                application_environment,
 
            "Duration":
                execution_time,
 
            "Status":
                status
 
        })
 
        # ----------------------------------------------------
        # CONSOLE LOG
        # ----------------------------------------------------
 
        all_logs += (
            f"\n{'=' * 60}\n"
            f"{application_environment}\n"
            f"{'=' * 60}\n"
        )
 
        all_logs += result.get(
            "Log",
            "No log available"
        )
 
        all_logs += "\n\n"
 
    # ========================================================
    # SEND CONSOLIDATED EMAIL
    # ========================================================
 
    send_ivt_email(
 
        environment="SDCOE Non-Production ESS Environments",
 
        results=consolidated_results,
 
        execution_time=f"\nTotal Execution Time : {overall_execution_time}\n\n",
 
        console_output=all_logs,
 
        validation_details=validation_details
 
    )