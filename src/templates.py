"""
邮件 HTML 模板模块
"""
from typing import Dict


def test_email(
    username: str,
    login_time: str,
    ip_info: dict,
    scores: dict = None,
) -> str:
    """生成登录测试邮件（HTML）"""
    if scores is None:
        scores_html = """            <div class="card">
                <div class="card-title">当前成绩</div>
                <div class="empty-state">成绩查询失败，请检查日志</div>
            </div>
"""
    elif not scores:
        scores_html = """            <div class="card">
                <div class="card-title">当前成绩</div>
                <div class="empty-state">暂无已发布的成绩</div>
            </div>
"""
    else:
        rows = ""
        for course, score in scores.items():
            rows += f"""                        <tr>
                            <td class="course-cell">{course}</td>
                            <td class="score-cell">{score}</td>
                        </tr>
"""
        scores_html = f"""            <div class="card">
                <div class="card-title">当前成绩 · {len(scores)} 门</div>
                <table class="score-table">
                    <thead>
                        <tr>
                            <th>课程名称</th>
                            <th>成绩</th>
                        </tr>
                    </thead>
                    <tbody>
{rows}                    </tbody>
                </table>
            </div>
"""

    return f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, "PingFang SC", "Microsoft YaHei", sans-serif;
            line-height: 1.6;
            color: #2c3e50;
            max-width: 560px;
            margin: 0 auto;
            padding: 24px;
            background-color: #f0f2f5;
        }}
        .header {{
            background: linear-gradient(160deg, #10b981 0%, #059669 100%);
            color: #fff;
            padding: 32px 24px 28px;
            text-align: center;
            border-radius: 12px 12px 0 0;
        }}
        .header-icon {{
            font-size: 36px;
            margin-bottom: 8px;
            display: block;
        }}
        .header h2 {{
            margin: 0;
            font-size: 22px;
            font-weight: 700;
            letter-spacing: 0.3px;
        }}
        .header p {{
            margin: 6px 0 0 0;
            opacity: 0.85;
            font-size: 13px;
        }}
        .content {{
            background: #fff;
            padding: 24px 24px 16px;
            border: 1px solid #e5e7eb;
            border-top: none;
            border-radius: 0 0 12px 12px;
        }}
        .card {{
            background: #f9fafb;
            border: 1px solid #e5e7eb;
            border-radius: 8px;
            padding: 18px 20px;
            margin-bottom: 16px;
        }}
        .card-title {{
            font-weight: 600;
            font-size: 15px;
            color: #059669;
            margin-bottom: 12px;
            padding-bottom: 10px;
            border-bottom: 1px solid #e5e7eb;
        }}
        .card-row {{
            display: flex;
            padding: 6px 0;
            font-size: 14px;
        }}
        .card-row + .card-row {{
            border-top: none;
        }}
        .card-label {{
            color: #6b7280;
            width: 90px;
            flex-shrink: 0;
        }}
        .card-value {{
            color: #1f2937;
            font-weight: 500;
        }}
        .empty-state {{
            text-align: center;
            color: #9ca3af;
            font-size: 14px;
            padding: 16px 0;
        }}
        .score-table {{
            width: 100%;
            border-collapse: collapse;
            font-size: 14px;
        }}
        .score-table th {{
            background: #ecfdf5;
            color: #059669;
            padding: 10px 14px;
            text-align: left;
            font-weight: 600;
            font-size: 12px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            border-bottom: 2px solid #a7f3d0;
        }}
        .score-table th:last-child {{
            text-align: right;
            width: 80px;
        }}
        .course-cell {{
            padding: 11px 14px;
            border-bottom: 1px solid #f3f4f6;
            font-weight: 500;
        }}
        .score-cell {{
            padding: 11px 14px;
            border-bottom: 1px solid #f3f4f6;
            text-align: right;
            font-weight: 700;
            color: #059669;
            font-size: 15px;
        }}
        .note {{
            background: #fffbeb;
            border: 1px solid #fde68a;
            border-radius: 6px;
            padding: 12px 16px;
            margin-top: 4px;
            margin-bottom: 8px;
            font-size: 13px;
            color: #92400e;
            line-height: 1.5;
        }}
        .note strong {{
            font-weight: 600;
        }}
        .footer {{
            text-align: center;
            color: #9ca3af;
            font-size: 11px;
            padding: 16px 0 0;
            margin-top: 8px;
            border-top: 1px solid #f3f4f6;
            line-height: 1.8;
        }}
    </style>
</head>
<body>
    <div class="header">
        <span class="header-icon">&#x1F393;</span>
        <h2>登录测试通知</h2>
        <p>广州大学成绩监测系统</p>
    </div>
    <div class="content">
        <div class="card">
            <div class="card-title">登录信息</div>
            <div class="card-row">
                <span class="card-label">登录时间</span>
                <span class="card-value">{login_time}</span>
            </div>
            <div class="card-row">
                <span class="card-label">登录账号</span>
                <span class="card-value">{username}</span>
            </div>
            <div class="card-row">
                <span class="card-label">登录 IP</span>
                <span class="card-value">{ip_info.get('public_ip', '—')}</span>
            </div>
        </div>

{scores_html}
        <div class="note">
            <strong>&#x26A0;</strong> 这是一封自动发送的测试邮件，用于验证邮件通知功能是否正常工作。
        </div>

        <div class="footer">
            <div>成绩监测系统自动发送 · 请勿回复</div>
            <div>{login_time}</div>
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
