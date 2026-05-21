"""
邮件 HTML 模板模块
"""
from typing import Dict


def test_email(
    username: str,
    login_time: str,
    ip_info: dict,
    device_info: dict,
    scores: dict = None,
) -> str:
    """生成登录测试邮件（HTML）"""
    scores_html = ""
    if scores:
        rows = ""
        for course, score in scores.items():
            rows += f"""                    <tr>
                        <td style="padding: 12px; border-bottom: 1px solid #e0e0e0;">{course}</td>
                        <td style="padding: 12px; border-bottom: 1px solid #e0e0e0; text-align: center; font-weight: bold; color: #4CAF50;">{score}</td>
                    </tr>
"""
        scores_html = f"""                <div class="info-section">
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
{rows}                            </tbody>
                        </table>
                    </div>
                    <div style="margin-top: 10px; color: #666; font-size: 14px;">
                        共 <strong>{len(scores)}</strong> 门课程成绩
                    </div>
                </div>
"""

    return f"""<!DOCTYPE html>
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
        .header h2 {{ margin: 0; font-size: 24px; font-weight: 600; }}
        .header p {{ margin: 10px 0 0 0; opacity: 0.9; font-size: 14px; }}
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
            content: "\\25b6";
            margin-right: 8px;
            font-size: 12px;
        }}
        .info-item {{
            margin: 10px 0;
            padding: 8px 0;
            border-bottom: 1px solid #e8e8e8;
        }}
        .info-item:last-child {{ border-bottom: none; }}
        .info-label {{
            font-weight: 600;
            color: #555;
            display: inline-block;
            width: 120px;
        }}
        .info-value {{ color: #333; }}
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
        table {{ font-size: 14px; }}
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
                <span class="info-value">{username}</span>
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
</html>"""


def score_update(
    new_scores: Dict[str, str],
    old_scores: Dict[str, str],
    current_time: str,
) -> str:
    """生成成绩更新通知邮件（HTML）"""
    new_courses = set(new_scores.keys()) - set(old_scores.keys())
    updated_courses = [
        c for c in old_scores
        if c in new_scores and new_scores[c] != old_scores[c]
    ]

    new_courses_html = ""
    if new_courses:
        rows = ""
        for course in new_courses:
            rows += f"""                    <tr>
                        <td style="padding: 12px; border-bottom: 1px solid #e0e0e0;">{course}</td>
                        <td style="padding: 12px; border-bottom: 1px solid #e0e0e0; text-align: center; font-weight: bold; color: #4CAF50;">{new_scores[course]}</td>
                    </tr>
"""
        new_courses_html = f"""                <div class="info-section">
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
{rows}                            </tbody>
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
            old = old_scores[course]
            new = new_scores[course]
            try:
                is_up = float(new) > float(old)
            except ValueError:
                is_up = new > old
            arrow = "↑" if is_up else "↓"
            color = "#4CAF50" if is_up else "#f44336"
            rows += f"""                    <tr>
                        <td style="padding: 12px; border-bottom: 1px solid #e0e0e0;">{course}</td>
                        <td style="padding: 12px; border-bottom: 1px solid #e0e0e0; text-align: center;">{old}</td>
                        <td style="padding: 12px; border-bottom: 1px solid #e0e0e0; text-align: center; font-weight: bold; color: {color};">{new} {arrow}</td>
                    </tr>
"""
        updated_courses_html = f"""                <div class="info-section">
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
{rows}                            </tbody>
                        </table>
                    </div>
                    <div style="margin-top: 10px; color: #666; font-size: 14px;">
                        共 <strong>{len(updated_courses)}</strong> 门课程成绩更新
                    </div>
                </div>
"""

    return f"""<!DOCTYPE html>
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
        .header h2 {{ margin: 0; font-size: 24px; font-weight: 600; }}
        .header p {{ margin: 10px 0 0 0; opacity: 0.9; font-size: 14px; }}
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
            content: "\\25b6";
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
        .summary-item strong {{ color: #1976D2; }}
        .footer {{
            margin-top: 30px;
            text-align: center;
            color: #999;
            font-size: 12px;
            padding-top: 20px;
            border-top: 1px solid #e0e0e0;
        }}
        table {{ font-size: 14px; }}
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
</html>"""


def heartbeat(
    current_time: str,
    uptime: str,
    course_count: int,
) -> str:
    """生成心跳邮件（HTML）"""
    return f"""<!DOCTYPE html>
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
        .header h2 {{ margin: 0; font-size: 24px; font-weight: 600; }}
        .header p {{ margin: 10px 0 0 0; opacity: 0.9; font-size: 14px; }}
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
        .status-item strong {{ color: #2e7d32; }}
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
            <div class="status-item"><strong>📚 当前监测课程数:</strong> {course_count} 门</div>
        </div>
        <div class="footer">
            <p>此邮件由成绩监测系统自动发送，用于确认程序正常运行。</p>
            <p>发送时间: {current_time}</p>
        </div>
    </div>
</body>
</html>"""
