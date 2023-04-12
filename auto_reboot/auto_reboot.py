# -*- coding: utf-8 -*-
import sys
import requests
import datetime
import os
import traceback
import time
from subprocess import check_output
import threading

DEBUG = False
TELEGRAM_LOG = None

if getattr(sys, 'frozen', False):
    # frozen
    from sys import exit


def send_telegram_message(message: str):
    global TELEGRAM_LOG
    try:
        telegram_token = os.getenv("AUTO_REBOOT_TELEGRAM_TOKEN")
        telegram_chat_id = os.getenv("AUTO_REBOOT_TELEGRAM_CHAT_ID")
        service_name = os.getenv("AUTO_REBOOT_SERVICE_NAME", os.path.basename(__file__).split('.')[0])
        if telegram_token and telegram_chat_id:
            send_message_text = f"=== *{service_name}* ===\n{message}"
            send_payload = f'https://api.telegram.org/bot{telegram_token}/sendMessage?chat_id={telegram_chat_id}&parse_mode=Markdown&text={send_message_text}'
            rp = requests.get(send_payload)
            if rp.status_code not in (200, 201):
                TELEGRAM_LOG = False, {"error": f"response_status: {rp.status_code}, response_text: {rp.text}"}
            else:
                TELEGRAM_LOG = True, {}
        else:
            TELEGRAM_LOG = False, {"error": "Telegram configs is not exist!"}
    except Exception:
        error = traceback.format_exc()
        TELEGRAM_LOG = False, {"error": error}


def telegram_notify(message: str, timeout: int = 5):
    th = threading.Thread(target=send_telegram_message, args=(message,), daemon=True)
    th.start()
    time.sleep(timeout)


def reboot_windows(days: int):
    current_time = datetime.datetime.now()
    tmp = check_output(["powershell", "-command", "(gcim Win32_OperatingSystem).LastBootUpTime"]). \
        replace(b'\r\n', b'').decode(encoding='utf8')

    w_date = datetime.datetime.strptime(tmp, "%A, %B %d, %Y %I:%M:%S %p")
    diff_in_day = (current_time - w_date).days
    if diff_in_day >= days:
        telegram_notify(f"System are going to reboot after *{days}* day(s) of running!")
        if not DEBUG:
            os.system("shutdown -r -t 000")
        else:
            print(f"(Debug) uptime days: {days}")
            print(f"(Debug) notify response: {TELEGRAM_LOG}")


def reboot_linux(days: int):
    tmp = check_output(["uptime"]).decode(encoding='utf8')
    if (' up ' in tmp and ' days,' in tmp) or days == 0:
        if ' up ' in tmp and ' days,' in tmp:
            up_days = tmp.split(' up ')[1].split(' days,')[0]
        else:
            up_days = "0"
        if int(up_days) >= days:
            telegram_notify(f"System are going to reboot after *{days}* day(s) of running!")
            if not DEBUG:
                os.system("/sbin/shutdown -r now")
            else:
                print(f"(Debug) uptime days: {days}")
                print(f"(Debug) notify response: {'Connection Error' if TELEGRAM_LOG is None else TELEGRAM_LOG}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("---")
        print("Please run with a param set number of days to reboot, example:\n  - reboot after 7 days: python auto_reboot.py 7\n  - to active debug mode, using: python auto_reboot.py 7 debug")
        print("---")
        print("To send notify before reboot via Telegram, set to runtime environment these value:")
        print("    - AUTO_REBOOT_TELEGRAM_TOKEN")
        print("    - AUTO_REBOOT_TELEGRAM_CHAT_ID")
        print("    - (Option) AUTO_REBOOT_SERVICE_NAME: To custom name of service")
        exit()
    if len(sys.argv) == 3 and sys.argv[2] == 'debug':
        DEBUG = True
    if DEBUG:
        print(f"(Debug) Telegram token: {os.getenv('AUTO_REBOOT_TELEGRAM_TOKEN')}")
        print(f"(Debug) Telegram chat id: {os.getenv('AUTO_REBOOT_TELEGRAM_CHAT_ID')}")
        print("(Debug) Service name:", os.getenv("AUTO_REBOOT_SERVICE_NAME", os.path.basename(__file__).split('.')[0]))
        if os.name != 'nt':
            if os.path.isfile('/sbin/shutdown'):
                print(f"(Debug) OK, path '/sbin/shutdown' is available")
            else:
                print(f"(Debug) Warning, path '/sbin/shutdown' is not exist!")

    if sys.argv[1].isdecimal() and int(sys.argv[1]) >= 0:
        if os.name == 'nt':
            reboot_windows(int(sys.argv[1]))
        else:
            reboot_linux(int(sys.argv[1]))
    else:
        print(f"The input: '{sys.argv[1]}' is not allow!")
