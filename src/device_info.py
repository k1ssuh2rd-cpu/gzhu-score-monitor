"""
设备信息解析模块
"""
import platform
import re
from typing import Dict, Optional
from src.logger import logger


class DeviceInfo:
    """设备信息类"""
    
    def __init__(self, user_agent: str = None):
        """
        初始化设备信息
        
        Args:
            user_agent: 用户代理字符串
        """
        self.user_agent = user_agent or self._get_default_user_agent()
        self._device_info = self._parse_device_info()
    
    def _get_default_user_agent(self) -> str:
        """
        获取默认用户代理字符串
        
        Returns:
            默认用户代理字符串
        """
        system = platform.system()
        version = platform.version()
        machine = platform.machine()
        
        if system == "Windows":
            return f"Mozilla/5.0 (Windows NT {version}; {machine}) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        elif system == "Darwin":
            return f"Mozilla/5.0 (Macintosh; Intel Mac OS X {version}) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        elif system == "Linux":
            return f"Mozilla/5.0 (X11; Linux {machine}) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        else:
            return "Mozilla/5.0 (Unknown) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    
    def _parse_device_info(self) -> Dict[str, str]:
        """
        解析设备信息
        
        Returns:
            设备信息字典
        """
        info = {
            "device_type": self._get_device_type(),
            "os_name": platform.system(),
            "os_version": self._get_os_version(),
            "os_architecture": platform.machine(),
            "browser_name": self._get_browser_name(),
            "browser_version": self._get_browser_version(),
            "python_version": platform.python_version(),
        }
        return info
    
    def _get_device_type(self) -> str:
        """
        获取设备类型
        
        Returns:
            设备类型（PC/Mobile/Tablet/Unknown）
        """
        if not self.user_agent:
            return "Unknown"
        
        user_agent_lower = self.user_agent.lower()
        
        if "mobile" in user_agent_lower or "android" in user_agent_lower:
            return "Mobile"
        elif "tablet" in user_agent_lower or "ipad" in user_agent_lower:
            return "Tablet"
        elif "windows" in user_agent_lower or "macintosh" in user_agent_lower or "linux" in user_agent_lower:
            return "PC"
        else:
            return "Unknown"
    
    def _get_os_version(self) -> str:
        """
        获取操作系统版本
        
        Returns:
            操作系统版本字符串
        """
        system = platform.system()
        
        if system == "Windows":
            return platform.version()
        elif system == "Darwin":
            return platform.mac_ver()[0]
        elif system == "Linux":
            return platform.release()
        else:
            return "Unknown"
    
    def _get_browser_name(self) -> str:
        """
        获取浏览器名称
        
        Returns:
            浏览器名称
        """
        if not self.user_agent:
            return "Unknown"
        
        user_agent_lower = self.user_agent.lower()
        
        if "chrome" in user_agent_lower and "edg" not in user_agent_lower:
            return "Chrome"
        elif "firefox" in user_agent_lower:
            return "Firefox"
        elif "safari" in user_agent_lower and "chrome" not in user_agent_lower:
            return "Safari"
        elif "edg" in user_agent_lower:
            return "Edge"
        elif "opera" in user_agent_lower:
            return "Opera"
        else:
            return "Unknown"
    
    def _get_browser_version(self) -> str:
        """
        获取浏览器版本
        
        Returns:
            浏览器版本字符串
        """
        if not self.user_agent:
            return "Unknown"
        
        browser_name = self._get_browser_name()
        
        if browser_name == "Chrome":
            match = re.search(r'Chrome/(\d+\.\d+\.\d+\.\d+)', self.user_agent)
            if match:
                return match.group(1)
        elif browser_name == "Firefox":
            match = re.search(r'Firefox/(\d+\.\d+)', self.user_agent)
            if match:
                return match.group(1)
        elif browser_name == "Safari":
            match = re.search(r'Version/(\d+\.\d+)', self.user_agent)
            if match:
                return match.group(1)
        elif browser_name == "Edge":
            match = re.search(r'Edg/(\d+\.\d+\.\d+\.\d+)', self.user_agent)
            if match:
                return match.group(1)
        elif browser_name == "Opera":
            match = re.search(r'OPR/(\d+\.\d+\.\d+\.\d+)', self.user_agent)
            if match:
                return match.group(1)
        
        return "Unknown"
    
    def get_all_info(self) -> Dict[str, str]:
        """
        获取所有设备信息
        
        Returns:
            设备信息字典
        """
        return self._device_info.copy()
    
    def get_formatted_info(self) -> str:
        """
        获取格式化的设备信息字符串
        
        Returns:
            格式化的设备信息字符串
        """
        info = self._device_info
        return (
            f"设备类型: {info['device_type']}\n"
            f"操作系统: {info['os_name']} {info['os_version']}\n"
            f"系统架构: {info['os_architecture']}\n"
            f"浏览器: {info['browser_name']} {info['browser_version']}\n"
            f"Python版本: {info['python_version']}"
        )
