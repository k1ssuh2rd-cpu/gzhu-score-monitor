"""
主程序入口
"""
import time
import signal
import sys
from pathlib import Path
from typing import Optional

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.config import config
from src.logger import logger
from src.gzhu_login import GZHULogin, GZHULoginError
from src.score_parser import parse_course_scores, format_scores, ScoreParseError
from src.email_notifier import create_notifier, EmailSendError


class ScoreMonitor:
    """成绩监控类"""
    
    def __init__(self):
        self.gzhu_login: Optional[GZHULogin] = None
        self.notifier = create_notifier()
        self.previous_score_count = 0
        self.running = False
    
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
        
        self.gzhu_login = GZHULogin(config.GZHU_USERNAME, config.GZHU_PASSWORD)
        
        if not self.gzhu_login.login():
            logger.error("登录失败，请检查账号密码")
            return False
        
        initial_data = self.gzhu_login.query_scores()
        if initial_data:
            try:
                initial_scores = parse_course_scores(initial_data)
                self.previous_score_count = len(initial_scores)
                logger.info(f"初始化完成，当前共有{self.previous_score_count}门课程成绩")
                return True
            except ScoreParseError:
                logger.error("解析初始成绩数据失败")
                return False
        else:
            logger.error("获取初始成绩数据失败")
            return False
    
    def check_scores(self) -> None:
        """
        检查成绩变化
        """
        data = self.gzhu_login.query_scores()
        if not data:
            logger.warning("获取成绩数据失败，跳过本次检查")
            return
        
        try:
            scores = parse_course_scores(data)
            current_count = len(scores)
            
            logger.info(f"当前课程数: {current_count}, 上次课程数: {self.previous_score_count}")
            
            if current_count != self.previous_score_count:
                logger.info("检测到成绩变化！")
                
                body = format_scores(scores)
                try:
                    self.notifier.send(
                        subject=config.EMAIL_SUBJECT,
                        body=body
                    )
                    self.previous_score_count = current_count
                except EmailSendError:
                    logger.error("发送通知邮件失败")
            else:
                logger.debug("成绩无变化")
                
        except ScoreParseError:
            logger.error("解析成绩数据失败")
    
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
                self.check_scores()
                time.sleep(config.CHECK_INTERVAL)
        except KeyboardInterrupt:
            logger.info("接收到中断信号，正在停止...")
        except Exception as e:
            logger.error(f"监控过程中发生错误: {e}")
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
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    monitor = ScoreMonitor()
    monitor.run()


if __name__ == "__main__":
    main()
