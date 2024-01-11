import os
import json
import subprocess
import logging
import time
from logging.handlers import RotatingFileHandler

base_dir = os.path.dirname(os.path.realpath(__file__))


def log_setup(level: int = logging.DEBUG, log_time_zone_local: bool = True, log_file_name: str = None):
    if not log_file_name:
        log_file_name = os.path.basename(__file__).split('.py')[0] + '.log'
    if not log_file_name.endswith('.log'):
        log_file_name += ".log"
    handler = RotatingFileHandler(os.path.join(base_dir, log_file_name),
                                  maxBytes=307200, backupCount=3, encoding='utf-8')  # 300KB
    formatter = logging.Formatter(fmt='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                                  datefmt='%Y-%m-%d %H:%M:%S')
    if not log_time_zone_local:
        formatter.converter = time.gmtime  # if you want UTC time
    handler.setFormatter(formatter)
    logger = logging.getLogger()
    logger.addHandler(handler)
    logger.setLevel(level)


def keep_alive(pc_list):
    for item in pc_list:
        out = subprocess.check_output([f"ps -aux | grep \"{item[0]}\""], shell=True)
        is_running = False
        for line in out.splitlines():
            line = line.decode('utf-8')
            if item[0] in line and " grep " not in line and "/bin/sh -c ps -aux" not in line:
                is_running = True
                break
        if not is_running:
            logging.info(f"[keep alive] the pattern [{item[0]}] is not found in process list, execute: [{item[1]}]")
            subprocess.check_output([item[1]], shell=True)


if __name__ == "__main__":
    log_setup(level=logging.INFO)
    logging.info("=== start ===")
    process_list = []
    pl_config_file = f"{base_dir}/check_list.json"
    if os.path.isfile(pl_config_file):
        with open(pl_config_file) as f:
            process_list = json.load(f)
            logging.info(f"check for {len(process_list)} process")
            keep_alive(process_list)
    else:
        print(f"Please create file {pl_config_file} to setup process to keep alive!")
        print("Example file content: [[\"process execute pattern\", \"command to run process if it's not running\"]]")
    logging.info("=== end ===")
