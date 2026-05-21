# Gzhu Score Monitor

[![Python](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

广州大学教务系统成绩监测工具。有新成绩发布时，自动通过 QQ 邮箱通知你。

## 一、准备工作

- 一台能联网的电脑（Windows / Mac / Linux 都行）
- 安装了 Python 3.9 或更高版本（[下载地址](https://www.python.org/downloads/)）
- 一个 QQ 邮箱，并开启 SMTP 服务获取授权码（[怎么获取？](#怎么获取-qq-邮箱授权码)）

## 二、安装和配置

### 1. 下载项目

```bash
git clone https://github.com/k1ssuh2rd-cpu/gzhu-score-monitor.git
cd gzhu-score-monitor
```

如果不会用 git，也可以点仓库页面的绿色 "Code" 按钮 → Download ZIP，解压后进入文件夹。

### 2. 安装依赖

```bash
pip install -r requirements.txt
```

### 3. 填写配置

```bash
copy .env.example .env    # Windows 命令提示符
cp .env.example .env      # Mac / Linux / Git Bash
```

然后用记事本或任意编辑器打开 `.env` 文件，填入你的信息：

| 变量 | 填什么 |
|------|--------|
| `GZHU_USERNAME` | 你的学号 |
| `GZHU_PASSWORD` | 教务系统密码 |
| `QQ_EMAIL` | 你的 QQ 邮箱地址，如 `123456@qq.com` |
| `QQ_AUTH_CODE` | QQ 邮箱的 SMTP 授权码（**不是 QQ 密码！**） |
| `RECEIVER_EMAILS` | 接收通知的邮箱，多个用逗号分隔 |

其余配置保持默认即可，后面想调整再看[完整配置说明](#完整配置说明)。

### 4. 发送测试邮件

```bash
python -m src.main --test
```

看到"登录成功，测试邮件已发送"说明一切正常。没收到邮件？检查 [常见问题](#常见问题)。

## 三、开始使用

### 持续监测（推荐长期挂着）

```bash
python -m src.main
```

程序会每 6 小时检查一次成绩，有变化就发邮件通知。按 `Ctrl+C` 停止。

### 只看一次成绩

```bash
python -m src.main --once
```

## 怎么获取 QQ 邮箱授权码？

1. 登录 QQ 邮箱网页版
2. 点击 **设置** → **账户**
3. 找到 **POP3/IMAP/SMTP 服务**
4. 开启 **SMTP 服务**，按提示发送短信后会得到一个授权码（一串字母）
5. 把这串字母填到 `.env` 的 `QQ_AUTH_CODE` 里

> 授权码只在生成时显示一次，记得保存好。如果忘了就重新生成。

## 完整配置说明

`.env` 文件里所有可配置的选项：

| 变量 | 必填 | 默认值 | 说明 |
|------|:---:|--------|------|
| `GZHU_USERNAME` | ✓ | - | 学号 |
| `GZHU_PASSWORD` | ✓ | - | 教务系统密码 |
| `QQ_EMAIL` | ✓ | - | 发通知的 QQ 邮箱 |
| `QQ_AUTH_CODE` | ✓ | - | QQ 邮箱 SMTP 授权码 |
| `RECEIVER_EMAILS` | ✓ | - | 收通知的邮箱，逗号分隔 |
| `TEST_EMAIL` | | 和 RECEIVER_EMAILS 相同 | 测试邮件的收件地址 |
| `CHECK_INTERVAL` | | 21600（6小时） | 成绩检查间隔，单位秒 |
| `EMAIL_SUBJECT` | | 新成绩通知 | 通知邮件的标题 |
| `ENABLE_LOGIN_TEST_EMAIL` | | true | 登录成功后是否发测试邮件 |
| `HEARTBEAT_ENABLED` | | true | 是否定期发送心跳邮件确认程序正常 |
| `HEARTBEAT_INTERVAL` | | 86400（24小时） | 心跳邮件间隔，单位秒 |

## 项目结构

```
├── pyproject.toml              # 项目元数据
├── requirements.txt            # Python 依赖
├── .github/workflows/check.yml # GitHub Actions 工作流
├── scripts/                    # 辅助工具
│   ├── test_smtp.py            # SMTP 连通性测试
│   └── admin.py                # 邮件发送记录管理
├── src/                        # 核心代码
│   ├── main.py                 # 主程序入口
│   ├── gzhu_login.py           # 教务系统登录
│   ├── score_parser.py         # 成绩解析
│   ├── email_notifier.py       # 邮件发送
│   ├── templates.py            # 邮件 HTML 模板
│   └── config.py               # 配置加载
├── logs/                       # 运行日志（自动生成）
└── status/                     # 成绩快照（自动生成）
```

## 常见问题

**邮件发不出去？**
确认 QQ 邮箱 SMTP 已开启，`.env` 里填的是授权码而不是 QQ 密码。运行 `python scripts/test_smtp.py` 可以诊断 SMTP 连接。

**提示"登录失败"？**
检查学号和密码是否正确，确认教务系统网站能正常打开。查看 `logs/` 目录下的日志文件了解详情。

**成绩更新了但没通知？**
程序每 6 小时才检查一次，不是实时的。如果教务系统上确实有新成绩但你还没收到通知，检查 `logs/score_monitor.log` 确认程序正常运行。

**怎么让程序开机自启？**
Windows 可以用任务计划程序，Linux/Mac 可以用 systemd 或 cron。程序本身不提供自启功能，需要自己配置系统。

## 相关项目

原始项目：[01seven/Gzhu-Scores-checking](https://github.com/01seven/Gzhu-Scores-checking)

## License

MIT
