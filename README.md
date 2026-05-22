# Gzhu Score Monitor

[![Python](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

广州大学教务系统成绩监测工具。有新成绩发布时，自动通过 QQ 邮箱通知你。

> 这完全是个零基础教程，一步一步跟着做就行。只要你会上网、会用记事本，就能搞定。

---

## 这个工具能做什么？

教务系统出新成绩时你自己是不知道的，总得隔三差五打开查，很烦。这个工具帮你盯着 —— 它每隔 6 小时自动登录教务系统查一次，如果分数有变化，就给你发邮件通知。你什么都不用管，有新成绩会自动收到邮件。

两种用法：
- **在自己电脑上跑**：程序在后台挂着，电脑开机就在查
- **只看一次成绩**：查一次打印结果，不持续运行

---

## 第一步：检查 Python 是否装好

这个工具是用 Python 写的，你的电脑需要有 Python。

### 怎么确认？

1. 按键盘上的 **`Win + R`**（Win 键就是左下角那个 Windows 图标键），会弹出一个"运行"窗口
2. 输入 **`cmd`**，然后按回车，会弹出一个黑底白字的窗口，这就是"命令提示符"
3. 在黑窗口里输入这行字，然后按回车：

```
python --version
```

如果出现类似这样的输出：

```
Python 3.9.13
```

说明你已经装了 Python，**跳到第二步**。

如果出现的是：

```
'python' 不是内部或外部命令，也不是可运行的程序或批处理文件。
```

说明还没装 Python，继续往下看。

### 安装 Python

1. 打开浏览器，访问 **https://www.python.org/downloads/**
2. 页面中间有个黄色大按钮，写着 **"Download Python 3.x.x"**，点它下载安装包
3. 下载完成后双击打开安装程序
4. **关键一步**：安装界面的最下面有个复选框，写着 **"Add Python to PATH"**（或者 "Add python.exe to PATH"），**一定要勾上！** 不勾的话后面会很麻烦
5. 勾好之后点 **"Install Now"**（现在安装），一路等它装完就行
6. 装完之后，**重新打开一个命令提示符窗口**（旧的关掉，按 `Win + R` → `cmd` 重新打开）
7. 再输入 `python --version`，这次应该能看到版本号了

---

## 第二步：下载这个项目

### 如果你会用 git：

```bash
git clone https://github.com/K1ssuh2rd/gzhu-score-monitor.git
cd gzhu-score-monitor
```

### 如果你不会用 git（推荐这种方式）：

1. 打开浏览器，访问 **https://github.com/K1ssuh2rd/gzhu-score-monitor**
2. 页面右上角有个绿色的 **"<> Code"** 按钮，点它
3. 在弹出的菜单里，点最下面的 **"Download ZIP"**
4. 下载完成后，在你喜欢的位置（比如桌面）解压这个 ZIP 文件
5. 解压后会得到一个文件夹叫 `gzhu-score-monitor`

---

## 第三步：安装依赖

"依赖"就是别人写好的代码包，这个项目需要用到它们。安装很简单：

1. 在文件管理器里打开刚才解压出来的 `gzhu-score-monitor` 文件夹
2. 在文件夹的**地址栏**里直接输入 **`cmd`**，然后按回车

> 这一步是要在"这个文件夹里"打开命令提示符。地址栏就是文件管理器上方显示路径的那一栏，比如显示着 `此电脑 > 桌面 > gzhu-score-monitor` 的地方，点一下变成蓝色的路径，删掉直接输入 `cmd`，回车。

3. 在弹出的黑窗口里输入以下命令，回车：

```bash
pip install -r requirements.txt
```

4. 你会看到一堆文字在滚，这是在下载和安装依赖。等它停下来，看到最后一行没有红色的 "error" 字样，就说明装好了。

> 如果这一步报错说 `pip` 不是命令，说明你在安装 Python 的时候没勾选 "Add Python to PATH"。回到第一步重新安装 Python，这次一定把那勾勾上。

---

## 第四步：获取 QQ 邮箱授权码（重要！）

程序要发邮件通知你，需要一个发件邮箱。我们用 QQ 邮箱来发。

> 下面每一步请严格照做，别跳步骤。

### 4.1 打开 QQ 邮箱网页版

打开浏览器，访问 **https://mail.qq.com/** ，用你的 QQ 号登录。

### 4.2 进入设置页面

登录后，看页面左上角，会看到 QQ 邮箱的 logo 和你的邮箱地址。在页面的左上区域找到 **"设置"** 两个字（在 logo 下面一点），点击它。

### 4.3 切换到"账户"标签

点完"设置"后，页面会变。在页面中间偏上的位置，有一排标签，找到一个叫 **"账户"** 的标签，点击它。

### 4.4 找到 SMTP 服务

在"账户"页面里，往下滚动，找到一块标题叫 **"POP3/IMAP/SMTP/Exchange/CardDAV/CalDAV服务"** 的区域。这里面有几项服务，我们要找的是：

> **SMTP 服务**（用于发信）

现在你的 SMTP 服务那一行显示的应该是 **"已关闭"**。

### 4.5 开启 SMTP 服务

1. 点击 SMTP 服务那行右边的 **"开启"** 按钮
2. QQ 会弹出一个安全验证，让你用手机发一条短信到某个号码
3. 拿出手机，按屏幕上显示的号码和短信内容，**原样发送这条短信**
4. 短信发送成功后，回到电脑上，点击页面上的 **"我已发送"** 或类似的确认按钮

### 4.6 拿到授权码

验证通过后，页面上会弹出一个框，里面显示的是一串字母，类似这样：

```
tfnkppxabcdedabd
```

**这串字母就是你的 SMTP 授权码。**

> **⚠️ 极度重要**：这串授权码**只会在这个弹窗里出现一次**，关掉之后就再也看不到了！请立刻把它复制下来，记在手机备忘录或者纸上。如果忘了，只能重新走一遍 4.5 的流程重新获取。

### 4.7 确认授权码拿到了

你现在手头应该有以下信息：

- 你的 QQ 邮箱地址，格式是 `你的QQ号@qq.com`，比如 `123456789@qq.com`
- 一串字母授权码，比如 `tfnkppxabcdedabd`

确认都拿到了，再进入下一步。

---

## 第五步：填写配置文件

### 5.1 找到配置文件模板

在 `gzhu-score-monitor` 文件夹里，找到一个叫 **`.env.example`** 的文件。

> 如果看不到这个文件，可能是系统隐藏了文件扩展名。没关系，它是个浅色的文件，图标可能像一张纸。

### 5.2 创建真正的配置文件

**Windows 用户：**

1. 先选中 `.env.example` 这个文件，按 `Ctrl + C` 复制，再按 `Ctrl + V` 粘贴
2. 你会得到一个叫 `.env.example - 副本` 的文件，把它**重命名**为 **`.env`**（注意：名字就是 `.env`，点号在最前面）

> 系统可能会警告"如果改变文件扩展名，文件可能不可用"，不用管，点是。

**Mac / Linux 用户：**

在黑窗口中（先 cd 到这个文件夹）输入：

```bash
cp .env.example .env
```

### 5.3 用记事本编辑 .env 文件

1. **右键点击** `.env` 文件
2. 选择 **"打开方式"** → **"记事本"**
3. 文件内容长这样：

```
GZHU_USERNAME=你的学号
GZHU_PASSWORD=你的教务系统密码
QQ_EMAIL=你的QQ邮箱@qq.com
QQ_AUTH_CODE=你的SMTP授权码
RECEIVER_EMAILS=receiver1@example.com,receiver2@example.com
TEST_EMAIL=test_receiver@example.com
...
```

### 5.4 填入你的真实信息

把等号右边的示例文字**替换成你自己的真实信息**。只改下面这些行就行，其他的不用动：

| 这一行 | 改成什么 |
|--------|----------|
| `GZHU_USERNAME=你的学号` | 把"你的学号"改成你的学号，如 `GZHU_USERNAME=2112345678` |
| `GZHU_PASSWORD=你的教务系统密码` | 改成你登录教务系统的密码 |
| `QQ_EMAIL=你的QQ邮箱@qq.com` | 改成你的 QQ 邮箱地址，如 `QQ_EMAIL=123456789@qq.com` |
| `QQ_AUTH_CODE=你的SMTP授权码` | 改成第四步拿到的那串字母，如 `QQ_AUTH_CODE=tfnkppxabcdedabd` |
| `RECEIVER_EMAILS=receiver1@example.com` | 改成接收通知的邮箱，可以填你自己的 QQ 邮箱；**多个邮箱用英文逗号分隔**，如 `RECEIVER_EMAILS=123456@qq.com,roommate@qq.com` |

改完之后，比如你的学号是 2112345678，密码是 abc123，QQ 是 123456789@qq.com，授权码是 tfnkppxabcdedabd，那 `.env` 文件的前几行应该是这样：

```
GZHU_USERNAME=2112345678
GZHU_PASSWORD=abc123
QQ_EMAIL=123456789@qq.com
QQ_AUTH_CODE=tfnkppxabcdedabd
RECEIVER_EMAILS=123456789@qq.com
```

4. 确认无误后，**点菜单栏的"文件" → "保存"**，然后关掉记事本。

---

## 第六步：发送测试邮件

现在来做一次测试，看看所有设置是否正确。

1. 在 `gzhu-score-monitor` 文件夹的地址栏输入 `cmd`，打开命令提示符
2. 输入以下命令，回车：

```bash
python -m src.main --test
```

3. 等待几秒钟，看看屏幕上显示什么：

   - 如果看到 **"登录成功，测试邮件已发送"** → **恭喜，一切正常！** 去你的邮箱看看有没有收到测试邮件（可能被放到垃圾箱里了，翻一下）
   - 如果看到 **"登录失败"** → 检查学号和密码填对了没有，确认你能在浏览器里正常打开教务系统网站
   - 如果看到一堆报错 → 跳到最下面的"常见问题"部分看看

> 如果测试邮件没收到，可以运行 `python scripts/test_smtp.py` 来专门诊断邮件发送的问题。

---

## 第七步：开始监测

### 方式A：持续监测（推荐，电脑长期开着）

```bash
python -m src.main
```

程序启动后，会显示类似这样的信息：

```
初始化完成，当前共有 42 门课程成绩
开始监控成绩变化...
检查间隔: 21600 秒
```

这说明程序已经在后台跑着了。每隔 6 小时它会自动查一次，有新成绩就发邮件。

**要停止的时候**，在这个窗口里按 `Ctrl + C`。

> 这个窗口不能关。关了程序也就停了。你可以把它最小化，不影响你干别的。

### 方式B：只看一次成绩

```bash
python -m src.main --once
```

执行一次，打印你当前所有课程的成绩，然后退出。不会发邮件。

---

## 怎么让程序开机自启？

### Windows

1. 在桌面右键 → **新建** → **快捷方式**
2. 位置填：`python -m src.main`（如果你想把程序藏起来在后台跑，用 `pythonw -m src.main`）
3. 点下一步，起个名字叫"成绩监测"，完成
4. 按 `Win + R`，输入 **`shell:startup`**，回车
5. 把这个快捷方式**拖进**刚打开的文件夹
6. 以后每次开机，程序就会自动开始监测了

### Mac / Linux

可以用 crontab 设置开机启动：

```bash
crontab -e
```

添加一行：

```
@reboot cd /你的路径/gzhu-score-monitor && python -m src.main
```

---

## 邮件管理后台

程序内置了一个简单的管理后台，可以查看邮件发送记录：

```bash
python -m scripts.admin
```

---

## 完整配置说明

`.env` 文件里所有可以改的选项（不改就用默认值，也很正常）：

| 变量 | 必填 | 默认值 | 说明 |
|------|:---:|--------|------|
| `GZHU_USERNAME` | ✓ | - | 学号 |
| `GZHU_PASSWORD` | ✓ | - | 教务系统密码 |
| `QQ_EMAIL` | ✓ | - | 发通知的 QQ 邮箱 |
| `QQ_AUTH_CODE` | ✓ | - | QQ 邮箱 SMTP 授权码（第四步拿到的） |
| `RECEIVER_EMAILS` | ✓ | - | 收通知的邮箱，多个用英文逗号分隔 |
| `TEST_EMAIL` | | 和 RECEIVER_EMAILS 一样 | 测试邮件的收件地址 |
| `CHECK_INTERVAL` | | 21600（6小时） | 检查间隔，单位秒 |
| `EMAIL_SUBJECT` | | 新成绩通知 | 通知邮件的标题 |
| `ENABLE_LOGIN_TEST_EMAIL` | | true | 登录后是否自动发测试邮件 |
| `HEARTBEAT_ENABLED` | | true | 是否定期发心跳邮件确认程序正常 |
| `HEARTBEAT_INTERVAL` | | 86400（24小时） | 心跳邮件间隔，单位秒 |

---

## 项目结构

```
├── pyproject.toml              # 项目元数据，不用管
├── requirements.txt            # Python 依赖列表
├── scripts/                    # 辅助工具
│   ├── test_smtp.py            # SMTP 连通性诊断工具
│   └── admin.py                # 邮件发送记录管理
├── src/                        # 核心代码
│   ├── main.py                 # 主程序入口
│   ├── gzhu_login.py           # 教务系统登录
│   ├── score_parser.py         # 成绩解析
│   ├── email_notifier.py       # 邮件发送
│   ├── templates.py            # 邮件 HTML 模板
│   └── config.py               # 配置加载
├── logs/                       # 运行日志（自动生成）
└── status/                     # 成绩快照和登录状态（自动生成）
```

---

## 常见问题

### 邮件发不出去？

1. 确认 QQ 邮箱 SMTP 服务确实开了（去 QQ 邮箱设置→账户里看看 SMTP 那行是不是"已开启"）
2. `.env` 里的 `QQ_AUTH_CODE` 填的是授权码，**不是你的 QQ 密码**
3. 运行诊断脚本看看具体哪里出了问题：

```bash
python scripts/test_smtp.py
```

### 提示"登录失败"？

1. 检查 `.env` 里的学号和密码有没有填错（注意大小写、空格）
2. 打开浏览器，去教务系统网站试着登录一次，确认账号密码对的
3. 看看 `logs/score_monitor.log` 这个日志文件，里面会有详细的错误信息

### 成绩更新了但没收到通知？

1. 程序是**每 6 小时**查一次，不是秒级更新的，耐心等一等
2. 检查 `logs/score_monitor.log`，确认程序还在正常运行
3. 到邮箱的**垃圾邮件**文件夹翻一翻，有时通知邮件会被误判为垃圾邮件

### 能改检查频率吗？

可以。打开 `.env` 文件，改 `CHECK_INTERVAL` 的值。这个值的单位是**秒**：

- 想每 1 小时查一次：填 `3600`
- 想每 3 小时查一次：填 `10800`
- 想每 12 小时查一次：填 `43200`

> ⚠️ 不建议设太短（比如几分钟），太频繁的请求可能会被教务系统封 IP。

### cmd 窗口关了就停了怎么办？

这是正常的。如果你想让程序在后台静默运行、不显示窗口，用这个命令：

```bash
pythonw -m src.main
```

（注意是 `pythonw` 不是 `python`，多一个 w。）这样不会弹出任何窗口，程序在后台跑。要停止的话去任务管理器里找 python 进程结束掉。

---

## 相关项目

原始项目：[01seven/Gzhu-Scores-checking](https://github.com/01seven/Gzhu-Scores-checking)

## License

MIT
