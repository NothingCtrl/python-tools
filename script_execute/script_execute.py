"""
Execute all scripts in scripts folder
"""
import threading
import os
import sys
import time
import datetime
import traceback
from subprocess import check_output

ALLOW_EXTENSION = ('bat', 'sh', 'ps1')

scripts_output = []
thread_list = []

if getattr(sys, 'frozen', False):
    # frozen
    base_dir = os.path.dirname(sys.executable)
else:
    # unfrozen -- normal python code
    base_dir = os.path.dirname(os.path.realpath(__file__))


def run_script(execute_path: str):
    global scripts_output

    def call_system():
        start_time = time.time()
        try:
            if execute_path.split('.')[-1].lower() == 'ps1' and os.name == 'nt':
                out = check_output(['powershell', '-file', execute_path]).decode(encoding='utf8')
            else:
                out = check_output([execute_path]).decode(encoding='utf8')
            if os.name == 'nt':
                out.replace("\r\r\r\n", "\r\n").replace("\r\r\n", "\r\n")
        except Exception:
            out = traceback.format_exc()
        scripts_output.append({
            'script_path': execute_path,
            'output': out,
            'duration': time.time() - start_time
        })

    th = threading.Thread(target=call_system, daemon=True)
    th.start()
    return th


def wait_to_finish(timeout: int = None):
    wait = False
    for _th in thread_list:
        if _th['thread'].is_alive() and (timeout is None or timeout > 0):
            wait = True
    if wait:
        time.sleep(1)
        if timeout is None:
            wait_to_finish()
        else:
            wait_to_finish(timeout - 1)

if __name__ == "__main__":
    time_now = datetime.datetime.now()
    script_dir = os.path.join(base_dir, 'scripts')

    print(f"=== Execute file with extension: {', '.join(ALLOW_EXTENSION)} ===")

    _timeout, execute_script = None, None
    if len(sys.argv) >= 2:
        if str.isdecimal(sys.argv[1]) and int(sys.argv[1]) > 0:
            _timeout = int(sys.argv[1])
        if len(sys.argv) >= 3:
            execute_script = sys.argv[2]

    print(f"=== Execute with timeout set (seconds): {_timeout if _timeout else 'un-limit'} ===")
    if execute_script:
        print(f"=== Single script execute: {execute_script}")

    scripts = []
    if os.path.isdir(script_dir):
        scripts = os.listdir(script_dir)
        if execute_script is not None:
            if execute_script in scripts:
                scripts = [execute_script]
            else:
                print(f"  - Script is not found in scripts folder: {script_dir}")
                scripts = []
        for item in scripts:
            if os.path.isfile(os.path.join(script_dir, item)) and item.split('.')[-1].lower() in ALLOW_EXTENSION:
                thread_list.append({
                    'name': item,
                    'thread': run_script(os.path.join(script_dir, item))
                })
        wait_to_finish(_timeout)
    else:
        os.mkdir(script_dir)
    log_dir = os.path.join(base_dir, 'logs')
    if not os.path.isdir(log_dir):
        os.mkdir(log_dir)
    log_file = time_now.strftime("%Y%m%d_%H%M") + "_report.log"

    log_text = ""
    count_exe = 0
    for report in scripts_output:
        count_exe += 1
        log_text += f"- Script: {report['script_path']}\n  - Duration: {report['duration']}\n  " \
                    f"- Output log:\n----------------------- BEGIN -----------------------\n{report['output']}" \
                    f"\n----------------------- END -----------------------\n\n\n"

    with open(os.path.join(log_dir, log_file), 'w+', errors='ignore') as f:
        f.write(f"Report for date: {time_now.strftime('%Y:%m:%d %H:%M:%S')}\n")
        f.write(f"Execute timeout: {_timeout if _timeout else 'no timeout'}\n")
        f.write(f"Single script execute mode: {'YES' if execute_script else 'NO'}\n")
        f.write(f"Total script: {len(scripts)}\n")
        f.write(f"Total response: {count_exe}\n")
        f.write("============\n")
        f.write(log_text)

