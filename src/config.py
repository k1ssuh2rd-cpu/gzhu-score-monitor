"""
配置管理模块
"""
import os
from pathlib import Path
from typing import List

BASE_DIR = Path(__file__).resolve().parent.parent


def load_env_file(env_file: Path = None) -> None:
    """
    加载 .env 文件
    
    Args:
        env_file: .env 文件路径
    """
    if env_file is None:
        env_file = BASE_DIR / ".env"
    
    if not env_file.exists():
        return
    
    with open(env_file, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#') or '=' not in line:
                continue
            key, value = line.split('=', 1)
            key = key.strip()
            value = value.strip()
            if value and value[0] in ('"', "'") and value[0] == value[-1]:
                value = value[1:-1]
            os.environ[key] = value


load_env_file()


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
    
    # 心跳邮件配置
    HEARTBEAT_ENABLED: bool = os.getenv("HEARTBEAT_ENABLED", "true").lower() == "true"
    HEARTBEAT_INTERVAL: int = int(os.getenv("HEARTBEAT_INTERVAL", "3600"))  # 默认1小时
    
    LOG_DIR: Path = BASE_DIR / "logs"
    LOG_DIR.mkdir(exist_ok=True)
    LOG_FILE: Path = LOG_DIR / "score_monitor.log"
    
    REQUEST_TIMEOUT: int = 30
    MAX_RETRY: int = 3
    RETRY_DELAY: int = 5


config = Config()
