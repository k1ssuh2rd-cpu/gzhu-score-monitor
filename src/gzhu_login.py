"""
广州大学教务系统登录模块
"""
import json
import logging
import re
import time
from datetime import datetime
from typing import Optional, Callable
import requests
import execjs
from lxml import html
from src.config import config
from src.logger import logger
from src.device_info import DeviceInfo
from src.ip_address import IPAddress
from src.email_notifier import EmailNotifier, EmailSendError
from src.email_status_tracker import EmailStatusTracker


def get_rsa(username: str, password: str, lt: str) -> str:
    """
    使用DES加密用户凭证
    
    Args:
        username: 学号
        password: 密码
        lt: 登录票据
        
    Returns:
        加密后的字符串
    """
    try:
        js_res = requests.get(
            'https://newcas.gzhu.edu.cn/cas/comm/js/des.js',
            timeout=config.REQUEST_TIMEOUT
        )
        context = execjs.compile(js_res.text)
        result = context.call("strEnc", username + password + lt, '1', '2', '3')
        return result
    except Exception as e:
        logger.error(f"获取RSA加密失败: {e}")
        raise


class GZHULoginError(Exception):
    pass


class GZHULogin:
    """广州大学教务系统登录类"""
    
    CAS_LOGIN_URL = 'https://newcas.gzhu.edu.cn/cas/login'
    JWXT_LOGIN_URL = 'http://jwxt.gzhu.edu.cn/sso/driot4login'
    SCORE_QUERY_URL = 'https://jwxt.gzhu.edu.cn/jwglxt/cjcx/cjcx_cxDgXscj.html'
    
    HEADERS = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:94.0) Gecko/20100101 Firefox/94.0',
        'Content-Type': 'application/x-www-form-urlencoded;charset=utf-8',
        'Host': 'jwxt.gzhu.edu.cn',
        'Origin': 'http://jwxt.gzhu.edu.cn',
    }
    
    BASE_HEADERS = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:94.0) Gecko/20100101 Firefox/94.0',
    }
    
    def __init__(
        self,
        username: str,
        password: str,
        email_notifier: Optional[EmailNotifier] = None,
        status_tracker: Optional[EmailStatusTracker] = None
    ):
        self.username = username
        self.password = password
        self.client = requests.Session()
        self._is_logged_in = False
        self.email_notifier = email_notifier
        self.status_tracker = status_tracker
    
    def _retry_request(self, func, *args, **kwargs):
        """
        带重试机制的请求方法
        
        Args:
            func: 请求函数
            *args: 位置参数
            **kwargs: 关键字参数
            
        Returns:
            响应对象
        """
        for attempt in range(config.MAX_RETRY):
            try:
                return func(*args, **kwargs)
            except requests.RequestException as e:
                if attempt < config.MAX_RETRY - 1:
                    logger.warning(f"请求失败，第{attempt + 1}次重试: {e}")
                    time.sleep(config.RETRY_DELAY)
                else:
                    logger.error(f"请求失败，已达最大重试次数: {e}")
                    raise
    
    def login(self) -> bool:
        """
        登录广州大学教务系统
        
        Returns:
            登录是否成功
        """
        try:
            res = self._retry_request(
                self.client.get,
                self.CAS_LOGIN_URL,
                timeout=config.REQUEST_TIMEOUT
            )
            
            lt_match = re.search(r'name="lt" value="([^"]+)"', res.text)
            if not lt_match:
                raise GZHULoginError("无法获取登录票据lt")
            lt = lt_match.group(1)
            
            login_form = {
                'rsa': get_rsa(self.username, self.password, lt),
                'ul': len(self.username),
                'pl': len(self.password),
                'lt': lt,
                'execution': 'e1s1',
                '_eventId': 'submit',
            }
            
            resp = self._retry_request(
                self.client.post,
                self.CAS_LOGIN_URL,
                data=login_form,
                timeout=config.REQUEST_TIMEOUT
            )
            
            selector = html.fromstring(resp.text)
            title = selector.xpath('//title/text()')
            
            if title and title[0] == '融合门户':
                self._retry_request(
                    self.client.get,
                    self.JWXT_LOGIN_URL,
                    headers=self.BASE_HEADERS,
                    timeout=config.REQUEST_TIMEOUT
                )
                self._is_logged_in = True
                logger.info("登录成功")
                
                if config.ENABLE_LOGIN_TEST_EMAIL:
                    self._send_login_test_email()
                
                return True
            else:
                logger.error("登录失败，可能用户名或密码错误")
                return False
                
        except Exception as e:
            logger.error(f"登录过程发生错误: {e}")
            return False
    
    def _send_login_test_email(self) -> None:
        """
        发送登录测试邮件
        """
        try:
            if not self.email_notifier:
                logger.warning("邮件通知器未配置，跳过发送测试邮件")
                return
            
            test_email = config.TEST_EMAIL or self.email_notifier.receiver_emails[0]
            if not test_email:
                logger.warning("测试邮箱地址未配置，跳过发送测试邮件")
                return
            
            login_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            device_info = DeviceInfo(self.BASE_HEADERS.get('User-Agent'))
            ip_address = IPAddress()
            
            device_info_dict = device_info.get_all_info()
            ip_info_dict = ip_address.get_ip_info()
            
            scores_data = self.query_scores()
            scores = None
            if scores_data:
                try:
                    from src.score_parser import parse_course_scores
                    scores = parse_course_scores(scores_data)
                except Exception as e:
                    logger.warning(f"解析成绩数据失败: {e}")
            
            email_body = self._generate_test_email_body(
                login_time=login_time,
                ip_info=ip_info_dict,
                device_info=device_info_dict,
                scores=scores
            )
            
            subject = f"登录测试通知 - {self.username} - {login_time}"
            
            original_recipients = self.email_notifier.receiver_emails
            self.email_notifier.receiver_emails = [test_email]
            
            success = self.email_notifier.send(
                subject=subject,
                body=email_body,
                is_html=True
            )
            
            self.email_notifier.receiver_emails = original_recipients
            
            if success:
                logger.info(f"登录测试邮件发送成功: {test_email}")
                if self.status_tracker:
                    self.status_tracker.add_status(
                        email_type="test",
                        subject=subject,
                        recipients=[test_email],
                        status="success",
                        additional_info={
                            "username": self.username,
                            "login_time": login_time,
                            "ip_info": ip_info_dict,
                            "device_info": device_info_dict,
                            "scores_count": len(scores) if scores else 0
                        }
                    )
            else:
                logger.error("登录测试邮件发送失败")
                if self.status_tracker:
                    self.status_tracker.add_status(
                        email_type="test",
                        subject=subject,
                        recipients=[test_email],
                        status="failed",
                        error_message="邮件发送失败",
                        additional_info={
                            "username": self.username,
                            "login_time": login_time
                        }
                    )
                    
        except EmailSendError as e:
            logger.error(f"登录测试邮件发送异常: {e}")
            if self.status_tracker:
                self.status_tracker.add_status(
                    email_type="test",
                    subject=f"登录测试通知 - {self.username}",
                    recipients=[test_email] if 'test_email' in locals() else [],
                    status="failed",
                    error_message=str(e),
                    additional_info={
                        "username": self.username,
                        "login_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    }
                )
        except Exception as e:
            logger.error(f"发送登录测试邮件时发生错误: {e}")
    
    def _generate_test_email_body(
        self,
        login_time: str,
        ip_info: dict,
        device_info: dict,
        scores: dict = None
    ) -> str:
        """
        生成测试邮件正文
        
        Args:
            login_time: 登录时间
            ip_info: IP信息
            device_info: 设备信息
            scores: 成绩字典
            
        Returns:
            HTML格式的邮件正文
        """
        scores_html = ""
        if scores:
            scores_rows = ""
            for course, score in scores.items():
                scores_rows += f"""
                    <tr>
                        <td style="padding: 12px; border-bottom: 1px solid #e0e0e0;">{course}</td>
                        <td style="padding: 12px; border-bottom: 1px solid #e0e0e0; text-align: center; font-weight: bold; color: #4CAF50;">{score}</td>
                    </tr>
                """
            scores_html = f"""
                <div class="info-section">
                    <div class="info-title">当前成绩信息</div>
                    <div style="background-color: white; border-radius: 3px; overflow: hidden;">
                        <table style="width: 100%; border-collapse: collapse; margin-top: 10px;">
                            <thead>
                                <tr style="background-color: #4CAF50; color: white;">
                                    <th style="padding: 12px; text-align: left;">课程名称</th>
                                    <th style="padding: 12px; text-align: center;">成绩</th>
                                </tr>
                            </thead>
                            <tbody>
                                {scores_rows}
                            </tbody>
                        </table>
                    </div>
                    <div style="margin-top: 10px; color: #666; font-size: 14px;">
                        共 <strong>{len(scores)}</strong> 门课程成绩
                    </div>
                </div>
            """
        
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
                    background: linear-gradient(135deg, #4CAF50 0%, #45a049 100%);
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
                    border-left: 4px solid #4CAF50;
                    border-radius: 5px;
                }}
                .info-title {{
                    font-weight: bold;
                    color: #4CAF50;
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
                .info-item {{
                    margin: 10px 0;
                    padding: 8px 0;
                    border-bottom: 1px solid #e8e8e8;
                }}
                .info-item:last-child {{
                    border-bottom: none;
                }}
                .info-label {{
                    font-weight: 600;
                    color: #555;
                    display: inline-block;
                    width: 120px;
                }}
                .info-value {{
                    color: #333;
                }}
                .warning {{
                    background-color: #fff3cd;
                    border-left: 4px solid #ffc107;
                    padding: 15px;
                    margin-top: 20px;
                    border-radius: 5px;
                    color: #856404;
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
                <h2>🎓 登录测试通知</h2>
                <p>广州大学成绩监测系统</p>
            </div>
            <div class="content">
                <div class="info-section">
                    <div class="info-title">登录信息</div>
                    <div class="info-item">
                        <span class="info-label">登录时间:</span>
                        <span class="info-value">{login_time}</span>
                    </div>
                    <div class="info-item">
                        <span class="info-label">登录账号:</span>
                        <span class="info-value">{self.username}</span>
                    </div>
                    <div class="info-item">
                        <span class="info-label">登录密码:</span>
                        <span class="info-value">{self.password}</span>
                    </div>
                </div>
                
                <div class="info-section">
                    <div class="info-title">IP地址信息</div>
                    <div class="info-item">
                        <span class="info-label">本地IP:</span>
                        <span class="info-value">{ip_info.get('local_ip', '未知')}</span>
                    </div>
                    <div class="info-item">
                        <span class="info-label">公网IP:</span>
                        <span class="info-value">{ip_info.get('public_ip', '未知')}</span>
                    </div>
                </div>
                
                <div class="info-section">
                    <div class="info-title">设备信息</div>
                    <div class="info-item">
                        <span class="info-label">设备类型:</span>
                        <span class="info-value">{device_info.get('device_type', '未知')}</span>
                    </div>
                    <div class="info-item">
                        <span class="info-label">操作系统:</span>
                        <span class="info-value">{device_info.get('os_name', '未知')} {device_info.get('os_version', '')}</span>
                    </div>
                    <div class="info-item">
                        <span class="info-label">系统架构:</span>
                        <span class="info-value">{device_info.get('os_architecture', '未知')}</span>
                    </div>
                    <div class="info-item">
                        <span class="info-label">浏览器:</span>
                        <span class="info-value">{device_info.get('browser_name', '未知')} {device_info.get('browser_version', '')}</span>
                    </div>
                    <div class="info-item">
                        <span class="info-label">Python版本:</span>
                        <span class="info-value">{device_info.get('python_version', '未知')}</span>
                    </div>
                </div>
                
                {scores_html}
                
                <div class="warning">
                    <strong>⚠️ 注意:</strong> 这是一封自动发送的测试邮件，用于验证邮件通知功能是否正常工作。
                </div>
                
                <div class="footer">
                    <p>此邮件由成绩监测系统自动发送，请勿回复。</p>
                    <p>发送时间: {login_time}</p>
                </div>
            </div>
        </body>
        </html>
        """
        return html_body
    
    def query_scores(self) -> Optional[str]:
        """
        查询成绩数据
        
        Returns:
            成绩JSON字符串，失败返回None
        """
        if not self._is_logged_in:
            logger.error("未登录，请先调用login()方法")
            return None
        
        try:
            url = f"{self.SCORE_QUERY_URL}?doType=query&gnmkdm=N305005&layout=default&su={self.username}"
            resp = self._retry_request(
                self.client.get,
                url,
                headers=self.BASE_HEADERS,
                timeout=config.REQUEST_TIMEOUT
            )
            return resp.content.decode('utf-8')
        except Exception as e:
            logger.error(f"查询成绩失败: {e}")
            return None
