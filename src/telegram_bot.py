"""Telegram Bot 模块 — 通过 Telegram 随时随地查成绩"""
import time
import requests
from typing import Optional, Callable
from datetime import datetime

from src.config import config
from src.logger import logger


class TelegramBot:
    """Telegram Bot，轮询命令并回复"""

    API_BASE = "https://api.telegram.org"

    def __init__(self, token: str, query_handler: Callable[[], str]):
        self.token = token
        self.query_handler = query_handler
        self.offset: Optional[int] = None

    def _api(self, method: str, data: dict) -> dict:
        try:
            resp = requests.post(
                f"{self.API_BASE}/bot{self.token}/{method}",
                json=data,
                timeout=15
            )
            return resp.json()
        except Exception as e:
            logger.error(f"Telegram API 请求失败 [{method}]: {e}")
            return {"ok": False}

    def _send_message(self, chat_id: int, text: str) -> None:
        result = self._api("sendMessage", {
            "chat_id": chat_id,
            "text": text,
            "parse_mode": "HTML",
            "disable_web_page_preview": True,
        })
        if result.get("ok"):
            logger.info(f"已回复 Telegram 消息 → chat_id={chat_id}")
        else:
            logger.error(f"发送 Telegram 消息失败: {result}")

    def _get_updates(self) -> list:
        data: dict = {"timeout": 30, "limit": 10}
        if self.offset is not None:
            data["offset"] = self.offset
        result = self._api("getUpdates", data)
        return result.get("result", [])

    def _handle_update(self, update: dict) -> None:
        msg = update.get("message")
        if not msg:
            return
        chat_id = msg.get("chat", {}).get("id")
        text = (msg.get("text") or "").strip()
        if not chat_id or not text:
            return

        logger.info(f"收到 Telegram 消息: chat_id={chat_id}, text={text[:50]}")
        response = self._dispatch(chat_id, text)
        if response:
            self._send_message(chat_id, response)

    def _dispatch(self, chat_id: int, text: str) -> Optional[str]:
        cmd = text.lower().split()[0] if text else ""

        if cmd == "/start":
            return (
                "🎓 <b>广州大学成绩监测 Bot</b>\n\n"
                "支持的命令：\n"
                "/check — 立即查询当前成绩\n"
                "/help — 查看帮助\n\n"
                "有新成绩发布时也会自动通知你。"
            )

        if cmd == "/check":
            return self._do_check()

        if cmd == "/help":
            return (
                "📋 <b>使用说明</b>\n\n"
                "/check — 查询当前所有成绩\n"
                "/start — 开始使用\n"
                "/help — 显示本帮助\n\n"
                "成绩更新时会自动推送通知。"
            )

        return None

    def _do_check(self) -> str:
        try:
            result = self.query_handler()
            return result
        except Exception as e:
            logger.error(f"查询成绩异常: {e}")
            return "查询成绩时出错，请稍后重试。"

    def run(self) -> None:
        """启动 Bot，轮询 Telegram 消息"""
        logger.info("Telegram Bot 已启动，等待命令...")
        print("Telegram Bot 已启动，按 Ctrl+C 停止")

        while True:
            try:
                updates = self._get_updates()
                for update in updates:
                    self._handle_update(update)
                    self.offset = update["update_id"] + 1
            except KeyboardInterrupt:
                raise
            except Exception as e:
                logger.error(f"Bot 轮询异常: {e}")
                time.sleep(5)


def build_check_handler():
    """构建成绩查询回调函数，供 TelegramBot 使用"""
    from src.gzhu_login import GZHULogin
    from src.score_parser import parse_course_scores, ScoreParseError

    def handler() -> str:
        gzhu = GZHULogin(config.GZHU_USERNAME, config.GZHU_PASSWORD)
        if not gzhu.login():
            return "登录教务系统失败，请检查账号密码。"

        data = gzhu.query_scores()
        if not data:
            return "查询成绩失败，请稍后重试。"

        try:
            scores = parse_course_scores(data)
        except ScoreParseError:
            return "解析成绩数据失败。"

        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        if not scores:
            return f"📭 <b>暂无已发布的成绩</b>\n\n查询时间：{now}"

        lines = [f"📋 <b>当前成绩 · {len(scores)} 门</b>", f"查询时间：{now}", ""]
        for course, score in scores.items():
            lines.append(f"<b>{course}</b>：{score}")

        return "\n".join(lines)

    return handler
