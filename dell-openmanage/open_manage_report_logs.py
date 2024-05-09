import os
import traceback
import sys
import time
import subprocess
import smtplib
import socket
import datetime
from dotenv import load_dotenv

load_dotenv()


def read_cli_log(severity: str = "", filter_from_date: str = "", debug: bool = False):
    """
    Read omreport

    severity can be:    Ok, Non-Critical, Critical
    """

    proc = subprocess.Popen("omreport system alertlog",
                            stderr=subprocess.PIPE,
                            stdout=subprocess.PIPE, shell=True,
                            universal_newlines=True)

    line_text = []
    line_char = []
    for c in iter(lambda: proc.stdout.read(1), ""):
        if c == "\n" or c == "\r":
            line_text.append("".join(line_char))
            line_char = []
        else:
            line_char.append(c)

    from_data = []
    if filter_from_date:
        # Ex: "Date and Time : Fri Mar 24 14:08:01 2023"
        from_date = datetime.datetime.strptime(filter_from_date, "%Y-%m-%d")
        from_data = from_date.strftime("%a %b %d %Y").split(" ")

    severity_line = "Severity      : "
    if severity:
        severity_line = f"Severity      : {severity}"

    result = []
    filter_line = []

    def _is_match_date(line_value):
        if from_data:
            if f"Date and Time : {from_data[0]} {from_data[1]} {from_data[2]}" in line and from_data[3] in line_value:
                return True
            return False
        return True

    def _is_match_severity(line_value):
        if severity_line in line_value:
            return True
        return False

    if debug:
        print("=== DEBUG VALUES ===")
        print(f"filter severity:\t[{severity_line}]")
        print(f"filter date:\t[{filter_from_date}] -- from_data: [{from_data}]")

    for line in line_text:
        if line:
            if debug:
                print("=== DEBUG ===")
                print(f"Line value:\t[{line}]")
                print(f"Filter severity:\t[{_is_match_severity(line)}]")
                print(f"Filter date:\t[{_is_match_date(line)}]")
                print("=== DEBUG END ===\n\n")
            if _is_match_severity(line):
                filter_line.append(line)
            elif filter_line and len(filter_line) < 5:
                if len(filter_line) == 2:
                    if _is_match_date(line):
                        filter_line.append(line)
                    else:
                        filter_line = []
                else:
                    filter_line.append(line)
                if len(filter_line) == 5:
                    result.append(filter_line)
                    filter_line = []
    if debug:
        print("=== DEBUG RESULT ==")
        print(result)
        print("=== DEBUG END ===")
    return result



def send_email(sender_address: str, to_address: str, subject: str, message: str):
    try:
        server = smtplib.SMTP("localhost", 25)
        server.sendmail(sender_address, [to_address], f"""Subject: {subject}\nTo: {to_address}\n\n\n{message}""")
    except Exception:
        if not os.path.isdir("logs"):
            os.mkdir("logs")
        with open(f"logs/error_log_{int(time.time())}.txt", "w+") as f:
            f.write(f"""=== ERROR ===
receiver: {to_address}
message: {message}

----- traceback -----
{traceback.format_exc()}
            """)


if __name__ == "__main__":
    allowed_severity = ('Ok', 'Critical', 'Non-Critical')
    _severity = ""
    if len(sys.argv) > 1:
        _severity = sys.argv[1]
        if _severity not in allowed_severity:
            print(f"- [ERROR] invalid severity value, allowed list: {allowed_severity}")
            exit(1)
    report_email = False
    is_debug = False
    filter_date = datetime.datetime.now().strftime("%Y-%m-%d")

    # example call params: python open_manage_report_logs.py Non-Critical debug 2024-05-09
    if len(sys.argv) > 2:
        report_email = sys.argv[2] == 'send-email'
        is_debug = sys.argv[2] == 'debug'
        if len(sys.argv) > 3:
            filter_date = sys.argv[3]

    output = read_cli_log(_severity, filter_date, debug=is_debug)
    output_str = ""
    for msg in output:
        output_str += (('' if not output_str else "\n\n") + "\n".join(msg))
    if report_email:
        sender_addr = os.getenv('SENDER_EMAIL')
        receiver_addr = os.getenv('RECEIVER_EMAIL')
        dt_now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
        if sender_addr and receiver_addr:
            if output_str:
                send_email(sender_addr, receiver_addr,
                           subject=f"[{socket.gethostname()}] ({dt_now}) OpenManage Server Report, Severity: {_severity}",
                           message=output_str)
        else:
            print(f"- [ERROR] please config SENDER_EMAIL and RECEIVER_EMAIL in .env file")
    else:
        print(output_str)