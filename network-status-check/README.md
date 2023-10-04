# `network_status_check.py`

A tool for check network status by access a URL. Reboot OS if connection failed (on Linux) or refresh interface (on Windows)

* help: `python3 network_status_check.py -h`
* usage: 
    * `python3 network_status_check.py --url http://192.168.1.1` (reboot OS if failed)
    * `python3 network_status_check.py --url http://192.168.1.1 -ri "Local Area Connection"` (refresh interface if failed)
    