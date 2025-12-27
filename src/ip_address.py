"""
IP地址获取模块
"""
import socket
import requests
from typing import Optional, Dict
from src.config import config
from src.logger import logger


class IPAddressError(Exception):
    pass


class IPAddress:
    """IP地址获取类"""
    
    def __init__(self):
        self._ip_info = {}
    
    def get_local_ip(self) -> Optional[str]:
        """
        获取本地IP地址
        
        Returns:
            本地IP地址，失败返回None
        """
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.settimeout(5)
            s.connect(("8.8.8.8", 80))
            local_ip = s.getsockname()[0]
            s.close()
            return local_ip
        except Exception as e:
            logger.warning(f"获取本地IP失败: {e}")
            return None
    
    def get_public_ip(self) -> Optional[str]:
        """
        获取公网IP地址
        
        Returns:
            公网IP地址，失败返回None
        """
        try:
            response = requests.get(
                'https://api.ipify.org?format=json',
                timeout=config.REQUEST_TIMEOUT
            )
            if response.status_code == 200:
                return response.json().get('ip')
        except Exception as e:
            logger.warning(f"获取公网IP失败: {e}")
        
        return None
    
    def get_ip_info(self) -> Dict[str, Optional[str]]:
        """
        获取完整的IP信息
        
        Returns:
            IP信息字典
        """
        self._ip_info = {
            "local_ip": self.get_local_ip(),
            "public_ip": self.get_public_ip()
        }
        return self._ip_info.copy()
    
    def get_formatted_info(self) -> str:
        """
        获取格式化的IP信息字符串
        
        Returns:
            格式化的IP信息字符串
        """
        info = self.get_ip_info()
        return (
            f"本地IP: {info['local_ip'] or '未知'}\n"
            f"公网IP: {info['public_ip'] or '未知'}"
        )
