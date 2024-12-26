from flask import Flask
from web.pages import (
    home,
    login,
    dashboard,
    logout,
    # recommend_hot_vid,
    # recommend_explore_vid,
)

from web.login_ulits import qrcode_status

def mainPage():
    app = Flask(__name__)

    # 注册路由
    app.add_url_rule("/", "home", home)
    app.add_url_rule("/login", "login", login)
    app.add_url_rule("/qrcode_status", "qrcode_status", qrcode_status, methods=["GET"])
    app.add_url_rule("/dashboard", "dashboard", dashboard)
    app.add_url_rule("/logout", "logout", logout, methods=["POST"])
    app.add_url_rule(
        "/api/recommend-hot-vid",
        "recommend-hot-vid",
        recommend_hot_vid,
        methods=["GET"],
    )
    app.add_url_rule(
        "/api/recommend-explore-vid",
        "recommend-explore-vid",
        recommend_explore_vid,
        methods=["GET"],
    )

    return app
