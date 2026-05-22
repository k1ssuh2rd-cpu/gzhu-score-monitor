"""
成绩解析模块
"""
import json
from typing import Dict, List
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


def _to_numeric(score_str: str) -> float:
    """将成绩字符串转为数值。仅处理'优'→95，其余原样转换"""
    if score_str in ("优", "优秀"):
        return 95.0
    return float(score_str)


def parse_course_details(json_data: str) -> List[dict]:
    """
    从JSON数据中提取课程的完整信息（含学分）

    Returns:
        课程信息列表，每项包含 name/cj/score/xf/jd 等字段
        cj 为原始成绩，score 为转换后的数值分
    """
    data = json.loads(json_data)
    courses = []
    for item in data.get('items', []):
        name = item.get('kcmc')
        score_str = item.get('cj')
        if not name:
            continue
        if not score_str:
            logger.warning(f"课程 '{name}' 暂无成绩数据，已跳过")
            continue
        try:
            xf = float(item.get('xf', 0))
        except (ValueError, TypeError):
            xf = 0.0
        try:
            jd = float(item.get('jd', 0))
        except (ValueError, TypeError):
            jd = 0.0
        try:
            score = _to_numeric(score_str)
        except (ValueError, TypeError):
            score = 0.0
        courses.append({
            'name': name,
            'cj': score_str,
            'score': score,
            'xf': xf,
            'jd': jd,
        })
    return courses


def calc_weighted_average(courses: List[dict]) -> dict:
    """
    计算加权均分和绩点

    Returns:
        {'avg_score': 加权均分, 'gpa': 平均绩点, 'total_xf': 总学分}
    """
    total_xf = sum(c['xf'] for c in courses)
    if total_xf == 0:
        return {'avg_score': None, 'gpa': None, 'total_xf': 0.0}

    weighted_sum = 0.0
    jd_sum = 0.0
    for c in courses:
        score = c.get('score', 0)
        if score == 0:
            continue
        weighted_sum += score * c['xf']
        jd_sum += c['jd'] * c['xf']

    return {
        'avg_score': round(weighted_sum / total_xf, 2),
        'gpa': round(jd_sum / total_xf, 2),
        'total_xf': total_xf,
    }


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
