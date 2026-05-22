"""
主程序入口
"""
import argparse
import json
import time
import signal
import sys
from typing import Dict, Optional
from datetime import datetime

from src.config import config, BASE_DIR
from src.logger import logger
from src.gzhu_login import GZHULogin, GZHULoginError
from src.score_parser import parse_course_scores, format_scores, ScoreParseError
from src.email_notifier import create_notifier, EmailSendError
from src.email_status_tracker import EmailStatusTracker
from src.templates import score_update, heartbeat

__version__ = "1.1.0"


class ScoreMonitor:
    """成绩监控类"""

    MAX_RECONNECT = 3

    def __init__(self):
        self.gzhu_login: Optional[GZHULogin] = None
        self.notifier = create_notifier()
        self.status_tracker = EmailStatusTracker()
        self.previous_score_count = 0
        self.previous_scores: Dict[str, str] = {}
        self.running = False
        self.last_heartbeat_time: Optional[datetime] = None
        self.reconnect_count = 0
    
    def initialize(self) -> bool:
        """
        初始化监控器
        
        Returns:
            初始化是否成功
        """
        if not config.GZHU_USERNAME or not config.GZHU_PASSWORD:
            logger.error("教务系统账号密码未配置，请检查.env文件")
            return False
        
        if not self.notifier:
            logger.error("邮件通知器初始化失败")
            return False
        
        self.gzhu_login = GZHULogin(
            config.GZHU_USERNAME,
            config.GZHU_PASSWORD,
            email_notifier=self.notifier,
            status_tracker=self.status_tracker
        )
        
        if not self.gzhu_login.login():
            logger.error("登录失败，请检查账号密码")
            return False
        
        initial_data = self.gzhu_login.query_scores()
        if initial_data:
            try:
                initial_scores = parse_course_scores(initial_data)
                self.previous_score_count = len(initial_scores)
                self.previous_scores = initial_scores.copy()
                logger.info(f"初始化完成，当前共有{self.previous_score_count}门课程成绩")
                return True
            except ScoreParseError:
                logger.error("解析初始成绩数据失败")
                return False
        else:
            logger.error("获取初始成绩数据失败")
            return False
    
    def _generate_score_update_email(
        self,
        new_scores: Dict[str, str],
        old_scores: Dict[str, str]
    ) -> str:
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        return score_update(new_scores, old_scores, current_time)
    
    def check_scores(self) -> None:
        """
        检查成绩变化
        """
        data = self.gzhu_login.query_scores()
        if not data:
            logger.warning("获取成绩数据失败，尝试重新登录...")
            if not self._try_reconnect():
                return
            data = self.gzhu_login.query_scores()
            if not data:
                return
        
        try:
            scores = parse_course_scores(data)
            current_count = len(scores)
            
            logger.info(f"当前课程数: {current_count}, 上次课程数: {self.previous_score_count}")
            
            if current_count != self.previous_score_count or scores != self.previous_scores:
                logger.info("检测到成绩变化！")
                
                email_body = self._generate_score_update_email(scores, self.previous_scores)
                
                try:
                    self.notifier.send(
                        subject=config.EMAIL_SUBJECT,
                        body=email_body,
                        is_html=True
                    )
                    self.previous_score_count = current_count
                    self.previous_scores = scores.copy()
                    if self.status_tracker:
                        self.status_tracker.add_status(
                            email_type="score",
                            subject=config.EMAIL_SUBJECT,
                            recipients=self.notifier.receiver_emails,
                            status="success",
                            additional_info={
                                "previous_count": len(self.previous_scores),
                                "current_count": current_count,
                                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                            }
                        )
                except EmailSendError:
                    logger.error("发送通知邮件失败")
                    if self.status_tracker:
                        self.status_tracker.add_status(
                            email_type="score",
                            subject=config.EMAIL_SUBJECT,
                            recipients=self.notifier.receiver_emails,
                            status="failed",
                            error_message="邮件发送失败",
                            additional_info={
                                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                            }
                        )
            else:
                logger.debug("成绩无变化")
                
        except ScoreParseError:
            logger.error("解析成绩数据失败")

    def _try_reconnect(self) -> bool:
        """尝试重新登录，返回是否成功"""
        if self.reconnect_count >= self.MAX_RECONNECT:
            logger.error(f"已达最大重连次数({self.MAX_RECONNECT})，放弃重连")
            return False
        self.reconnect_count += 1
        logger.info(f"尝试重新登录 (第{self.reconnect_count}/{self.MAX_RECONNECT}次)...")
        if self.gzhu_login.login():
            self.reconnect_count = 0
            logger.info("重新登录成功")
            return True
        logger.error("重新登录失败")
        return False

    def _generate_heartbeat_email(self) -> str:
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        if self.last_heartbeat_time:
            delta = datetime.now() - self.last_heartbeat_time
            hours = int(delta.total_seconds() // 3600)
            minutes = int((delta.total_seconds() % 3600) // 60)
            uptime = f"{hours}小时{minutes}分钟"
        else:
            uptime = "刚刚启动"
        return heartbeat(current_time, uptime, self.previous_score_count)
    
    def _check_and_send_heartbeat(self) -> None:
        """
        检查并发送心跳邮件
        """
        if not config.HEARTBEAT_ENABLED:
            return
        
        current_time = datetime.now()
        
        # 首次运行或到达心跳间隔时发送
        should_send = (
            self.last_heartbeat_time is None or
            (current_time - self.last_heartbeat_time).total_seconds() >= config.HEARTBEAT_INTERVAL
        )
        
        if should_send:
            logger.info("发送心跳邮件...")
            try:
                email_body = self._generate_heartbeat_email()
                self.notifier.send(
                    subject="[心跳] 成绩监测系统运行正常",
                    body=email_body,
                    is_html=True
                )
                self.last_heartbeat_time = current_time
                logger.info("心跳邮件发送成功")
                if self.status_tracker:
                    self.status_tracker.add_status(
                        email_type="heartbeat",
                        subject="[心跳] 成绩监测系统运行正常",
                        recipients=self.notifier.receiver_emails,
                        status="success",
                        additional_info={
                            "timestamp": current_time.strftime("%Y-%m-%d %H:%M:%S"),
                            "course_count": self.previous_score_count
                        }
                    )
            except EmailSendError as e:
                logger.error(f"心跳邮件发送失败: {e}")
                if self.status_tracker:
                    self.status_tracker.add_status(
                        email_type="heartbeat",
                        subject="[心跳] 成绩监测系统运行正常",
                        recipients=self.notifier.receiver_emails,
                        status="failed",
                        error_message=str(e),
                        additional_info={
                            "timestamp": current_time.strftime("%Y-%m-%d %H:%M:%S")
                        }
                    )
    
    def run_once(self) -> None:
        """查询一次成绩并打印结果"""
        if not self.initialize():
            logger.error("初始化失败")
            return
        data = self.gzhu_login.query_scores()
        if data:
            try:
                scores = parse_course_scores(data)
                print(format_scores(scores))
            except ScoreParseError:
                logger.error("解析成绩数据失败")
        else:
            logger.error("查询成绩失败")

    def run_test(self) -> None:
        """发送测试邮件验证配置"""
        if not config.GZHU_USERNAME or not config.GZHU_PASSWORD:
            logger.error("教务系统账号密码未配置，请检查.env文件")
            return
        if not self.notifier:
            logger.error("邮件通知器初始化失败")
            return
        self.gzhu_login = GZHULogin(
            config.GZHU_USERNAME,
            config.GZHU_PASSWORD,
            email_notifier=self.notifier,
            status_tracker=self.status_tracker
        )
        if self.gzhu_login.login():
            print("登录成功，测试邮件已发送")
        else:
            print("登录失败，请检查账号密码和网络连接")

    def run_check(self) -> None:
        """CI模式：查询一次，对比上次状态，有变化则发邮件通知"""
        if not self.initialize():
            logger.error("初始化失败")
            sys.exit(1)

        state_file = BASE_DIR / "status" / "scores.json"
        previous_scores: Dict[str, str] = {}
        if state_file.exists():
            try:
                previous_scores = json.loads(state_file.read_text(encoding="utf-8"))
            except Exception:
                pass

        data = self.gzhu_login.query_scores()
        if not data:
            logger.error("查询成绩失败")
            sys.exit(1)

        try:
            scores = parse_course_scores(data)
        except ScoreParseError:
            logger.error("解析成绩数据失败")
            sys.exit(1)

        if scores != previous_scores:
            logger.info(f"检测到成绩变化 (上次{len(previous_scores)}门 → 本次{len(scores)}门)，发送通知...")
            body = self._generate_score_update_email(scores, previous_scores)
            try:
                self.notifier.send(subject=config.EMAIL_SUBJECT, body=body, is_html=True)
                logger.info("通知邮件发送成功")
            except EmailSendError:
                logger.error("发送通知邮件失败")
                sys.exit(1)
        else:
            logger.info(f"成绩无变化 (共{len(scores)}门)")

        state_file.write_text(json.dumps(scores, ensure_ascii=False), encoding="utf-8")

    def run(self) -> None:
        """
        运行监控循环
        """
        if not self.initialize():
            logger.error("初始化失败，程序退出")
            return

        self.running = True
        logger.info("开始监控成绩变化...")
        logger.info(f"检查间隔: {config.CHECK_INTERVAL}秒")

        try:
            while self.running:
                try:
                    self.check_scores()
                    self._check_and_send_heartbeat()
                    self.reconnect_count = 0
                except Exception as e:
                    logger.error(f"检查异常: {e}")
                    self._try_reconnect()
                time.sleep(config.CHECK_INTERVAL)
        except KeyboardInterrupt:
            logger.info("接收到中断信号，正在停止...")
        finally:
            self.stop()
    
    def stop(self) -> None:
        """
        停止监控
        """
        self.running = False
        logger.info("监控已停止")


def signal_handler(signum, frame):
    """信号处理函数"""
    logger.info(f"接收到信号 {signum}，准备退出...")
    sys.exit(0)


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="广州大学成绩监测系统")
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    parser.add_argument("--once", action="store_true", help="查询一次成绩并打印结果")
    parser.add_argument("--test", action="store_true", help="发送测试邮件验证配置并退出")
    parser.add_argument("--check", action="store_true", help="CI模式：查询并对比上次，有变化则发邮件通知")
    parser.add_argument("--bot", action="store_true", help="启动 Telegram Bot")
    args = parser.parse_args()

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    monitor = ScoreMonitor()

    if args.test:
        monitor.run_test()
    elif args.once:
        monitor.run_once()
    elif args.check:
        monitor.run_check()
    elif args.bot:
        from src.telegram_bot import TelegramBot, build_check_handler
        token = config.TELEGRAM_BOT_TOKEN
        if not token:
            print("未配置 TELEGRAM_BOT_TOKEN，请在 .env 中添加")
            sys.exit(1)
        handler = build_check_handler()
        bot = TelegramBot(token, handler)
        bot.run()
    else:
        monitor.run()


if __name__ == "__main__":
    main()
