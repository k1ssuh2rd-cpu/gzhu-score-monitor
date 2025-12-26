# 广州大学成绩监测系统

自动监测广州大学教务系统成绩发布情况，并通过邮件及时通知。

## 功能特性

- 自动登录广州大学教务系统
- 实时监测成绩发布情况
- 检测到新成绩时自动发送邮件通知
- 支持多收件人
- 完整的日志记录

## 安装依赖

```bash
pip install -r requirements.txt
```

## 配置说明

1. 复制 `.env.example` 为 `.env`
2. 填写你的账号密码和邮箱配置

```bash
cp .env.example .env
```

## 使用方法

```bash
python src/main.py
```

## 项目结构

```
成绩监测/
├── .env.example          # 环境变量示例
├── .gitignore           # Git忽略文件
├── requirements.txt     # 依赖列表
├── README.md            # 项目说明
├── logs/                # 日志目录
└── src/
    ├── __init__.py
    ├── config.py        # 配置管理
    ├── logger.py        # 日志配置
    ├── gzhu_login.py    # 登录模块
    ├── score_parser.py  # 成绩解析
    ├── email_notifier.py # 邮件通知
    └── main.py          # 主程序入口
```

## 注意事项

- 请妥善保管 `.env` 文件，不要提交到版本控制系统
- QQ邮箱需要开启SMTP服务并获取授权码
- 建议使用虚拟环境运行
