import os
import click
import shutil
import time
import traceback
import sys
import logging
from logging.handlers import RotatingFileHandler
from sys import exit

if getattr(sys, 'frozen', False):
    base_dir = os.path.dirname(sys.executable)
else:
    base_dir = os.path.dirname(os.path.realpath(__file__))

def _scan_dir(dir_path: str, deep: int = 0, max_deep: int = 0):
    data = [{'path': dir_path, 'is_dir': os.path.isdir(dir_path), 'c_time': os.path.getctime(dir_path), 'm_time': os.path.getmtime(dir_path), 'deep': deep}]
    if os.path.isdir(dir_path):
        items = os.listdir(dir_path)
        for item in items:
            _path = os.path.join(dir_path, item)
            if os.path.isfile(_path):
                data.append({'path': _path, 'is_dir': False, 'c_time': os.path.getctime(_path), 'm_time': os.path.getmtime(_path), 'deep': deep})
            else:
                if max_deep:
                    if deep + 1 <= max_deep:
                        data += _scan_dir(_path, deep + 1, max_deep)
                else:
                    data += _scan_dir(_path, deep + 1, max_deep)
    return data

def _scan_empty_dir(dir_path: str):
    data = []
    if os.path.isdir(dir_path):
        items = os.listdir(dir_path)
        if not items:
            data.append(dir_path)
        else:
            for item in items:
                _path = os.path.join(dir_path, item)
                if os.path.isdir(_path):
                    data += _scan_empty_dir(_path)
    return data


def get_disk_free(dir_path: str):
    total, used, free = shutil.disk_usage(dir_path)
    free_in_gb = free // (2 ** 30)
    return free_in_gb


def log_setup(level: int = logging.DEBUG, log_time_zone_local: bool = True):
    handler = RotatingFileHandler(os.path.join(base_dir, os.path.basename(__file__).split('.py')[0] + '.log'), maxBytes=102400, backupCount=3, encoding='utf-8')  # 100KB
    formatter = logging.Formatter(fmt='%(asctime)s - %(name)s - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
    if not log_time_zone_local:
        formatter.converter = time.gmtime  # if you want UTC time
    handler.setFormatter(formatter)
    logger = logging.getLogger()
    logger.addHandler(handler)
    logger.setLevel(level)


@click.command()
@click.option('--path', help="Directory to clean up", required=True)
@click.option('--mode', help="Clean mode, support: folder, file (default: file)", default='file')
@click.option('--folder-level', help="Clean folder level (default: 0). Required a number from 1 in-case --mode is 'folder'. "
                                     "This value for deep level of folder will get delete, "
                                     "the directory of --path is root folder (deep level 0), example when 1, "
                                     "all direct sub-directory of --path (depp level = 1) will get delete if ages > --ages", default=0)
@click.option('--disk-free-trigger', help='Minimum disk free in GB to trigger old file cleanup. '
                                          'Old files will not be deleted if disk free is above '
                                          'this value. (default: not set)', default=0)
@click.option('--debug', help='Debug mode (default: false)', default=False)
@click.option('--ages', help='The ages of file/folder in days is allow delete', required=True, type=int)
@click.option('--delete-empty-dir', help='Delete all empty directory', default=False)
def clean_old_file(path: str, mode: str, folder_level: int = 0, disk_free_trigger: int = 0, ages: int = 0,
                   delete_empty_dir: bool = False, debug: bool = False):
    clean_folder_mode = mode == 'folder'
    logging.info(f"App start...\npath: {path}\nmode: {mode}\nfolder_level: {folder_level}"
                 f"\ndisk_free_trigger: {disk_free_trigger}\nages: {ages}\ndelete_empty_dir: {delete_empty_dir}\ndebug: {debug}")
    if clean_folder_mode:
        if not folder_level:
            click.echo(f"Error: --folder-level must from 1, current value: {folder_level}")
            exit()

    if debug:
        click.echo(click.style("Debug mode, no file/folder get delete!", fg="green"))
        click.echo(click.style('-----------------------', fg='green'))
        click.echo('Scan path: ' + click.style(path, fg='red'))
        click.echo('Delete mode: ' + click.style(mode, fg='red'))
        click.echo('Delete folder level: ' + click.style(folder_level, fg='red'))
        click.echo('Delete when disk free below: ' + click.style(disk_free_trigger, fg='red') + ' GB' + (' (skip)' if not disk_free_trigger else ''))
        click.echo('Delete folder/file ages from: ' + click.style(ages, fg='red') + ' days')
        click.echo('Delete empty folder: ' + click.style(delete_empty_dir, fg='red'))
        input("Press Enter to continue...")
    if not os.path.isdir(path):
        click.echo("Directory: " + click.style(path, fg="red") + " is not exist!")
        exit()
    if disk_free_trigger:
        free_gb = get_disk_free(path)
        if get_disk_free(path) > disk_free_trigger:
            if not debug:
                click.echo(f"The current disk free size: {click.style(free_gb, fg='green')} GB, not need to delete old files...")
                exit()
            else:
                click.echo(f"The current disk free size: {click.style(free_gb, fg='green')} GB")
    if clean_folder_mode:
        data_items = _scan_dir(path, max_deep=folder_level)
    else:
        data_items = _scan_dir(path)
    now = time.time()
    if debug:
        click.echo(click.style('-----------------------', fg='green'))
        click.echo("[Debug] Folder scan result")
        data_items.sort(key=lambda x: x['path'])
        for item in data_items:
            click.echo(f"[{click.style('D', fg='red') if item['is_dir'] else 'F'}] {item['path']} → age: "+ click.style((now - item['c_time'])/86400, fg='green') +" days")

    if data_items:
        data_items.sort(key=lambda x: x['m_time'])
        if debug:
            if clean_folder_mode:
                click.echo(click.style('-----------------------', fg='green'))
                have_level_folder = False
                for item in data_items:
                    if item['is_dir'] and item['deep'] == folder_level:
                        click.echo(f"[Debug] Folder can be delete: " + click.style(item['path'], fg='red'))
                        have_level_folder = True
                if not have_level_folder:
                    click.echo(f"[Debug] Folder can be delete: " + click.style('EMPTY', fg='red'))
            click.echo(click.style('-----------------------', fg='green'))
            input("Press Enter to continue to show delete old folder/file result...")
        delete_count = 0
        for item in data_items:
            item_age = (now - (item['c_time'] if item['c_time'] > item['m_time'] else item['m_time'])) / 86400
            if clean_folder_mode:
                if item['is_dir'] and item['deep'] == folder_level and item_age > ages:
                    if debug:
                        click.echo(f"[Debug] Folder delete: " + click.style(item['path'], fg='red') + ", ages: " + click.style(item_age, fg='red') + ' days')
                    else:
                        try:
                            shutil.rmtree(item['path'])
                            logging.info(f"Deleted folder: {item['path']}, ages: {item_age:.2f} days")
                            # check disk free size to stop delete
                            if disk_free_trigger and (get_disk_free(path) > disk_free_trigger):
                                break
                        except Exception:
                            logging.error(f"Error delete folder: {item['path']}, traceback:\n{traceback.format_exc()}")
            else:
                if not item['is_dir'] and item_age > ages:
                    if debug:
                        click.echo(f"[Debug] File delete: " + click.style(item['path'], fg='red') + ", ages: " + click.style(item_age, fg='red') + ' days')
                    else:
                        try:
                            os.unlink(item['path'])
                            delete_count += 1
                            logging.info(f"Deleted file: {item['path']}, ages: {item_age} days")
                        except Exception:
                            logging.error(f"Error delete file: {item['path']}, traceback:\n{traceback.format_exc()}")
                        # check disk free size to stop delete
                        if delete_count and not delete_count % 5 and disk_free_trigger and (get_disk_free(path) > disk_free_trigger):
                            break
    if delete_empty_dir:
        if debug:
            click.echo(click.style('-----------------------', fg='green'))
            input("Press Enter to continue to show delete empty directory result...")
        empty_dirs = _scan_empty_dir(path)
        for item in empty_dirs:
            if item != path:
                if debug:
                    click.echo(f"[Debug] Empty folder delete: " + click.style(item, fg='red'))
                else:
                    try:
                        shutil.rmtree(item)
                        logging.info(f"Deleted empty folder: {item}")
                    except Exception:
                        logging.error(f"Error delete empty folder: {item}")


if __name__ == "__main__":
    """Delete old file
    if --disk-free-trigger (GB) is set, only trigger delete when disk free below this value, start from oldest item, also, 
    stop delete when disk free above this value
    if --disk-free-trigger is not set, folder or file older than --ages will be delete
    """
    log_setup(level=logging.INFO, log_time_zone_local=True)
    clean_old_file()
