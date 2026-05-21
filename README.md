# Gzhu Score Monitor

[![Python](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

广州大学教务系统成绩监测工具。定时检查成绩变化，通过 QQ 邮箱发送 HTML 通知。

> 基于 [@01seven](https://github.com/01seven) 的[原始项目](https://github.com/01seven/Gzhu-Scores-checking)改进，增加了自动重连、会话缓存、GitHub Actions 部署等能力。

## 快速开始

```bash
git clone <your-repo-url>
cd Gzhu-Score-Monitor
cp .env.example .env        # 编辑 .env 填入账号和邮箱信息
pip install -e .            # 安装依赖并注册命令行工具
gzhu-monitor --test         # 发送测试邮件，验证一切正常
gzhu-monitor                # 启动持续监测
```

## 命令行

```bash
gzhu-monitor           # 持续监测（每 6 小时检查一次）
gzhu-monitor --once    # 查询一次，打印当前成绩
gzhu-monitor --test    # 登录并发送测试邮件
gzhu-monitor --check   # CI 模式：对比上次状态，有变化则通知
gzhu-test-smtp         # SMTP 连通性测试
gzhu-admin             # 邮件发送历史管理
```

未安装时可用 `python -m` 等价运行，见[手动运行](#手动运行)。

## 相比原项目的改进

- **自动重连** — 查询失败时自动重新登录（最多 3 次），避免因会话过期中断监测
- **会话缓存** — 登录凭证持久化到本地，重启无需重新登录
- **模板分离** — HTML 邮件模板集中在 `src/templates.py`，易于自定义样式
- **标准打包** — `pyproject.toml` + `pip install -e .`，注册全局命令行工具
- **CI 就绪** — 内置 GitHub Actions 工作流，Fork 后配置 Secrets 即可无人值守运行
- **安全修复** — 测试邮件不再包含明文密码

## 配置

编辑 `.env` 文件：

| 变量 | 必填 | 说明 |
|------|:---:|------|
| `GZHU_USERNAME` | ✓ | 学号 |
| `GZHU_PASSWORD` | ✓ | 教务系统密码 |
| `QQ_EMAIL` | ✓ | 发送通知的 QQ 邮箱 |
| `QQ_AUTH_CODE` | ✓ | QQ 邮箱 SMTP 授权码（[获取方式](#获取-qq-邮箱授权码)） |
| `RECEIVER_EMAILS` | ✓ | 接收通知的邮箱，逗号分隔 |
| `TEST_EMAIL` | | 测试邮件收件地址 |
| `CHECK_INTERVAL` | | 检查间隔（秒），默认 21600 |
| `HEARTBEAT_ENABLED` | | 是否启用心跳邮件，默认 true |
| `HEARTBEAT_INTERVAL` | | 心跳间隔（秒），默认 86400 |

### 获取 QQ 邮箱授权码

QQ 邮箱 → 设置 → 账户 → POP3/SMTP 服务 → 开启并生成授权码。

## 项目结构

```
├── LICENSE
├── pyproject.toml
├── .github/workflows/check.yml   # GitHub Actions
├── scripts/                      # 命令行工具
│   ├── test_smtp.py
│   └── admin.py
├── src/                          # 核心代码
│   ├── main.py                   # 入口，ScoreMonitor 主逻辑
│   ├── gzhu_login.py             # CAS 登录 + DES 加密
│   ├── score_parser.py           # 成绩 JSON 解析
│   ├── email_notifier.py         # SMTP 发送
│   ├── email_status_tracker.py   # 发送记录
│   ├── templates.py              # 邮件 HTML 模板
│   ├── config.py                 # 配置加载
│   └── ...
├── logs/                         # 运行日志
└── status/                       # 成绩快照与会话缓存
```

## GitHub Actions

Fork 本仓库，在 Settings → Secrets → Actions 中添加配置项（同 `.env` 文件中的必填项），Actions 每 6 小时自动运行一次 `--check`，成绩有变化即邮件通知。

也可在 Actions 页面手动触发（`workflow_dispatch`）。

## 手动运行

未安装时可直接用 `python -m` 方式运行：

```bash
python -m src.main              # 持续监测
python -m src.main --once       # 查询一次
python -m src.main --test       # 发送测试邮件
python -m src.main --check      # CI 模式
python scripts/test_smtp.py     # SMTP 测试
python -m scripts.admin         # 管理后台
```

## FAQ

**邮件发不出去？** 确认 QQ 邮箱 SMTP 已开启，授权码正确。运行 `gzhu-test-smtp` 诊断。

**登录失败？** 检查账号密码，查看 `logs/` 下的日志。确认教务系统可正常访问。

**成绩没更新？** 系统每 6 小时检查一次。确认教务系统上确实有新成绩，查看日志确认运行状态。

## License

MIT
