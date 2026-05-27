# Gzhu Score Monitor · 广州大学成绩监测

[![Python](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Version](https://img.shields.io/badge/version-1.1.0-blue)](https://github.com/K1ssuh2rd/gzhu-score-monitor)

**Automatically checks Guangzhou University's academic system for new grades and notifies you via QQ email — so you never have to manually refresh again.**

**自动登录广州大学教务系统，成绩有更新立即通过 QQ 邮箱通知你，不用再隔三差五手动查成绩。**

---

## 目录 / Table of Contents

- [Install · 安装](#install--安装)
- [Quick Start · 快速开始](#quick-start--快速开始)
- [Usage · 使用方式](#usage--使用方式)
- [Configuration · 配置说明](#configuration--配置说明)
- [Project Structure · 项目结构](#project-structure--项目结构)
- [FAQ · 常见问题](#faq--常见问题)
- [Contributing · 贡献指南](#contributing--贡献指南)
- [Credits · 致谢](#credits--致谢)
- [License · 许可证](#license--许可证)

---

## Install · 安装

```bash
# 1. Clone
git clone https://github.com/K1ssuh2rd/gzhu-score-monitor.git
cd gzhu-score-monitor

# 2. (Optional) Create virtual environment
python -m venv .venv && source .venv/bin/activate  # macOS/Linux
python -m venv .venv && .venv\Scripts\activate     # Windows

# 3. Install dependencies
pip install -r requirements.txt

# 4. Setup config
cp .env.example .env
# Then edit .env with your credentials (see Configuration section)

# 5. Test it!
python -m src.main --test
```

> Requires Python 3.9+. Don't have it? Download from [python.org](https://www.python.org/downloads/). Check the box **"Add Python to PATH"** during installation.

---

## Quick Start · 快速开始

| 你想做什么？ | 命令 |
|------------|------|
| 后台持续监测，成绩变化自动通知 | `python -m src.main` |
| 查一次，终端打印成绩单 | `python -m src.main --once` |
| 查一次，同时发邮件 | `python -m src.main --once --email` |
| 选一个学期查 | `python -m src.main --once --semester` |
| 测试邮件配置是否正常 | `python -m src.main --test` |
| 不想记命令，用菜单 | `python scripts/menu.py` |

---

## Usage · 使用方式

### 持续监测（推荐）

```bash
python -m src.main
```

程序每 5 分钟自动登录教务系统检查一次。如果检测到新成绩或成绩变动，立即发送邮件通知。同时每 24 小时发一次心跳邮件，确认程序还在正常运行。

按 `Ctrl + C` 停止。

### 单次查询

```bash
# 查本学期全部成绩，终端打印（含加权均分、绩点）
python -m src.main --once

# 同上，同时把成绩单发邮件到邮箱
python -m src.main --once --email

# 交互式选择学期（方向键 ↑↓ 移动，回车确认）
python -m src.main --once --semester
python -m src.main --once --semester --email
```

输出示例：

```
  2023-2024 学年 第一学期  成绩单
  --------------------------------------------------
  高等数学A
    成绩     90    绩点 3.7    学分 4.0
  大学英语1
    成绩     85    绩点 3.3    学分 3.0
  --------------------------------------------------
  2 门    总学分 7.0    加权均分 87.86    平均绩点 3.53
```

### 测试与诊断

```bash
python -m src.main --test           # 登录 + 发送测试邮件
python scripts/test_smtp.py         # 逐步诊断 SMTP 连接问题
python scripts/menu.py              # 交互式菜单
```

### pip install（可选）

```bash
pip install .                       # 安装到系统
gzhu-monitor                        # = python -m src.main
gzhu-monitor --once --semester      # 支持所有参数
gzhu-test-smtp                      # = python scripts/test_smtp.py
```

---

## Configuration · 配置说明

`.env` 文件所有可配置项：

| 变量 | 必填 | 默认值 | 说明 |
|------|:---:|--------|------|
| `GZHU_USERNAME` | ✓ | - | 学号 |
| `GZHU_PASSWORD` | ✓ | - | 教务系统密码 |
| `QQ_EMAIL` | ✓ | - | 发通知的 QQ 邮箱地址 |
| `QQ_AUTH_CODE` | ✓ | - | QQ 邮箱 SMTP 授权码（非 QQ 密码！） |
| `RECEIVER_EMAILS` | ✓ | - | 接收通知的邮箱，多个用英文逗号分隔 |
| `TEST_EMAIL` | | 同 `RECEIVER_EMAILS` | 测试邮件收件地址 |
| `CHECK_INTERVAL` | | `300` | 检查间隔（秒），默认 5 分钟 |
| `EMAIL_SUBJECT` | | `新成绩通知` | 通知邮件标题 |
| `ENABLE_LOGIN_TEST_EMAIL` | | `true` | 登录后是否自动发测试邮件 |
| `HEARTBEAT_ENABLED` | | `true` | 是否发送心跳邮件 |
| `HEARTBEAT_INTERVAL` | | `86400` | 心跳间隔（秒），默认 24 小时 |

### Getting QQ Email Auth Code · 获取 QQ 邮箱授权码

1. 访问 [mail.qq.com](https://mail.qq.com/)，登录你的 QQ 邮箱
2. 进入 **设置 → 账户**
3. 找到 **"POP3/IMAP/SMTP/Exchange/CardDAV/CalDAV服务"** 区域
4. 开启 **SMTP 服务**，按提示发送短信验证
5. 短信验证通过后会弹出一串字母授权码，**立即复制保存**
6. 将这串授权码填入 `.env` 的 `QQ_AUTH_CODE` 字段

> ⚠️ 授权码**只显示一次**，关了弹窗就找不到了，只能重新获取。

---

## Project Structure · 项目结构

```
gzhu-score-monitor/
├── pyproject.toml              # 项目元数据 & pip install 入口
├── requirements.txt            # Python 依赖
├── .env.example                # 配置文件模板
├── scripts/
│   ├── menu.py                 # 交互式菜单
│   └── test_smtp.py            # SMTP 连通性诊断工具
├── src/
│   ├── main.py                 # 入口：argparse CLI + ScoreMonitor
│   ├── gzhu_login.py           # CAS 登录、session 缓存、成绩查询
│   ├── score_parser.py         # JSON 解析、加权均分 & GPA 计算
│   ├── email_notifier.py       # QQ SMTP(465 SSL) 邮件发送
│   ├── templates.py            # 邮件 HTML 模板（测试/更新/心跳/查询）
│   ├── config.py               # .env 配置加载
│   └── logger.py               # 双通道日志（DEBUG→文件, INFO→控制台）
├── logs/                       # 运行日志（gitignore）
└── status/                     # session 缓存 & 成绩快照（gitignore）
```

### How It Works · 原理

```
定时唤醒 → CAS 登录 (DES 加密) → SSO 跳转至教务系统
    → POST 查询成绩 JSON → 解析 & 对比
    → 有变化? → QQ 邮箱 (SMTP 465 SSL) 发送 HTML 通知
    → 无变化? → 记录日志,等待下一轮
    → 定期心跳: 每 24h 确认程序存活
```

登录链路：`newcas.gzhu.edu.cn` → 融合门户 → `jwxt.gzhu.edu.cn` SSO → 教务系统

---

## FAQ · 常见问题

<details>
<summary><b>邮件发不出去？</b></summary>

1. 确认 QQ 邮箱 SMTP 服务已开启（设置 → 账户 → SMTP 状态为"已开启"）
2. `.env` 里的 `QQ_AUTH_CODE` 填的是**授权码**，不是 QQ 密码
3. 运行 `python scripts/test_smtp.py` 逐步排查
</details>

<details>
<summary><b>提示"登录失败"？</b></summary>

1. 检查 `.env` 中学号和密码是否正确（注意空格、大小写）
2. 在浏览器中手动登录教务系统确认账号正常
3. 查看 `logs/score_monitor.log` 获取详细错误信息
4. 确认你能访问 `newcas.gzhu.edu.cn`（该域名仅限中国大陆访问）
</details>

<details>
<summary><b>成绩更新了但没收到通知？</b></summary>

1. 检查间隔默认 5 分钟，稍微等一下
2. 查看邮箱**垃圾邮件**文件夹
3. 检查 `logs/score_monitor.log` 日志确认程序状态
</details>

<details>
<summary><b>怎么在后台静默运行？</b></summary>

```bash
# Windows：无窗口后台运行
pythonw -m src.main
# 停止：打开任务管理器，结束 python 进程

# macOS / Linux：
nohup python -m src.main &
```
</details>

<details>
<summary><b>怎么开机自启？</b></summary>

**Windows：** `Win + R` → `shell:startup` → 新建快捷方式，目标填 `python -m src.main`（静默用 `pythonw`）。

**macOS / Linux：** `crontab -e` 添加 `@reboot cd /path/to/project && python -m src.main`。
</details>

<details>
<summary><b>能调整检查频率吗？</b></summary>

在 `.env` 中修改 `CHECK_INTERVAL`（单位秒）：
- 1 分钟：`60`
- 10 分钟：`600`
- 1 小时：`3600`

频率太高可能被教务系统限流，建议不低于 300 秒。
</details>

<details>
<summary><b>Python 3.12+ 报 SSL 错误？</b></summary>

教务系统服务器 SSL 配置老旧（不支持 TLS 1.3），代码已内置 TLS 降级适配器（`set_ciphers('DEFAULT:@SECLEVEL=1')`）。如仍有问题请提交 Issue。
</details>

---

## Contributing · 贡献指南

欢迎提交 PR！贡献前请：

1. **Fork** 本项目
2. 创建特性分支：`git checkout -b feature/your-feature`
3. 保持代码风格一致（本项目不强制 formatter，但请遵循现有风格）
4. 确认 `python -m src.main --test` 通过
5. 提交 PR 时写清楚做了什么、为什么这样做

Bug report 或 Feature request 请在 [Issues](https://github.com/K1ssuh2rd/gzhu-score-monitor/issues) 提出。

---

## Credits · 致谢

原始项目：[01seven/Gzhu-Scores-checking](https://github.com/01seven/Gzhu-Scores-checking)

本项目在其基础上重构和增强了：session 缓存、交互式学期选择、心跳邮件、SMTP 诊断、加权均分 & GPA 计算、邮件 HTML 模板、TLS 兼容适配等。

---

## License · 许可证

MIT
