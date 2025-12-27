"""
管理后台API模块
提供邮件发送状态的实时查看功能
"""
import json
from datetime import datetime
from typing import Dict, List, Optional
from pathlib import Path
from src.email_status_tracker import EmailStatusTracker
from src.logger import logger


class AdminAPI:
    """管理后台API类"""
    
    def __init__(self, status_tracker: EmailStatusTracker):
        """
        初始化管理后台API
        
        Args:
            status_tracker: 邮件状态跟踪器
        """
        self.status_tracker = status_tracker
    
    def get_all_status(self) -> Dict:
        """
        获取所有邮件状态
        
        Returns:
            包含所有状态的字典
        """
        try:
            status_list = self.status_tracker.get_all_status()
            return {
                "success": True,
                "data": status_list,
                "count": len(status_list),
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
        except Exception as e:
            logger.error(f"获取所有状态失败: {e}")
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
    
    def get_recent_status(self, limit: int = 10) -> Dict:
        """
        获取最近的邮件状态
        
        Args:
            limit: 返回数量限制
            
        Returns:
            包含最近状态的字典
        """
        try:
            status_list = self.status_tracker.get_recent_status(limit)
            return {
                "success": True,
                "data": status_list,
                "count": len(status_list),
                "limit": limit,
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
        except Exception as e:
            logger.error(f"获取最近状态失败: {e}")
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
    
    def get_status_by_type(self, email_type: str) -> Dict:
        """
        根据邮件类型获取状态
        
        Args:
            email_type: 邮件类型（test/score）
            
        Returns:
            包含指定类型状态的字典
        """
        try:
            status_list = self.status_tracker.get_status_by_type(email_type)
            return {
                "success": True,
                "data": status_list,
                "count": len(status_list),
                "email_type": email_type,
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
        except Exception as e:
            logger.error(f"获取类型状态失败: {e}")
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
    
    def get_status_by_id(self, status_id: int) -> Dict:
        """
        根据ID获取状态
        
        Args:
            status_id: 状态ID
            
        Returns:
            包含指定ID状态的字典
        """
        try:
            status = self.status_tracker.get_status_by_id(status_id)
            if status:
                return {
                    "success": True,
                    "data": status,
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }
            else:
                return {
                    "success": False,
                    "error": f"未找到ID为 {status_id} 的状态记录",
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }
        except Exception as e:
            logger.error(f"获取ID状态失败: {e}")
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
    
    def get_statistics(self) -> Dict:
        """
        获取邮件发送统计信息
        
        Returns:
            包含统计信息的字典
        """
        try:
            stats = self.status_tracker.get_statistics()
            return {
                "success": True,
                "data": stats,
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
        except Exception as e:
            logger.error(f"获取统计信息失败: {e}")
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
    
    def clear_old_status(self, days: int = 30) -> Dict:
        """
        清除旧的状态记录
        
        Args:
            days: 保留天数
            
        Returns:
            包含清除结果的字典
        """
        try:
            removed_count = self.status_tracker.clear_old_status(days)
            return {
                "success": True,
                "data": {
                    "removed_count": removed_count,
                    "retention_days": days
                },
                "message": f"成功清除 {removed_count} 条旧记录",
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
        except Exception as e:
            logger.error(f"清除旧记录失败: {e}")
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
    
    def export_status_to_json(self, output_file: str = None) -> Dict:
        """
        导出邮件状态到JSON文件
        
        Args:
            output_file: 输出文件路径，默认为 logs/email_status_export.json
            
        Returns:
            包含导出结果的字典
        """
        try:
            if output_file is None:
                output_file = "logs/email_status_export.json"
            
            status_list = self.status_tracker.get_all_status()
            
            output_path = Path(output_file)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(status_list, f, ensure_ascii=False, indent=2)
            
            return {
                "success": True,
                "data": {
                    "output_file": str(output_path.absolute()),
                    "exported_count": len(status_list)
                },
                "message": f"成功导出 {len(status_list)} 条记录到 {output_file}",
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
        except Exception as e:
            logger.error(f"导出状态失败: {e}")
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
    
    def get_dashboard_data(self) -> Dict:
        """
        获取仪表板数据（综合信息）
        
        Returns:
            包含仪表板数据的字典
        """
        try:
            recent_status = self.status_tracker.get_recent_status(5)
            statistics = self.status_tracker.get_statistics()
            
            return {
                "success": True,
                "data": {
                    "recent_status": recent_status,
                    "statistics": statistics
                },
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
        except Exception as e:
            logger.error(f"获取仪表板数据失败: {e}")
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }


def create_admin_api(status_tracker: EmailStatusTracker) -> AdminAPI:
    """
    创建管理后台API实例
    
    Args:
        status_tracker: 邮件状态跟踪器
        
    Returns:
        AdminAPI实例
    """
    return AdminAPI(status_tracker)
