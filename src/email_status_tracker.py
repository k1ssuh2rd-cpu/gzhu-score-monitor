"""
邮件发送状态跟踪模块
"""
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
from threading import Lock
from src.config import config
from src.logger import logger


class EmailStatusTracker:
    """邮件发送状态跟踪类"""
    
    def __init__(self, status_file: Path = None):
        """
        初始化邮件状态跟踪器
        
        Args:
            status_file: 状态文件路径
        """
        if status_file is None:
            status_file = config.LOG_DIR / "email_status.json"
        
        self.status_file = status_file
        self.status_file.parent.mkdir(parents=True, exist_ok=True)
        self._lock = Lock()
        self._ensure_file_exists()
    
    def _ensure_file_exists(self) -> None:
        """
        确保状态文件存在
        """
        if not self.status_file.exists():
            self._write_data([])
    
    def _read_data(self) -> List[Dict]:
        """
        读取状态数据
        
        Returns:
            状态数据列表
        """
        try:
            with open(self.status_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"读取邮件状态文件失败: {e}")
            return []
    
    def _write_data(self, data: List[Dict]) -> None:
        """
        写入状态数据
        
        Args:
            data: 状态数据列表
        """
        try:
            with open(self.status_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"写入邮件状态文件失败: {e}")
    
    def add_status(
        self,
        email_type: str,
        subject: str,
        recipients: List[str],
        status: str,
        error_message: Optional[str] = None,
        additional_info: Optional[Dict] = None
    ) -> None:
        """
        添加邮件发送状态
        
        Args:
            email_type: 邮件类型（test/score）
            subject: 邮件主题
            recipients: 收件人列表
            status: 状态（success/failed）
            error_message: 错误信息（失败时）
            additional_info: 附加信息
        """
        with self._lock:
            try:
                data = self._read_data()
                
                status_record = {
                    "id": len(data) + 1,
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "email_type": email_type,
                    "subject": subject,
                    "recipients": recipients,
                    "status": status,
                    "error_message": error_message,
                    "additional_info": additional_info or {}
                }
                
                data.append(status_record)
                self._write_data(data)
                
                logger.info(f"邮件状态已记录: {status_record['id']} - {status}")
                
            except Exception as e:
                logger.error(f"添加邮件状态失败: {e}")
    
    def get_all_status(self) -> List[Dict]:
        """
        获取所有邮件状态
        
        Returns:
            状态数据列表
        """
        with self._lock:
            return self._read_data()
    
    def get_recent_status(self, limit: int = 10) -> List[Dict]:
        """
        获取最近的邮件状态
        
        Args:
            limit: 返回数量限制
            
        Returns:
            状态数据列表
        """
        with self._lock:
            data = self._read_data()
            return data[-limit:] if data else []
    
    def get_status_by_type(self, email_type: str) -> List[Dict]:
        """
        根据邮件类型获取状态
        
        Args:
            email_type: 邮件类型（test/score）
            
        Returns:
            状态数据列表
        """
        with self._lock:
            data = self._read_data()
            return [item for item in data if item.get('email_type') == email_type]
    
    def get_status_by_id(self, status_id: int) -> Optional[Dict]:
        """
        根据ID获取状态
        
        Args:
            status_id: 状态ID
            
        Returns:
            状态数据，不存在返回None
        """
        with self._lock:
            data = self._read_data()
            for item in data:
                if item.get('id') == status_id:
                    return item
            return None
    
    def clear_old_status(self, days: int = 30) -> int:
        """
        清除旧的状态记录
        
        Args:
            days: 保留天数
            
        Returns:
            清除的记录数
        """
        with self._lock:
            try:
                data = self._read_data()
                from datetime import timedelta
                
                cutoff_date = datetime.now() - timedelta(days=days)
                cutoff_str = cutoff_date.strftime("%Y-%m-%d %H:%M:%S")
                
                new_data = [
                    item for item in data
                    if item.get('timestamp', '') >= cutoff_str
                ]
                
                removed_count = len(data) - len(new_data)
                self._write_data(new_data)
                
                logger.info(f"清除了 {removed_count} 条旧状态记录")
                return removed_count
                
            except Exception as e:
                logger.error(f"清除旧状态记录失败: {e}")
                return 0
    
    def get_statistics(self) -> Dict:
        """
        获取邮件发送统计信息
        
        Returns:
            统计信息字典
        """
        with self._lock:
            data = self._read_data()
            
            total = len(data)
            success = sum(1 for item in data if item.get('status') == 'success')
            failed = sum(1 for item in data if item.get('status') == 'failed')
            
            test_emails = sum(1 for item in data if item.get('email_type') == 'test')
            score_emails = sum(1 for item in data if item.get('email_type') == 'score')
            
            return {
                "total": total,
                "success": success,
                "failed": failed,
                "success_rate": f"{(success / total * 100):.2f}%" if total > 0 else "0%",
                "test_emails": test_emails,
                "score_emails": score_emails
            }
