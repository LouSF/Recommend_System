import os
import time
from urllib.parse import urlparse
import requests
import qrcode
import base64
from PIL import Image
from io import BytesIO
from flask import Flask, render_template, request, jsonify, redirect, url_for
import logging

logging.basicConfig(level = logging.INFO,format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


QR_CODE_GENERATE_URL = (
    "https://passport.bilibili.com/x/passport-login/web/qrcode/generate"
)
QR_CODE_POLL_URL = "https://passport.bilibili.com/x/passport-login/web/qrcode/poll"

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36"
}

cookie_file_path = "user_data/cookie.txt"
cookie_data = {}
cookie_str = ""

img_path = ""
img_path_rel = ""


def getQRcodeKey():
    response = requests.get(QR_CODE_GENERATE_URL, headers=headers)
    print(response)
    if response.status_code == 200:
        data = response.json()
        if data["code"] == 0:
            logger.info("success get QR code")
            return data["data"]["url"] + "main-fe-header", data["data"]["qrcode_key"]
        else:
            logger.warning("fail to get QR code")
            return None, None
    return None, None

def QRkey2Base64(url: str):
    if url:
        # 创建二维码
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(url)
        qr.make(fit=True)
        img = qr.make_image(fill="black", back_color="white")
        buffered = BytesIO()
        img.save(buffered, format="BMP")

        qr_base64 = base64.b64encode(buffered.getvalue()).decode("utf-8")
        logger.info("Create QR code")
        return qr_base64
    logger.warning("Failed to create QR code")
    return None

def check_qrcode_status(qrcode_key):
    global cookie_data, cookie_str
    response = requests.get(
        QR_CODE_POLL_URL, params={"qrcode_key": qrcode_key}, headers=headers
    )

    if response.status_code == 200:
        data = response.json()
        code = data["data"]["code"]
        print(data)
        if code == 0:
            cookie_data = response.cookies.get_dict()
            print(cookie_data)
            cookie_str = "; ".join(
                [f"{key}={value}" for key, value in cookie_data.items()]
            )
            cookie_str = "buvid3=1; " + cookie_str
            print(cookie_str)
            timestamp = data["data"]["timestamp"]
            url = data["data"]["url"]
            return code, timestamp, url, cookie_str
        else:
            logger.warning("Failed to login")
            return code, None, None, None
    return None, None, None, None

def qrcode_status():
    global headers
    qrcode_key = request.args.get("qrcode_key")
    if not qrcode_key:
        logger.warning("Missing qrcode_key")
        return jsonify({"error": "Missing qrcode_key"}), 400

    status, timestamp, url, cookies = check_qrcode_status(qrcode_key)
    if status == 86101:
        logger.info("QR code not scanned")
        return jsonify({"status": "not scanned"}), 200
    elif status == 86038:
        logger.warning("QR code expired")
        return jsonify({"error": "QR code expired"}), 400
    elif status == 86090:
        logger.info("QR code scanned but not confirmed")
        return jsonify({"status": "scanned but not confirmed"}), 200
    elif status == 0:
        logger.info("Login success")
        print(cookies)

        cookie_dir = os.path.dirname(cookie_file_path)
        if not os.path.exists(cookie_dir):
            try:
                os.makedirs(cookie_dir)
                logger.info(f"create folder succeed: {cookie_dir}")
            except Exception as e:
                logger.warning(f"create folder error: {e}")

        try:
            with open(cookie_file_path, "w") as f:
                f.write(f"{cookies}")
            logger.info(f"save SESSDATA succeed: {cookie_file_path}")
            headers["Cookie"] = cookies
        except Exception as e:
            logger.warning(f"save SESSDATA error: {e}")
        return (
            jsonify(
                {
                    "status": "login success",
                    "timestamp": timestamp,
                    "url": url,
                    "cookies": cookies,
                }
            ),
            200,
        )