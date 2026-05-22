# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 常用命令

```bash
# 持续监控（循环检查，间隔由 .env 中 CHECK_INTERVAL 控制，建议 21600=6小时）
python -m src.main

# 查询一次并打印结果（不发邮件）
python -m src.main --once

# 测试登录 → 发测试邮件
python -m src.main --test

# CI 模式：查询一次，与上次对比，有变化发邮件
python -m src.main --check

# 主动查询，必定发邮件
python -m src.main --query

# 诊断 SMTP 邮件发送
python scripts/test_smtp.py
```

## 架构

Python 3.9+ CLI，核心链路：登录教务系统 → 查成绩 JSON → 解析对比 → QQ 邮箱发 HTML 通知。

```
入口 src/main.py (ScoreMonitor 类 + argparse)
├── src/config.py        — .env → Config 对象
├── src/gzhu_login.py    — CAS 登录 (newcas.gzhu.edu.cn)，DES 加密，pickle 缓存 session
│   ├── 登录链路: CAS → 融合门户 → jwxt SSO → 教务系统
│   ├── 成绩查询: /jwglxt/cjcx/cjcx_cxDgXscj.html?doType=query
│   └── 登录成功自动发测试邮件（可关闭）
├── src/score_parser.py  — 教务 JSON → {课程名: 成绩} dict
├── src/email_notifier.py — QQ SMTP(465 SSL) → HTML 邮件
│   └── create_notifier() 工厂函数，读取 config 构建 EmailNotifier
├── src/templates.py     — 邮件 HTML 模板:
│   ├── test_email()     — 登录测试通知
│   ├── score_update()   — 成绩更新对比（新增 + 更新）
│   ├── heartbeat()      — 心跳确认程序正常
│   └── query_scores()   — 主动查询全部成绩
└── src/logger.py        — logging 配置（DEBUG→文件, INFO→控制台）
```

## 配置

`.env` 必填项：`GZHU_USERNAME`, `GZHU_PASSWORD`, `QQ_EMAIL`, `QQ_AUTH_CODE`, `RECEIVER_EMAILS`

`.env` 可选：`CHECK_INTERVAL`, `HEARTBEAT_ENABLED`, `HEARTBEAT_INTERVAL`

## 注意事项

- session 缓存于 `status/session.pkl`，有效期有限，过期会自动重新登录
- 状态文件 `status/scores.json`（CI 模式 `--check` 对比用）
- 不要将 `.env`、`status/`、`logs/` 提交到 git
