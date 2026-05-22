"""
配置管理模块
"""
import os
from pathlib import Path
from typing import List

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent

load_dotenv(BASE_DIR / ".env")


class Config:
    GZHU_USERNAME: str = os.getenv("GZHU_USERNAME", "")
    GZHU_PASSWORD: str = os.getenv("GZHU_PASSWORD", "")
    QQ_EMAIL: str = os.getenv("QQ_EMAIL", "")
    QQ_AUTH_CODE: str = os.getenv("QQ_AUTH_CODE", "")
    RECEIVER_EMAILS: List[str] = [
        email.strip() for email in os.getenv("RECEIVER_EMAILS", "").split(",") if email.strip()
    ]
    TEST_EMAIL: str = os.getenv("TEST_EMAIL", "")
    CHECK_INTERVAL: int = int(os.getenv("CHECK_INTERVAL", "5"))
    EMAIL_SUBJECT: str = os.getenv("EMAIL_SUBJECT", "新成绩通知")
    ENABLE_LOGIN_TEST_EMAIL: bool = os.getenv("ENABLE_LOGIN_TEST_EMAIL", "true").lower() == "true"

    HEARTBEAT_ENABLED: bool = os.getenv("HEARTBEAT_ENABLED", "true").lower() == "true"
    HEARTBEAT_INTERVAL: int = int(os.getenv("HEARTBEAT_INTERVAL", "86400"))

    TELEGRAM_BOT_TOKEN: str = os.getenv("TELEGRAM_BOT_TOKEN", "")

    LOG_DIR: Path = BASE_DIR / "logs"
    LOG_DIR.mkdir(exist_ok=True)
    LOG_FILE: Path = LOG_DIR / "score_monitor.log"

    REQUEST_TIMEOUT: int = 30
    MAX_RETRY: int = 3
    RETRY_DELAY: int = 5


config = Config()
