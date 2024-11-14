import imaplib
import email
from email.header import decode_header
import requests
import os
import re
import json
import time
import hashlib
import sys
from pprint import pprint
from traceback import format_exc

IMAGE_ATTRS = (
    ('image_id', None),
    ('image_url', None),
    ('is_cropped', False),
    ('format', 0),
    ('rating', 'G'),
    ('updated_date', ''),
    ('altText', '')
)


def file_hash_md5(file_path: str):
    with open(file_path, "rb") as f:
        file_hash = hashlib.md5()
        chunk = f.read(8192)
        while chunk:
            file_hash.update(chunk)
            chunk = f.read(8192)
    return file_hash.hexdigest()


def load_configs(filter_key: str = "headers"):
    _data = {}
    if os.path.isfile("_gravatar_config.json"):
        with open("_gravatar_config.json") as f:
            if filter_key:
                _data = json.load(f)[filter_key]
            else:
                _data = json.load(f)
    return _data


def save_configs(data_pair: dict):
    with open("_gravatar_config.json", "w+") as f:
        json.dump(data_pair, f, indent=4, sort_keys=True)
    return True

def get_confirm_email(email_addr: str):
    configs = load_configs(filter_key="")
    if "mailbox_username" in configs and "mailbox_password" in configs and "mail_server_address" in configs:
        # create an IMAP4 class with SSL
        imap = imaplib.IMAP4_SSL(configs['mail_server_address'])
        login_retry = 5
        while login_retry > 0:
            # authenticate
            try:
                imap.login(configs['mailbox_username'], configs['mailbox_password'])
                break
            except imaplib.IMAP4.abort:
                login_retry -= 1
                if login_retry > 0:
                    time.sleep(15)
        if login_retry == 0:
            print(f"- [get_confirm_email] ERROR, cannot login!")
            return ""
        status, messages = imap.select("INBOX")
        # total number of emails
        messages = int(messages[0])
        # fetch top 3 messages
        for i in range(messages, messages - 3, -1):
            # fetch the email message by ID
            res, msg = imap.fetch(str(i), "(RFC822)")
            for response in msg:
                if isinstance(response, tuple):
                    # parse a bytes email into a message object
                    msg = email.message_from_bytes(response[1])
                    # decode the email subject
                    subject, encoding = decode_header(msg["Subject"])[0]
                    if isinstance(subject, bytes):
                        # if it's a bytes, decode to str
                        subject = subject.decode(encoding)
                    # decode email sender
                    send_from, encoding = decode_header(msg.get("From"))[0]
                    if isinstance(send_from, bytes):
                        send_from = send_from.decode(encoding)
                    # print("Subject:", subject)
                    # print("From:", send_from)
                    body = ""
                    content_type = ""
                    # if the email message is multipart
                    if msg.is_multipart():
                        # iterate over email parts
                        for part in msg.walk():
                            # extract content type of email
                            content_type = part.get_content_type()
                            content_disposition = str(part.get("Content-Disposition"))
                            try:
                                # get the email body
                                body += part.get_payload(decode=True).decode()
                            except:
                                pass
                    else:
                        # extract content type of email
                        content_type = msg.get_content_type()
                        # get the email body
                        body = msg.get_payload(decode=True).decode()

                    if body and "Verify email addition" in subject and "donotreply@gravatar.com" in send_from and \
                            content_type == "text/html":
                        if email_addr in body:
                            pattern = re.compile("href=\".*?\">Confirm your email")
                            groups = pattern.search(body)
                            if groups:
                                # close the connection and logout
                                imap.close()
                                imap.logout()
                                return groups[0].replace("href=\"", "").replace("\">Confirm your email", "")
        # close the connection and logout
        imap.close()
        imap.logout()
        return ""
    else:
        return ""


def add_email(email_addr: str) -> tuple:
    """Add an email address to Gravatar account"""
    end_point = "https://api.gravatar.com/v2/users/me/identity?_locale=&source=web-app-editor"
    configs = load_configs(filter_key="")
    auto_active_email = False
    if "mailbox_username" in configs and "mailbox_password" in configs and "mail_server_address" in configs:
        auto_active_email = True
    if configs.get("headers"):
        update_x_gr_nonce()
        ss_rq = requests.session()
        rp = ss_rq.post(end_point, json={"email": email_addr, "locate": "en"}, headers=configs.get("headers"))
        if rp.status_code:
            try:
                _data = rp.json()
                if "error" in _data:
                    return False, _data["error"]
            except Exception:
                return False, "[ERROR] Json decode error!"
            if auto_active_email:
                print(f"- [add_email] auto confirm address [{email_addr}], please wait...")
                active_ok = False
                start_time = time.time()
                time.sleep(30)
                while time.time() - start_time < 300:
                    active_url = get_confirm_email(email_addr)
                    if active_url:
                        print(f"- [add_email] active url: {active_url}")
                        # user click url and browser redirect to gravatar.com
                        # then redirect to gravatar.com/profile/avatars/?added=<address>
                        ss_rq.get(active_url.replace("https://en.gravatar.com/", "https://gravatar.com/"),
                                  headers=configs.get("headers"), allow_redirects=True)
                        active_ok = True
                        break
                    else:
                        time.sleep(30)
                if not active_ok:
                    print(f"- [add_email] cannot active for address: {email_addr}")
                    return False, "Cannot get active url"
            return True, ""
        else:
            return False, f"[ERROR] Response error, status code: {rp.status_code}, text: {rp.text}"
    else:
        return False, "[ERROR] Please add config for payload request headers!"


def set_avatar(email_addr: str, image_id: str) -> tuple:
    end_point = "https://api.gravatar.com/v2/users/me/identity/MD5_HASH?_locale=&source=web-app-editor"
    headers = load_configs()
    if headers:
        update_x_gr_nonce()
        ss_rq = requests.session()
        email_hash = hashlib.md5(email_addr.strip().lower().encode('utf-8')).hexdigest()
        target = end_point.replace("MD5_HASH", email_hash)
        rp = ss_rq.post(target, json={"image_id": image_id}, headers=headers)
        if rp.status_code:
            try:
                _data = rp.json()
                if not "error" in _data or not _data["error"]:
                    return True, ""
            except Exception:
                pass
            return "error" not in rp.text, rp.text
        else:
            return False, f"[ERROR] Response error, status code: {rp.status_code}, text: {rp.text}"
    else:
        return False, "[ERROR] Please add config for payload request headers!"


def set_alt_text(image_id: str, alt_text: str) -> tuple:
    end_point = f"https://api.gravatar.com/v2/users/me/image/{image_id}?_locale=&source=web-app-editor"
    headers = load_configs()
    if headers:
        ss_rq = requests.session()
        rp = ss_rq.post(end_point, json={"altText": alt_text}, headers=headers)
        if rp.status_code:
            try:
                _data = rp.json()
                if not "error" in _data or not _data["error"]:
                    image_data = {}
                    for att in IMAGE_ATTRS:
                        if att[0] in _data:
                            image_data[att[0]] = _data[att[0]]
                        else:
                            image_data[att[0]] = att[1]
                    return True, image_data
                else:
                    return False, _data
            except Exception:
                pass
            return "error" not in rp.text, rp.text
        else:
            return False, f"[ERROR] Response error, status code: {rp.status_code}, text: {rp.text}"
    else:
        return False, "[ERROR] Please add config for payload request headers!"


def delete_image(image_id: str) -> tuple:
    end_point = f"https://api.gravatar.com/v2/users/me/image/{image_id}?_locale=&source=web-app-editor"
    headers = load_configs()
    if headers:
        ss_rq = requests.session()
        headers['X-Http-Method-Override'] = "delete"
        rp = ss_rq.post(end_point, headers=headers)
        if rp.status_code:
            try:
                _data = rp.json()
                if not "error" in _data or not _data["error"]:
                    return True, ""
            except Exception:
                pass
            return "error" not in rp.text, rp.text
        else:
            return False, f"[ERROR] Response error, status code: {rp.status_code}, text: {rp.text}"
    else:
        return False, "[ERROR] Please add config for payload request headers!"


def upload_image(file_path: str, alt_text_filename: bool = True) -> tuple:
    """Upload an image avatar"""
    end_point = "https://api.gravatar.com/v2/users/me/image?_locale=&source=web-app-editor"
    configs = load_configs(filter_key="")
    headers = configs["headers"] if "headers" in configs else {}
    if headers:
        update_x_gr_nonce()
        ss_rq = requests.session()
        image_f = open(file_path, 'rb')
        files = {'image': (os.path.basename(file_path), image_f, "image/jpeg")}
        # required post request with Content-Type:multipart/form-data; boundary=????
        body, content_type = requests.models.RequestEncodingMixin._encode_files(files, {
            "source": "direct",
            "forceIdentity": False
        })
        headers['Content-Type'] = content_type
        rp = ss_rq.post(end_point, data=body, headers=headers)
        if rp.status_code:
            try:
                _data = rp.json()  # payload format: {"image": {...}, "user": {...}}
                if "image" in _data and "image_id" in _data["image"]:
                    image_data = {}
                    for att in IMAGE_ATTRS:
                        if att[0] in _data['image']:
                            image_data[att[0]] = _data['image'][att[0]]
                        else:
                            image_data[att[0]] = att[1]
                    if alt_text_filename:
                        status, _error = set_alt_text(image_data['image_id'], os.path.basename(file_path))
                        if not status:
                            print(f"- [upload_image] Set altText failed, error:\n{_error}")
                    if configs.get("move_uploaded_to_done", False):
                        try:
                            image_f.close()
                            base_dir = os.path.dirname(file_path)
                            done_dir = os.path.join(base_dir, "done")
                            new_file_path = os.path.join(done_dir, os.path.basename(file_path))
                            if not os.path.isdir(done_dir):
                                os.mkdir(done_dir)
                            if not os.path.isfile(new_file_path):
                                os.rename(file_path, new_file_path)
                            else:
                                tmp = os.path.basename(file_path).split(".")
                                ext = tmp.pop(-1)
                                name = ".".join(tmp)
                                new_file_path = os.path.join(done_dir, f"{name}_{int(time.time())}.{ext}")
                                os.rename(file_path, new_file_path)
                        except Exception:
                            print(f"- [upload_image] Cannot move file {os.path.basename(file_path)}, "
                                  f"error:\n{format_exc()}")
                    return True, image_data
            except Exception:
                pass
            return False, rp.text
        else:
            return False, f"[ERROR] Response error, status code: {rp.status_code}, text: {rp.text}"
    else:
        return False, "[ERROR] Please add config for payload request headers!"


def upload_and_set_avatar(email_addr: str, file_path: str) -> tuple:
    email_exist = False
    ok, _data = get_data(email_addr)
    if ok and _data['identities']:
        for item in _data['identities']:
            if item['email'] == email_addr:
                email_exist = True
                break
    if not email_exist:
        ok, error = add_email(email_addr)
        if not ok:
            return False, "", error
    status, _data = upload_image(file_path)
    if status:
        status, error = set_avatar(email_addr, _data['image_id'])
        if status:
            return True, _data['image_id'], "IMAGE_UPLOADED_AND_SET"
        else:
            return False, _data['image_id'], error
    else:
        return False, "", _data


def set_avatar_from_dir(dir_path: str, domain: str, allow_extension: tuple =('jpg',)):
    """Scan dir_path get image file then add to gravatar, file name must have format: <username>.jpg"""
    items = os.listdir(dir_path)
    ok_item = []
    err_item = []
    for item in items:
        file_path = os.path.join(dir_path, item)
        if os.path.isfile(file_path):
            name_split = item.split(".")
            ex = name_split.pop(-1)
            if ex in allow_extension:
                username = ".".join(name_split).lower()
                email_addr = f"{username}@{domain}"
                is_ok, _, error = upload_and_set_avatar(email_addr, file_path)
                msg = f"---\n- username: [{username}], email: [{email_addr}], result: {'OK' if is_ok else 'ERROR'}"
                if not is_ok:
                    msg += f", error: {error}"
                print(f"{msg}\n")
                if is_ok:
                    ok_item.append(username)
                else:
                    err_item.append(username)
    if items and (ok_item or err_item):
        print(f"- Total OK: {len(ok_item)}, list: {ok_item}")
        print(f"- Total ERROR: {len(err_item)}, list: {err_item}")
    else:
        print(f"- Nothing todo")
    return ok_item, err_item


def get_data(filter_text: str = "") -> tuple:
    end_point = "https://api.gravatar.com/v2/users/me?_locale=&source=web-app-editor"
    headers = load_configs()
    if headers:
        update_x_gr_nonce()
        ss_rq = requests.session()
        rp = ss_rq.get(end_point, headers=headers)
        if rp.status_code:
            try:
                if not filter_text:
                    return True, rp.json()  # data example: {"id":..., "login":..., "email":....}
                else:
                    _data = rp.json()
                    filter_rs = {"identities": [], "images": []}
                    if "identities" in _data:
                        for item in _data["identities"]:
                            if filter_text in item["email"] or filter_text in item["image_id"]:
                                filter_rs["identities"].append(item)
                    if "images" in _data:
                        for item in _data["images"]:
                            if filter_text in item["altText"] or filter_text in item["image_id"]:
                                filter_rs["images"].append(item)
                    return True, filter_rs
            except Exception:
                return True, rp.text
        return False, rp.text
    else:
        return False, "[ERROR] Please add config for payload request headers!"


def update_x_gr_nonce(force: bool = False) -> tuple:
    """Auto refresh token X-Gr-Nonce"""
    end_point = "https://gravatar.com/profile/avatars"
    configs = load_configs(filter_key="")
    if "headers" in configs:
        interval = configs.get('x_gr_update_interval', 900)
        if force or 'x_gr_update_time' not in configs or time.time() - configs['x_gr_update_time'] > interval:
            ss_rq = requests.session()
            rp = ss_rq.get(end_point, headers=configs['headers'])
            if rp.status_code:
                if "data-rest-api-nonce=\"" in rp.text:
                    pattern = re.compile("data-rest-api-nonce=\".*?\">")
                    groups = pattern.search(rp.text)
                    if groups:
                        configs['headers']['X-Gr-Nonce'] = groups[0].replace("data-rest-api-nonce=\"", "").replace("\">", "")
                        configs['x_gr_update_time'] = time.time()
                        if 'x_gr_update_interval' not in configs:
                            configs['x_gr_update_interval'] = 900
                        save_configs(configs)
                        return True, "NEW_TOKEN_SAVED"
            else:
                return False, "CONNECT_FAILED"
        else:
            return False, "NOT_NEED_UPDATE"
    else:
        return False, "NO_CONFIG_EXIST"


def show_help():
    print("""--- USAGE ---
* Get data: `python gravatar.py get_data`, to filter email or image `python gravatar.py get_data <filter-text-here>`
* Add email: `python gravatar.py add_email <email-address>` (automatic check inbox to get active URL if these is available email configs)
* Set avatar for an exist email: `python gravatar.py set_avatar <email-address> <image-id>`
* Set alt-text for an exist image: `python gravatar.py set_alt_text <image-id> <your-text>`
* Delete an exist image: `python gravatar.py delete_image <image-id>`
* Upload image from local: `python gravatar.py upload_image <path-to-image-file>`
* **Upload image and set email avatar**: `python gravatar.py upload_and_set_avatar <email-address> <path-to-image-file>`
* **Scan directory and set email avatar based-on filename**: `python gravatar.py set_avatar_from_dir <path-to-directory> <domain>`
* Refresh `X-Gr-Nonce`: `python gravatar.py update_x_gr_nonce` (just for test, this token refresh automatically)

--- CONFIG ---
Before execute, it's required user confirm by input 'y' or 'Y', to ignore it, set environment param: `GRAVATAR_IGNORE_CONFIRM=1`
    """)


if __name__ == "__main__":
    if len(sys.argv) > 1:
        function_name = sys.argv[1]
        if function_name in ('-h', '--help'):
            show_help()
            exit()
        params = sys.argv[1:]
        params.pop(0)
        print("-" * 20)
        print(f"- Function name: {function_name}")
        print(f"- Params: {params}")
        allow_execute = False
        if os.getenv('GRAVATAR_IGNORE_CONFIRM', '0') == '0':
            cf = input("Press y/Y to continue... ")
            allow_execute = cf.lower() == 'y'
        else:
            allow_execute = True
        if allow_execute:
            try:
                result = getattr(sys.modules[__name__], function_name)(*params)
                print("-" * 10)
                print(f"Result:")
                pprint(result)
            except Exception:
                print("-" * 10)
                print(f"Error, traceback: {format_exc()}")
    else:
        show_help()
