# Gravatar Tools

Support feature to management Gravatar account:

* Add new email (need confirm by email)
* Upload, delete and set alt-text for avatar
* Set email avatar

## Setup and Usages

* Required login to gravatar.com and get browser cookie
* Create virtual env, install packages requirement `pip install -r requirements.txt`
* Create a config file `_gravatar_config.json` follow example, replace `YOUR-COOKIE-HERE` with actual cookie:
    ```json
    {
        "headers": {
            "Accept": "application/json, */*;q=0.1",
            "Accept-Encoding": "gzip",
            "Accept-Language": "en-US,en;q=0.9,vi;q=0.8",
            "Cache-Control": "no-cache",
            "Content-Type": "application/json",
            "Cookie": "ccpa_applies=false; is-logged-in=1; gravatar=YOUR-COOKIE-HERE",
            "Origin": "https://gravatar.com",
            "Pragma": "no-cache",
            "Priority": "u=1, i",
            "Referer": "https://gravatar.com/",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36"
        }
    }
    ```
### Features

* Get data: `python gravatar.py get_data`, to filter email or image `python gravatar.py get_data <filter-text-here>`
* Add email: `python gravatar.py add_email <email-address>` (after request, you need confirm by click on url send to mailbox)
* Set avatar for an exist email: `python gravatar.py set_avatar <email-address> <image-id>`
* Set alt-text for an exist image: `python gravatar.py set_alt_text <image-id> <your-text>`
* Delete an exist image: `python gravatar.py delete_image <image-id>`
* Upload new image from local: `python gravatar.py upload_image <path-to-image-file>`
* Upload new image and use it as avatar for an email: `python gravatar.py upload_and_set_avatar <email-address> <path-to-image-file>`
* Refresh `X-Gr-Nonce`: `python gravatar.py update_x_gr_nonce` (just for test, this token refresh automatically)