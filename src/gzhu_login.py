"""
广州大学教务系统登录模块
"""
import json
import logging
import re
import time
from typing import Optional
import requests
import execjs
from lxml import html
from src.config import config
from src.logger import logger


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
    
    def __init__(self, username: str, password: str):
        self.username = username
        self.password = password
        self.client = requests.Session()
        self._is_logged_in = False
    
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
                return True
            else:
                logger.error("登录失败，可能用户名或密码错误")
                return False
                
        except Exception as e:
            logger.error(f"登录过程发生错误: {e}")
            return False
    
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
