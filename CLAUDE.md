# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 常用命令

```bash
# 持续监控（循环检查，间隔由 .env 中 CHECK_INTERVAL 控制，默认 300=5分钟）
python -m src.main

# 查询一次并打印结果
python -m src.main --once

# 同时发邮件报告
python -m src.main --once --email

# 交互式选择学期（配合 --once）
python -m src.main --once --semester

# 测试登录 → 发测试邮件
python -m src.main --test

# 交互式菜单（不用记命令，选数字即可）
python scripts/menu.py

# 诊断 SMTP 邮件发送
python scripts/test_smtp.py

# 如果 pip install 了本项目，也可以用短命令
gzhu-monitor              # = python -m src.main
gzhu-monitor --once       # = python -m src.main --once
gzhu-test-smtp            # = python scripts/test_smtp.py
```

## 架构

Python 3.9+ CLI，核心链路：登录教务系统 → 查成绩 JSON → 解析对比 → QQ 邮箱发 HTML 通知。

```
入口 src/main.py (ScoreMonitor 类 + argparse)
├── src/config.py        — .env → Config 对象
├── src/gzhu_login.py    — CAS 登录 (newcas.gzhu.edu.cn)，DES 加密，pickle 缓存 session
│   ├── 登录链路: CAS → 融合门户 → jwxt SSO → 教务系统
│   ├── 成绩查询: POST /jwglxt/cjcx/cjcx_cxDgXscj.html，queryModel.showCount 控制分页
│   ├── 学期推算: 根据学号第2-3位推算入学年份，生成可选学期列表
│   └── 登录成功自动发测试邮件（可关闭）
├── src/score_parser.py  — 教务 JSON → 课程详情列表，等级制"优"→95 分
│   ├── parse_course_scores()   — 课程名→成绩 映射
│   ├── parse_course_details()  — 完整课程信息（含学分、绩点、数值分）
│   └── calc_weighted_average() — 加权均分 & GPA
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

`.env` 可选：`CHECK_INTERVAL`, `HEARTBEAT_ENABLED`, `HEARTBEAT_INTERVAL`, `TEST_EMAIL`, `ENABLE_LOGIN_TEST_EMAIL`, `EMAIL_SUBJECT`

## 注意事项

- session 缓存于 `status/session.pkl`，有效期有限，过期会自动重新登录，查询返回非 JSON 时会自动重登
- 状态文件 `status/scores_{xnm}_{xqm}.json`（CI 模式 `--check` 按学期存储）
- 查询结果原始 JSON 保存于 `logs/last_score_response.json` 供排查
- 不要将 `.env`、`status/`、`logs/` 提交到 git
- `newcas.gzhu.edu.cn` 仅限中国大陆访问，海外服务器（境外 VPS）无法连接
- 学号格式假定第 2-3 位为入学年份（如 `32264400031` → 2022 年入学），学期列表据此推算

## ScoreMonitor 运行模式

| 方法 | 触发参数 | 行为 |
|------|----------|------|
| `run()` | (无参数) | 持续循环：查成绩 → 对比 → 有变化发邮件 → 心跳检查 → sleep |
| `run_once(xnm, xqm, send_email)` | `--once` | 查一次，终端打印成绩单（含加权均分、GPA）。`--email` 同时发邮件报告 |
| `run_test()` | `--test` | 仅登录，成功后发测试邮件 |

- `--semester` 会先调用 `_choose_semester_interactive()` 弹出方向键选择界面（非 TTY 环境回退为序号输入），选完学期后传给 `run_once`
- `SIGINT`/`SIGTERM` 信号会触发优雅退出

## 硬编码常量

`src/config.py` 中除 `.env` 可配置项外，还有三个硬编码常量，修改需改源码：

```python
REQUEST_TIMEOUT = 30   # HTTP 请求超时秒数
MAX_RETRY = 3          # 请求失败最大重试次数
RETRY_DELAY = 5        # 重试间隔秒数
```

## 登录链路细节

`gzhu_login.py` 的登录是复合链路：
1. GET `newcas.gzhu.edu.cn/cas/login` → 提取 `lt` 票据
2. DES 加密 `username + password + lt`（外调 JS `des.js`，用 `PyExecJS` 执行）
3. POST CAS 登录 → 成功后页面 title 应为 `融合门户`
4. GET `jwxt.gzhu.edu.cn/sso/driot4login` → SSO 跳转完成教务系统登录

session 加载优先用 pickle 缓存，加载后标记 `_is_logged_in=True`，**不验证有效性**。下次查询时如果返回非 JSON，才判定过期并重新登录。

**TLS 兼容**：教务系统服务器 SSL 配置老旧（不支持 TLS 1.3），Python 3.12+ 默认安全级别会拒绝握手。`_mount_tls_adapter()` 在 session 上挂载了一个降级适配器：`set_ciphers('DEFAULT:@SECLEVEL=1')` + 跳过证书验证。不要移除这个适配器。
