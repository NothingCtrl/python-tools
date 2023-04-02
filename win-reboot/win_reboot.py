import sys
import os
import datetime
from subprocess import check_output

def windows_reboot_by_days(days: int):
    current_time = datetime.datetime.now()
    tmp = check_output(["powershell", "-command", "(gcim Win32_OperatingSystem).LastBootUpTime"]). \
        replace(b'\r\n', b'').decode(encoding='utf8')

    w_date = datetime.datetime.strptime(tmp, "%A, %B %d, %Y %I:%M:%S %p")
    diff_in_day = (current_time - w_date).days
    if diff_in_day >= days:
        os.system("shutdown -r -t 000")

if __name__ == "__main__":
    if os.name != 'nt':
        print("Only working on Windows")
        exit()
    if len(sys.argv) < 2:
        print("Please call with number of day to reboot, example: python win_reboot.py 7")
        exit()
    if sys.argv[1].isdecimal() and int(sys.argv[1]) >= 0:
        windows_reboot_by_days(int(sys.argv[1]))
    else:
        print(f"The input: '{sys.argv[1]}' is not allow!")