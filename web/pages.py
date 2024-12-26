import os
import logging
import web.login_ulits as login_ulits
import web.conf as conf
import time
from urllib.parse import urlparse
from flask import Flask, render_template, request, jsonify, redirect, url_for

from recommendModel.getData import get_history_data, get_hot_data, get_recommand_data


logging.basicConfig(level = logging.INFO,format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

conf = conf.conf()
cookie_file_path = conf.cookie_file_path



def dashboard():
    global cookie_str
    headers["Cookie"] = cookie_str
    history_info = get_history_info()
    for x in history_info:
        parsed_url = urlparse(x["pic"])
        file_name = os.path.basename(parsed_url.path)
        full_path = os.path.join(img_path_rel, file_name)
        x["pic"] = os.path.normpath(full_path).replace("\\", "/")
        temp = []
        count = 0
        for xx in x["tag"]:
            if len(xx) <= 8 and count < 2:
                temp.append(xx)
                count += 1
        x["tag"] = temp
    return render_template(
        "dashboard.html", cookie_str=cookie_str, history_info=history_info
    )


def home():
    global cookie_str, headers
    if os.path.exists(cookie_file_path):
        with open(cookie_file_path, "r") as f:
            cookie_str = f.read()
            headers["Cookie"] = cookie_str
            print(f"read:{cookie_str}")
            return dashboard()
    else:
        return login()


def login():
    url, qrcode_key = login_ulits.getQRcodeKey()
    logger.info("Key: " + qrcode_key)
    qr_base64 = login_ulits.QRkey2Base64(url)
    if url and qrcode_key:
        return render_template("login.html", qr_code=qr_base64, qrcode_key=qrcode_key)
    else:
        logger.warning("Failed to login")
        return jsonify({"success": False})

def logout():
    if os.path.exists(cookie_file_path):
        os.remove(cookie_file_path)
    return jsonify({"success": True})