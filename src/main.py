"""
主程序入口
"""
import time
import signal
import sys
from pathlib import Path
from typing import Optional, Dict
from datetime import datetime

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.config import config
from src.logger import logger
from src.gzhu_login import GZHULogin, GZHULoginError
from src.score_parser import parse_course_scores, format_scores, ScoreParseError
from src.email_notifier import create_notifier, EmailSendError
from src.email_status_tracker import EmailStatusTracker


class ScoreMonitor:
    """成绩监控类"""
    
    def __init__(self):
        self.gzhu_login: Optional[GZHULogin] = None
        self.notifier = create_notifier()
        self.status_tracker = EmailStatusTracker()
        self.previous_score_count = 0
        self.previous_scores: Dict[str, str] = {}
        self.running = False
        self.last_heartbeat_time: Optional[datetime] = None
    
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
        """
        生成成绩更新邮件正文
        
        Args:
            new_scores: 新成绩字典
            old_scores: 旧成绩字典
            
        Returns:
            HTML格式的邮件正文
        """
        new_courses = set(new_scores.keys()) - set(old_scores.keys())
        updated_courses = []
        
        for course in old_scores.keys():
            if course in new_scores and new_scores[course] != old_scores[course]:
                updated_courses.append(course)
        
        new_courses_html = ""
        if new_courses:
            rows = ""
            for course in new_courses:
                rows += f"""
                    <tr>
                        <td style="padding: 12px; border-bottom: 1px solid #e0e0e0;">{course}</td>
                        <td style="padding: 12px; border-bottom: 1px solid #e0e0e0; text-align: center; font-weight: bold; color: #4CAF50;">{new_scores[course]}</td>
                    </tr>
                """
            new_courses_html = f"""
                <div class="info-section">
                    <div class="info-title">📚 新增课程成绩</div>
                    <div style="background-color: white; border-radius: 3px; overflow: hidden;">
                        <table style="width: 100%; border-collapse: collapse; margin-top: 10px;">
                            <thead>
                                <tr style="background-color: #4CAF50; color: white;">
                                    <th style="padding: 12px; text-align: left;">课程名称</th>
                                    <th style="padding: 12px; text-align: center;">成绩</th>
                                </tr>
                            </thead>
                            <tbody>
                                {rows}
                            </tbody>
                        </table>
                    </div>
                    <div style="margin-top: 10px; color: #666; font-size: 14px;">
                        共 <strong>{len(new_courses)}</strong> 门新课程
                    </div>
                </div>
            """
        
        updated_courses_html = ""
        if updated_courses:
            rows = ""
            for course in updated_courses:
                old_score = old_scores[course]
                new_score = new_scores[course]
                change_type = "↑" if float(new_score) > float(old_score) else "↓"
                change_color = "#4CAF50" if float(new_score) > float(old_score) else "#f44336"
                rows += f"""
                    <tr>
                        <td style="padding: 12px; border-bottom: 1px solid #e0e0e0;">{course}</td>
                        <td style="padding: 12px; border-bottom: 1px solid #e0e0e0; text-align: center;">{old_score}</td>
                        <td style="padding: 12px; border-bottom: 1px solid #e0e0e0; text-align: center; font-weight: bold; color: {change_color};">{new_score} {change_type}</td>
                    </tr>
                """
            updated_courses_html = f"""
                <div class="info-section">
                    <div class="info-title">📊 成绩更新对比</div>
                    <div style="background-color: white; border-radius: 3px; overflow: hidden;">
                        <table style="width: 100%; border-collapse: collapse; margin-top: 10px;">
                            <thead>
                                <tr style="background-color: #2196F3; color: white;">
                                    <th style="padding: 12px; text-align: left;">课程名称</th>
                                    <th style="padding: 12px; text-align: center;">原成绩</th>
                                    <th style="padding: 12px; text-align: center;">新成绩</th>
                                </tr>
                            </thead>
                            <tbody>
                                {rows}
                            </tbody>
                        </table>
                    </div>
                    <div style="margin-top: 10px; color: #666; font-size: 14px;">
                        共 <strong>{len(updated_courses)}</strong> 门课程成绩更新
                    </div>
                </div>
            """
        
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        html_body = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    line-height: 1.6;
                    color: #333;
                    max-width: 600px;
                    margin: 0 auto;
                    padding: 20px;
                    background-color: #f5f5f5;
                }}
                .header {{
                    background: linear-gradient(135deg, #2196F3 0%, #1976D2 100%);
                    color: white;
                    padding: 30px 20px;
                    text-align: center;
                    border-radius: 10px 10px 0 0;
                    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                }}
                .header h2 {{
                    margin: 0;
                    font-size: 24px;
                    font-weight: 600;
                }}
                .header p {{
                    margin: 10px 0 0 0;
                    opacity: 0.9;
                    font-size: 14px;
                }}
                .content {{
                    background-color: white;
                    padding: 30px;
                    border: 1px solid #e0e0e0;
                    border-top: none;
                    border-radius: 0 0 10px 10px;
                    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                }}
                .info-section {{
                    margin-bottom: 25px;
                    padding: 20px;
                    background-color: #f9f9f9;
                    border-left: 4px solid #2196F3;
                    border-radius: 5px;
                }}
                .info-title {{
                    font-weight: bold;
                    color: #2196F3;
                    margin-bottom: 15px;
                    font-size: 18px;
                    display: flex;
                    align-items: center;
                }}
                .info-title::before {{
                    content: "▶";
                    margin-right: 8px;
                    font-size: 12px;
                }}
                .summary {{
                    background-color: #e3f2fd;
                    border-left: 4px solid #2196F3;
                    padding: 15px;
                    margin-bottom: 25px;
                    border-radius: 5px;
                }}
                .summary-item {{
                    margin: 8px 0;
                    font-size: 14px;
                }}
                .summary-item strong {{
                    color: #1976D2;
                }}
                .footer {{
                    margin-top: 30px;
                    text-align: center;
                    color: #999;
                    font-size: 12px;
                    padding-top: 20px;
                    border-top: 1px solid #e0e0e0;
                }}
                table {{
                    font-size: 14px;
                }}
            </style>
        </head>
        <body>
            <div class="header">
                <h2>🎯 成绩更新通知</h2>
                <p>广州大学成绩监测系统</p>
            </div>
            <div class="content">
                <div class="summary">
                    <div class="summary-item"><strong>📅 更新时间:</strong> {current_time}</div>
                    <div class="summary-item"><strong>📚 新增课程:</strong> {len(new_courses)} 门</div>
                    <div class="summary-item"><strong>📊 更新课程:</strong> {len(updated_courses)} 门</div>
                </div>
                
                {new_courses_html}
                
                {updated_courses_html}
                
                <div class="footer">
                    <p>此邮件由成绩监测系统自动发送，请勿回复。</p>
                    <p>发送时间: {current_time}</p>
                </div>
            </div>
        </body>
        </html>
        """
        return html_body
    
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
            
            if current_count != self.previous_score_count or scores != self.previous_scores:
                logger.info("检测到成绩变化！")
                
                email_body = self._generate_score_update_email(scores, self.previous_scores)
                
                try:
                    success = self.notifier.send(
                        subject=config.EMAIL_SUBJECT,
                        body=email_body,
                        is_html=True
                    )
                    
                    if success:
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
    
    def _generate_heartbeat_email(self) -> str:
        """
        生成心跳邮件正文
        
        Returns:
            HTML格式的邮件正文
        """
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        uptime = ""
        if self.last_heartbeat_time:
            delta = datetime.now() - self.last_heartbeat_time
            hours = int(delta.total_seconds() // 3600)
            minutes = int((delta.total_seconds() % 3600) // 60)
            uptime = f"{hours}小时{minutes}分钟"
        else:
            uptime = "刚刚启动"
        
        html_body = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    line-height: 1.6;
                    color: #333;
                    max-width: 600px;
                    margin: 0 auto;
                    padding: 20px;
                    background-color: #f5f5f5;
                }}
                .header {{
                    background: linear-gradient(135deg, #4CAF50 0%, #388E3C 100%);
                    color: white;
                    padding: 30px 20px;
                    text-align: center;
                    border-radius: 10px 10px 0 0;
                    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                }}
                .header h2 {{
                    margin: 0;
                    font-size: 24px;
                    font-weight: 600;
                }}
                .header p {{
                    margin: 10px 0 0 0;
                    opacity: 0.9;
                    font-size: 14px;
                }}
                .content {{
                    background-color: white;
                    padding: 30px;
                    border: 1px solid #e0e0e0;
                    border-top: none;
                    border-radius: 0 0 10px 10px;
                    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                }}
                .status-box {{
                    background-color: #e8f5e9;
                    border-left: 4px solid #4CAF50;
                    padding: 20px;
                    margin-bottom: 20px;
                    border-radius: 5px;
                }}
                .status-item {{
                    margin: 10px 0;
                    font-size: 14px;
                }}
                .status-item strong {{
                    color: #2e7d32;
                }}
                .footer {{
                    margin-top: 30px;
                    text-align: center;
                    color: #999;
                    font-size: 12px;
                    padding-top: 20px;
                    border-top: 1px solid #e0e0e0;
                }}
            </style>
        </head>
        <body>
            <div class="header">
                <h2>💓 程序心跳检测</h2>
                <p>广州大学成绩监测系统</p>
            </div>
            <div class="content">
                <div class="status-box">
                    <div class="status-item"><strong>✅ 状态:</strong> 程序运行正常</div>
                    <div class="status-item"><strong>🕐 检测时间:</strong> {current_time}</div>
                    <div class="status-item"><strong>⏱️ 距上次心跳:</strong> {uptime}</div>
                    <div class="status-item"><strong>📚 当前监测课程数:</strong> {self.previous_score_count} 门</div>
                </div>
                <div class="footer">
                    <p>此邮件由成绩监测系统自动发送，用于确认程序正常运行。</p>
                    <p>发送时间: {current_time}</p>
                </div>
            </div>
        </body>
        </html>
        """
        return html_body
    
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
                success = self.notifier.send(
                    subject="[心跳] 成绩监测系统运行正常",
                    body=email_body,
                    is_html=True
                )
                
                if success:
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
                self._check_and_send_heartbeat()
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
