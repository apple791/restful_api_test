"""仅使用 Booker 配置，不要求安装 MySQL 或设置数据库密码。"""
import os

BASE_URL = os.getenv("BOOKER_BASE_URL", "https://restful-booker.herokuapp.com").rstrip("/")
# 下列默认值仅为 Restful-booker 公开练习服务的示例凭据。
USERNAME = os.getenv("BOOKER_USERNAME", "admin")
PASSWORD = os.getenv("BOOKER_PASSWORD", "password123")
TIMEOUT = float(os.getenv("BOOKER_TIMEOUT", "10"))
