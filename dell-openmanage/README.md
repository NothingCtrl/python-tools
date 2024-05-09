# Dell OpenManage Report


Wrap report output of command `omreport system alertlog` on Dell server with severity and date filter.
The result can print in console or send via email.

### Usage:

* Severity allowed values: `Ok`, `Non-Critical`, `Critical`
* Send email using non-auth SMTP server with a `.env` config follow:
  ```
  SENDER_EMAIL=foo@bar.com
  RECEIVER_EMAIL=demo@bar.com
  ```
  check folder **`smtp_server`** for SMTP server
* Filter logs have severity = `Critical` of current date: 
  * Print output: `python open_manage_report_logs.py Critical`
  * Send email: `python open_manage_report_logs.py Critical send-email`
  * Debug: `python open_manage_report_logs.py Critical debug`
  
* Filter logs have severity = `Non-Critical` of specific date `2023-05-2`:
  * Print output: `python open_manage_report_logs.py Non-Critical _ 2023-05-21`
  * Send email: `python open_manage_report_logs.py Non-Critical send-email 2023-05-21`
  * Debug: `python open_manage_report_logs.py Non-Critical debug 2023-05-21`
  
### Release

* The release file `release/open_manage_report_logs.exe` build with `pyinstaller` on Windows 11 64bit 