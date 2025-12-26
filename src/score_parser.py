"""
成绩解析模块
"""
import json
import logging
from typing import Dict, Optional
from src.logger import logger


class ScoreParseError(Exception):
    pass


def parse_course_scores(json_data: str) -> Dict[str, str]:
    """
    从JSON数据中提取课程名称和对应的成绩
    
    Args:
        json_data: 成绩JSON字符串
        
    Returns:
        课程名称到成绩的映射字典
        
    Raises:
        ScoreParseError: JSON解析失败时抛出
    """
    try:
        data = json.loads(json_data)
        scores = {}
        
        for item in data.get('items', []):
            course_name = item.get('kcmc')
            score = item.get('cj')
            
            if course_name and score:
                scores[course_name] = score
        
        logger.debug(f"解析到{len(scores)}门课程成绩")
        return scores
        
    except json.JSONDecodeError as e:
        logger.error(f"JSON解析错误: {e}")
        raise ScoreParseError(f"JSON解析失败: {e}")
    except Exception as e:
        logger.error(f"解析成绩数据时发生错误: {e}")
        raise ScoreParseError(f"解析失败: {e}")


def format_scores(scores: Dict[str, str]) -> str:
    """
    格式化成绩信息为可读文本
    
    Args:
        scores: 课程成绩字典
        
    Returns:
        格式化后的成绩文本
    """
    if not scores:
        return "暂无成绩数据"
    
    lines = ["检测到新成绩发布：", ""]
    for course, score in scores.items():
        lines.append(f"  {course}: {score}")
    
    return "\n".join(lines)
