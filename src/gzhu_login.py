"""
广州大学教务系统登录模块
"""
import json
import logging
import pickle
import re
import time
from datetime import datetime
from pathlib import Path
from typing import Optional, Callable
import requests
import execjs
from lxml import html
from src.config import config, BASE_DIR
from src.logger import logger
from src.device_info import DeviceInfo
from src.ip_address import IPAddress
from src.email_notifier import EmailNotifier, EmailSendError
from src.email_status_tracker import EmailStatusTracker
from src.templates import test_email as test_email_template


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
        self._session_path = BASE_DIR / "status" / "session.pkl"
        self._session_path.parent.mkdir(parents=True, exist_ok=True)
        self._try_load_session()
    
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
        登录广州大学教务系统，优先使用缓存的session

        Returns:
            登录是否成功
        """
        if self._is_logged_in:
            logger.info("已有有效登录会话，跳过登录")
            return True

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
                self._save_session()
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
            
            email_body = test_email_template(
                username=self.username,
                login_time=login_time,
                ip_info=ip_info_dict,
                device_info=device_info_dict,
                scores=scores,
            )

            subject = f"登录测试通知 - {self.username} - {login_time}"

            original_recipients = self.email_notifier.receiver_emails
            self.email_notifier.receiver_emails = [test_email]

            try:
                self.email_notifier.send(subject=subject, body=email_body, is_html=True)
                self.email_notifier.receiver_emails = original_recipients
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
                            "scores_count": len(scores) if scores else 0,
                        },
                    )
            except EmailSendError:
                self.email_notifier.receiver_emails = original_recipients
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
                            "login_time": login_time,
                        },
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
            self._is_logged_in = False
            return None

    @property
    def is_logged_in(self) -> bool:
        return self._is_logged_in

    def _save_session(self) -> None:
        """保存Session cookies到文件"""
        try:
            with open(self._session_path, 'wb') as f:
                pickle.dump(self.client.cookies, f)
            logger.debug("Session已保存")
        except Exception as e:
            logger.warning(f"保存Session失败: {e}")

    def _try_load_session(self) -> None:
        """尝试从文件加载Session cookies并验证"""
        if not self._session_path.exists():
            return
        try:
            with open(self._session_path, 'rb') as f:
                cookies = pickle.load(f)
            self.client.cookies = cookies
            self._is_logged_in = True
            logger.info("已加载缓存的登录会话")
        except Exception as e:
            logger.debug(f"加载Session失败（将重新登录）: {e}")
            if self._session_path.exists():
                self._session_path.unlink(missing_ok=True)
