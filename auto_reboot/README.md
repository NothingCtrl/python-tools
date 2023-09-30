### Auto Reboot

> Tested with **Windows 7** (and up) and **Ubuntu 16.04** (and up)

#### Features note

* Auto reboot system by counting uptime days (not by interval)
* Support for sending Telegram messages before a reboot using the [Telegram Bot API](https://core.telegram.org/bots#how-do-i-create-a-bot) is available. To use this feature, the required environment parameters are:
    ```
    export AUTO_REBOOT_TELEGRAM_TOKEN=
    export AUTO_REBOOT_TELEGRAM_CHAT_ID=
    export AUTO_REBOOT_SERVICE_NAME=
    ```
#### Usage example

* Reboot the system if it has been running for 100 days or more.: `./auto_reboot 100`
* In the debug mode, application will print out report but not execute reboot command: `./auto_reboot 100 debug`
