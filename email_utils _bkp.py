import os
import re
import html
import smtplib
from email.message import EmailMessage
from dotenv import load_dotenv


load_dotenv()


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


def send_ivt_email(
    environment,
    results,
    execution_time,
    console_output=""
):

    SMTP_HOST = os.getenv("SMTP_HOST")
    SMTP_PORT = int(os.getenv("SMTP_PORT", "25"))

    FROM_EMAIL = os.getenv("FROM_EMAIL")
    TO_EMAIL = os.getenv("TO_EMAIL")

    # ==========================================
    # VALIDATE SMTP CONFIGURATION
    # ==========================================

    if not SMTP_HOST:
        raise Exception("SMTP_HOST is not configured")

    if not FROM_EMAIL:
        raise Exception("FROM_EMAIL is not configured")

    if not TO_EMAIL:
        raise Exception("TO_EMAIL is not configured")

    recipients = [
        email.strip()
        for email in TO_EMAIL.split(",")
        if email.strip()
    ]

    # ==========================================
    # CALCULATE SUMMARY
    # ==========================================

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

    # ==========================================
    # CLEAN CONSOLE OUTPUT
    # ==========================================

    clean_console = remove_ansi_codes(console_output)

    # Escape HTML characters
    safe_console = html.escape(clean_console)

    # ==========================================
    # STATUS COLORS
    # ==========================================

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

    # ==========================================
    # VALIDATION RESULT ROWS
    # ==========================================

    validation_rows = ""

    for test_name, result in results.items():

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

        validation_rows += f"""
        <tr>
            <td style="
                padding:12px 16px;
                border-bottom:1px solid #e9ecef;
                color:#212529;
                font-size:14px;
            ">
                {html.escape(test_name)}
            </td>

            <td style="
                padding:12px 16px;
                border-bottom:1px solid #e9ecef;
                text-align:right;
            ">
                <span style="
                    display:inline-block;
                    padding:5px 12px;
                    border-radius:20px;
                    background:{status_bg};
                    color:{status_color};
                    font-weight:600;
                    font-size:12px;
                ">
                    {icon} {status}
                </span>
            </td>
        </tr>
        """

    # ==========================================
    # HTML EMAIL
    # ==========================================

    html_body = f"""
<!DOCTYPE html>

<html>

<head>

<meta charset="UTF-8">

<meta name="viewport" content="width=device-width, initial-scale=1.0">

<title>PeopleSoft IVT Automation Report</title>

</head>

<body style="
    margin:0;
    padding:0;
    background:#f4f6f8;
    font-family:Arial,Helvetica,sans-serif;
">

<table width="100%" cellpadding="0" cellspacing="0"
       style="background:#f4f6f8;padding:30px 10px;">

<tr>

<td align="center">

<table width="700" cellpadding="0" cellspacing="0"
       style="
           max-width:700px;
           width:100%;
           background:#ffffff;
           border-radius:10px;
           overflow:hidden;
           box-shadow:0 2px 8px rgba(0,0,0,0.08);
       ">

<!-- ========================================== -->
<!-- HEADER -->
<!-- ========================================== -->

<tr>

<td style="
    background:#1f2937;
    padding:25px 30px;
    color:#ffffff;
">

<div style="
    font-size:22px;
    font-weight:700;
">
    PeopleSoft IVT Automation
</div>

<div style="
    margin-top:5px;
    font-size:13px;
    color:#d1d5db;
">
    Execution Summary
</div>

</td>

</tr>


<!-- ========================================== -->
<!-- ENVIRONMENT -->
<!-- ========================================== -->

<tr>

<td style="padding:25px 30px 10px 30px;">

<table width="100%">

<tr>

<td>

<div style="
    font-size:12px;
    color:#6b7280;
    text-transform:uppercase;
">
    Environment
</div>

<div style="
    margin-top:5px;
    font-size:18px;
    font-weight:600;
    color:#111827;
">
    {html.escape(str(environment))}
</div>

</td>

<td align="right">

<span style="
    display:inline-block;
    padding:6px 14px;
    border-radius:20px;
    background:{overall_bg};
    color:{overall_color};
    font-size:13px;
    font-weight:700;
">
    {overall_icon} {overall_status}
</span>

</td>

</tr>

</table>

</td>

</tr>


<!-- ========================================== -->
<!-- SUMMARY CARDS -->
<!-- ========================================== -->

<tr>

<td style="padding:10px 30px 25px 30px;">

<table width="100%" cellpadding="0" cellspacing="8">

<tr>

<td width="33%" style="
    background:#f8f9fa;
    border:1px solid #e9ecef;
    border-radius:8px;
    padding:18px;
    text-align:center;
">

<div style="
    font-size:28px;
    font-weight:700;
    color:#212529;
">
    {total_tests}
</div>

<div style="
    margin-top:5px;
    font-size:12px;
    color:#6c757d;
">
    TOTAL TESTS
</div>

</td>


<td width="33%" style="
    background:#e8f5e9;
    border:1px solid #c8e6c9;
    border-radius:8px;
    padding:18px;
    text-align:center;
">

<div style="
    font-size:28px;
    font-weight:700;
    color:#198754;
">
    {passed_count}
</div>

<div style="
    margin-top:5px;
    font-size:12px;
    color:#198754;
">
    PASSED
</div>

</td>


<td width="33%" style="
    background:#fdecec;
    border:1px solid #f5c2c7;
    border-radius:8px;
    padding:18px;
    text-align:center;
">

<div style="
    font-size:28px;
    font-weight:700;
    color:#dc3545;
">
    {failed_count}
</div>

<div style="
    margin-top:5px;
    font-size:12px;
    color:#dc3545;
">
    FAILED
</div>

</td>

</tr>

</table>

</td>

</tr>


<!-- ========================================== -->
<!-- EXECUTION INFORMATION -->
<!-- ========================================== -->

<tr>

<td style="padding:0 30px 25px 30px;">

<table width="100%"
       style="
           border:1px solid #e9ecef;
           border-radius:8px;
           border-collapse:separate;
           overflow:hidden;
       ">

<tr>

<td style="
    padding:12px 16px;
    color:#6c757d;
    font-size:13px;
">
    Execution Time
</td>

<td style="
    padding:12px 16px;
    text-align:right;
    font-weight:600;
    color:#212529;
">
    {html.escape(str(execution_time))}
</td>

</tr>

</table>

</td>

</tr>


<!-- ========================================== -->
<!-- VALIDATION RESULTS -->
<!-- ========================================== -->

<tr>

<td style="padding:0 30px 25px 30px;">

<div style="
    font-size:17px;
    font-weight:700;
    color:#212529;
    margin-bottom:12px;
">
    Validation Results
</div>

<table width="100%"
       cellpadding="0"
       cellspacing="0"
       style="
           border:1px solid #e9ecef;
           border-radius:8px;
           overflow:hidden;
       ">

<tr style="background:#f8f9fa;">

<th align="left"
    style="
        padding:12px 16px;
        font-size:12px;
        color:#6c757d;
        text-transform:uppercase;
    ">
    Validation
</th>

<th align="right"
    style="
        padding:12px 16px;
        font-size:12px;
        color:#6c757d;
        text-transform:uppercase;
    ">
    Status
</th>

</tr>

{validation_rows}

</table>

</td>

</tr>


<!-- ========================================== -->
<!-- CONSOLE OUTPUT -->
<!-- ========================================== -->

<tr>

<td style="padding:0 30px 30px 30px;">

<div style="
    font-size:17px;
    font-weight:700;
    color:#212529;
    margin-bottom:12px;
">
    Execution Log
</div>

<pre style="
    margin:0;
    padding:18px;
    background:#111827;
    color:#d1d5db;
    border-radius:8px;
    font-family:Consolas,'Courier New',monospace;
    font-size:11px;
    line-height:1.5;
    white-space:pre-wrap;
    word-break:break-word;
    overflow-wrap:anywhere;
">{safe_console if safe_console else "Console output not available."}</pre>

</td>

</tr>


<!-- ========================================== -->
<!-- FOOTER -->
<!-- ========================================== -->

<tr>

<td style="
    background:#f8f9fa;
    padding:18px 30px;
    text-align:center;
    color:#6c757d;
    font-size:11px;
">

This is an automated message generated by the
PeopleSoft IVT Automation framework.

</td>

</tr>

</table>

</td>

</tr>

</table>

</body>

</html>
"""

    # ==========================================
    # PLAIN TEXT FALLBACK
    # ==========================================

    plain_body = f"""
PeopleSoft IVT Automation Execution Summary

Environment : {environment}
Execution Time : {execution_time}

Overall Status : {overall_status}

Total Tests : {total_tests}
Passed : {passed_count}
Failed : {failed_count}


VALIDATION RESULTS
========================================

"""

    for test_name, result in results.items():

        status = "PASSED" if result else "FAILED"

        plain_body += f"{test_name}: {status}\n"

    plain_body += """

========================================
EXECUTION LOG
========================================

"""

    plain_body += (
        clean_console
        if clean_console
        else "Console output not available."
    )

    # ==========================================
    # CREATE EMAIL
    # ==========================================

    message = EmailMessage()

    message["Subject"] = (
        f"PeopleSoft IVT Automation - "
        f"{environment} - "
        f"{overall_status}"
    )

    message["From"] = FROM_EMAIL
    message["To"] = ", ".join(recipients)

    # Plain text fallback
    message.set_content(plain_body)

    # HTML version
    message.add_alternative(
        html_body,
        subtype="html"
    )

    # ==========================================
    # SEND EMAIL
    # ==========================================

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

            server.send_message(message)

        print(
            "IVT email sent successfully"
        )

    except Exception as e:

        print(
            f"Failed to send IVT email: {e}"
        )

        raise
    
def send_consolidated_email(all_results):

    consolidated_results = {}
    all_logs = ""

    for result in all_results:

        consolidated_results[
            f"{result['Environment']} ({result['ExecutionTime']})"
        ] = (
            result["Status"] == "PASS"
        )

        all_logs += (
            f"\n{'=' * 60}\n"
            f"{result['Environment']}\n"
            f"{'=' * 60}\n"
        )

        all_logs += result.get(
            "Log",
            "No log available"
        )

        all_logs += "\n\n"

    send_ivt_email(
        environment="Candidate Gateway Portal",
        results=consolidated_results,
        execution_time="Completed",
        console_output=all_logs
    )