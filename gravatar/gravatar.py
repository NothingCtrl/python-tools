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


def add_email(email: str) -> tuple:
    """Add an email address to Gravatar account"""
    end_point = "https://api.gravatar.com/v2/users/me/identity?_locale=&source=web-app-editor"
    headers = load_configs()
    if headers:
        update_x_gr_nonce()
        ss_rq = requests.session()
        rp = ss_rq.post(end_point, data={"email": email, "locate": "en"}, headers=headers)
        if rp.status_code:
            return True, ""
        else:
            return False, f"Response error, status code: {rp.status_code}, text: {rp.text}"
    else:
        return False, "[ERROR] Please add config for payload request headers!"


def set_avatar(email: str, image_id: str) -> tuple:
    end_point = "https://api.gravatar.com/v2/users/me/identity/MD5_HASH?_locale=&source=web-app-editor"
    headers = load_configs()
    if headers:
        update_x_gr_nonce()
        ss_rq = requests.session()
        email_hash = hashlib.md5(email.strip().lower().encode('utf-8')).hexdigest()
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
            return False, f"Response error, status code: {rp.status_code}, text: {rp.text}"
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
            return False, f"Response error, status code: {rp.status_code}, text: {rp.text}"
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
            return False, f"Response error, status code: {rp.status_code}, text: {rp.text}"
    else:
        return False, "[ERROR] Please add config for payload request headers!"


def upload_image(file_path: str, alt_text_filename: bool = True) -> tuple:
    """Upload an image avatar"""
    end_point = "https://api.gravatar.com/v2/users/me/image?_locale=&source=web-app-editor"
    headers = load_configs()
    if headers:
        update_x_gr_nonce()
        ss_rq = requests.session()
        files = {'image': (os.path.basename(file_path), open(file_path, 'rb'), "image/jpeg")}
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
                            print(f"Set altText failed, error:\n{_error}")
                    return True, image_data
            except Exception:
                pass
            return False, rp.text
        else:
            return False, f"Response error, status code: {rp.status_code}, text: {rp.text}"
    else:
        return False, "[ERROR] Please add config for payload request headers!"


def upload_and_set_avatar(email_address: str, file_path: str) -> tuple:
    status, _data = upload_image(file_path)
    if status:
        status, error = set_avatar(email_address, _data['image_id'])
        if status:
            return True, _data['image_id'], "IMAGE_UPLOADED_AND_SET"
        else:
            return False, _data['image_id'], error
    else:
        return False, _data


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


if __name__ == "__main__":
    if len(sys.argv) > 1:
        function_name = sys.argv[1]
        params = sys.argv[1:]
        params.pop(0)
        print("-" * 20)
        print(f"- Function name: {function_name}")
        print(f"- Params: {params}")
        cf = input("Press y/Y to continue... ")
        if cf.lower() == 'y':
            try:
                result = getattr(sys.modules[__name__], function_name)(*params)
                print("-" * 10)
                print(f"Result:")
                pprint(result)
            except Exception:
                print("-" * 10)
                print(f"Error, traceback: {format_exc()}")
