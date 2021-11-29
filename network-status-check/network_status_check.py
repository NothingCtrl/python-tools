import ssl
import urllib.request
import time
import os
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("--url", "-u", help="URL to check for network status")
parser.add_argument("--refresh-interface", "-ri", help="Name interface to refresh (Windows only), if not set, will call OS reboot if network status check failed")
args = parser.parse_args()

if getattr(sys, 'frozen', False):
    # frozen
    from sys import exit

def request_check(url, retry: int = 3, delay: int = 15):
    # context to ignore SSL verify
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    count = 0
    while count <= retry:
        try:
            return urllib.request.urlopen(url, context=ctx).getcode() == 200
        except Exception:
            ...
        count += 1
        time.sleep(delay)
    return False
    
def refresh_windows_network_interface(interface_name: str = "Local Area Connection"):
    # disable and enable windows interface
    # this command must run under Administrator role
    os.system(f'netsh interface set interface "{interface_name}" admin=disable')
    time.sleep(3)
    os.system(f'netsh interface set interface "{interface_name}" admin=enable')
    
def reboot_os():
    if os.name == 'nt':
        os.system("shutdown -t 0 -r -f")
    else:
        os.system("sudo shutdown -r now")
    
    
if __name__ == "__main__":
    if not args.url:
        print("--url / -u is required for check network status!")
    else:
        if not request_check(args.url):
            if args.refresh_interface and os.name == 'nt':
                refresh_windows_network_interface(args.refresh_interface)
            else:
                reboot_os()

