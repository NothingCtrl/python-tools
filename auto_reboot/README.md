### Auto Reboot

> Tested with **Windows 7** (and up) and **Ubuntu 16.04** (and up)

#### Features note

* Auto reboot system by counting uptime days (not by interval)
* Support send Telegram message before reboot ([create a bot](https://core.telegram.org/bots#how-do-i-create-a-bot)), required environment params:
    ```
    export AUTO_REBOOT_TELEGRAM_TOKEN=
    export AUTO_REBOOT_TELEGRAM_CHAT_ID=
    export AUTO_REBOOT_SERVICE_NAME=
    ```
#### Usage

* Reboot if system uptime from 100 days: `./auto_reboot 100`
* Debug mode will print out report but not execute reboot command: `./auto_reboot 100 debug`
