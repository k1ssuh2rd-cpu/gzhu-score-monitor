"""
主程序入口
"""
import argparse
import json
import os
import signal
import sys
import time
from typing import Dict, Optional
from datetime import datetime

from src.config import config, BASE_DIR
from src.logger import logger
from src.gzhu_login import GZHULogin
from src.score_parser import (
    parse_course_scores, parse_course_details, calc_weighted_average,
    ScoreParseError,
)
from src.email_notifier import create_notifier, EmailSendError
from src.templates import score_update, heartbeat, query_scores

__version__ = "1.1.0"


def _get_key():
    """跨平台读取单个按键。返回 'up'/'down'/'enter'/'esc'/None。"""
    if os.name == 'nt':
        import msvcrt
        key = msvcrt.getch()
        if key == b'\xe0' or key == b'\x00':
            key = msvcrt.getch()
            if key == b'H':
                return 'up'
            elif key == b'P':
                return 'down'
        elif key == b'\r' or key == b'\n':
            return 'enter'
        elif key == b'\x1b':
            return 'esc'
        return None
    else:
        import termios
        import tty
        fd = sys.stdin.fileno()
        old = termios.tcgetattr(fd)
        try:
            tty.setraw(fd)
            key = sys.stdin.read(1)
            if key == '\x1b':
                key += sys.stdin.read(2)
                if key == '\x1b[A':
                    return 'up'
                elif key == '\x1b[B':
                    return 'down'
                return 'esc'
            elif key in ('\r', '\n'):
                return 'enter'
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old)
        return None


def _filter_semesters(semesters: list[dict], username: str) -> list[dict]:
    """过滤学期列表：只显示入学年份以后的学期，移除未来学期，按时间倒序"""
    now = datetime.now()
    cur_xnm = now.year if now.month >= 8 else now.year - 1
    enroll_year = 2000 + int(username[1:3])

    filtered = [s for s in semesters if enroll_year <= int(s["xnm"]) <= cur_xnm]
    filtered.sort(key=lambda s: (int(s["xnm"]), int(s["xqm"])), reverse=True)
    return filtered


def _choose_semester_interactive(gzhu_login) -> tuple:
    """
    方向键交互式选择学期，返回 (xnm, xqm, xnmmc, xqmmc)。
    返回 (None, None, None, None) 表示用户取消。
    """
    semesters = gzhu_login.get_available_semesters()
    if not semesters:
        print("未能获取可选学期列表")
        return None, None, None, None

    semesters = _filter_semesters(semesters, gzhu_login.username)
    if not semesters:
        print("没有可选的学期")
        return None, None, None, None

    if not sys.stdin.isatty():
        return _choose_semester_by_input(semesters)

    now = datetime.now()
    cur_xnm = str(now.year if now.month >= 8 else now.year - 1)
    cur_xqm = "3" if now.month >= 8 or now.month == 1 else "12"
    default_idx = next(
        (i for i, s in enumerate(semesters) if s["xnm"] == cur_xnm and s["xqm"] == cur_xqm),
        0
    )
    current_idx = default_idx
    printed_lines = 0

    def render():
        nonlocal printed_lines
        if printed_lines > 0:
            sys.stdout.write(f"\033[{printed_lines}A")
        printed_lines = 0
        sys.stdout.write("\n请选择要查询的学期（↑↓ 移动，回车确认，Esc 取消）：\n\n")
        printed_lines += 3
        for i, s in enumerate(semesters):
            if i == current_idx:
                sys.stdout.write(f"  \033[1;36m▶ {s['xnmmc']} 学年第 {s['xqmmc']} 学期\033[0m\n")
            else:
                sys.stdout.write(f"    {s['xnmmc']} 学年第 {s['xqmmc']} 学期\n")
            printed_lines += 1
        sys.stdout.flush()

    render()
    try:
        while True:
            key = _get_key()
            if key == 'up':
                current_idx = (current_idx - 1) % len(semesters)
                render()
            elif key == 'down':
                current_idx = (current_idx + 1) % len(semesters)
                render()
            elif key == 'enter':
                s = semesters[current_idx]
                return s["xnm"], s["xqm"], s["xnmmc"], s["xqmmc"]
            elif key == 'esc':
                print("\n已取消")
                return None, None, None, None
    except Exception:
        return _choose_semester_by_input(semesters)


def _choose_semester_by_input(semesters: list[dict]) -> tuple:
    """回退方案：输入序号选择学期"""
    print("\n请选择要查询的学期：")
    for i, s in enumerate(semesters, 1):
        label = f"{s['xnmmc']} 学年第 {s['xqmmc']} 学期"
        print(f"  [{i:2d}] {label}")

    while True:
        try:
            choice = input(f"\n请输入序号 (1-{len(semesters)}，直接回车取消): ").strip()
            if not choice:
                return None, None, None, None
            idx = int(choice) - 1
            if 0 <= idx < len(semesters):
                s = semesters[idx]
                return s["xnm"], s["xqm"], s["xnmmc"], s["xqmmc"]
            print(f"请输入 1 到 {len(semesters)} 之间的数字")
        except ValueError:
            print("请输入有效数字")
        except (KeyboardInterrupt, EOFError):
            print()
            return None, None, None, None


class ScoreMonitor:
    """成绩监控类"""

    MAX_RECONNECT = 3

    def __init__(self):
        self.gzhu_login: Optional[GZHULogin] = None
        self.notifier = create_notifier()
        self.previous_score_count = 0
        self.previous_scores: Dict[str, str] = {}
        self.running = False
        self.last_heartbeat_time: Optional[datetime] = None
        self.reconnect_count = 0
    
    def initialize(self) -> bool:
        """初始化监控器（含查询本学期成绩做基线）"""
        if not self._login_only():
            return False
        initial_data = self.gzhu_login.query_scores()
        if initial_data:
            try:
                initial_scores = parse_course_scores(initial_data)
                self.previous_score_count = len(initial_scores)
                self.previous_scores = initial_scores.copy()
                logger.info(f"初始化完成，当前共有{self.previous_score_count}门课程成绩")
                return True
            except ScoreParseError:
                logger.error("解析初始成绩数据失败")
                return False
        else:
            logger.error("获取初始成绩数据失败")
            return False
    
    def _generate_score_update_email(
        self,
        new_scores: Dict[str, str],
        old_scores: Dict[str, str]
    ) -> str:
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        return score_update(new_scores, old_scores, current_time)
    
    def check_scores(self) -> None:
        """
        检查成绩变化
        """
        data = self.gzhu_login.query_scores()
        if not data:
            logger.warning("获取成绩数据失败，尝试重新登录...")
            if not self._try_reconnect():
                return
            data = self.gzhu_login.query_scores()
            if not data:
                return
        
        try:
            scores = parse_course_scores(data)
            current_count = len(scores)
            
            logger.info(f"当前课程数: {current_count}, 上次课程数: {self.previous_score_count}")
            
            if current_count != self.previous_score_count or scores != self.previous_scores:
                logger.info("检测到成绩变化！")
                
                email_body = self._generate_score_update_email(scores, self.previous_scores)
                
                try:
                    self.notifier.send(
                        subject=config.EMAIL_SUBJECT,
                        body=email_body,
                        is_html=True
                    )
                    self.previous_score_count = current_count
                    self.previous_scores = scores.copy()
                except EmailSendError:
                    logger.error("发送通知邮件失败")
            else:
                logger.debug("成绩无变化")
                
        except ScoreParseError:
            logger.error("解析成绩数据失败")

    def _try_reconnect(self) -> bool:
        """尝试重新登录，返回是否成功"""
        if self.reconnect_count >= self.MAX_RECONNECT:
            logger.error(f"已达最大重连次数({self.MAX_RECONNECT})，放弃重连")
            return False
        self.reconnect_count += 1
        logger.info(f"尝试重新登录 (第{self.reconnect_count}/{self.MAX_RECONNECT}次)...")
        if self.gzhu_login.login():
            self.reconnect_count = 0
            logger.info("重新登录成功")
            return True
        logger.error("重新登录失败")
        return False

    def _generate_heartbeat_email(self) -> str:
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        if self.last_heartbeat_time:
            delta = datetime.now() - self.last_heartbeat_time
            hours = int(delta.total_seconds() // 3600)
            minutes = int((delta.total_seconds() % 3600) // 60)
            uptime = f"{hours}小时{minutes}分钟"
        else:
            uptime = "刚刚启动"
        return heartbeat(current_time, uptime, self.previous_score_count)
    
    def _check_and_send_heartbeat(self) -> None:
        """
        检查并发送心跳邮件
        """
        if not config.HEARTBEAT_ENABLED:
            return
        
        current_time = datetime.now()
        
        # 首次运行或到达心跳间隔时发送
        should_send = (
            self.last_heartbeat_time is None or
            (current_time - self.last_heartbeat_time).total_seconds() >= config.HEARTBEAT_INTERVAL
        )
        
        if should_send:
            logger.info("发送心跳邮件...")
            try:
                email_body = self._generate_heartbeat_email()
                self.notifier.send(
                    subject="[心跳] 成绩监测系统运行正常",
                    body=email_body,
                    is_html=True
                )
                self.last_heartbeat_time = current_time
                logger.info("心跳邮件发送成功")
            except EmailSendError as e:
                logger.error(f"心跳邮件发送失败: {e}")
    
    def _login_only(self) -> bool:
        """仅登录，不查本学期成绩（指定学期查询时用）"""
        if not config.GZHU_USERNAME or not config.GZHU_PASSWORD:
            logger.error("教务系统账号密码未配置，请检查.env文件")
            return False
        if not self.notifier:
            logger.error("邮件通知器初始化失败")
            return False
        self.gzhu_login = GZHULogin(
            config.GZHU_USERNAME,
            config.GZHU_PASSWORD,
            email_notifier=self.notifier,
        )
        if not self.gzhu_login.login():
            logger.error("登录失败，请检查账号密码")
            return False
        return True

    def _print_score_report(self, data: str) -> None:
        """格式化打印成绩报告（--once 模式用）"""
        raw = json.loads(data)
        total_items = len(raw.get('items', []))
        courses = parse_course_details(data)
        avg = calc_weighted_average(courses)
        if not courses:
            print("\n  暂无成绩数据\n")
            return

        first = (raw.get('items') or [{}])[0]
        xnmmc = first.get('xnmmc', '')
        xqmmc = first.get('xqmmc', '')
        title = f"{xnmmc} 学年第 {xqmmc} 学期  成绩单" if xnmmc and xqmmc else "成绩单"

        sep = "-" * 50
        print()
        print(f"  {title}")
        print(f"  {sep}")

        for c in courses:
            print(f"  {c['name']}")
            score_display = f"{c['score']:.0f}"
            if c['cj'] not in (str(int(c['score'])), str(c['score'])):
                score_display = f"{c['cj']}({score_display})"
            print(f"    成绩 {score_display:>6}    绩点 {c['jd']:.1f}    学分 {c['xf']:.1f}")

        print(f"  {sep}")
        print(f"  {len(courses)} 门    总学分 {avg['total_xf']:.1f}    加权均分 {avg['avg_score']}    平均绩点 {avg['gpa']}")
        if total_items != len(courses):
            print(f"  （教务系统返回 {total_items} 条，{total_items - len(courses)} 条无成绩已跳过）")
        print(f"  {sep}")
        print()

        # 保存原始 JSON 到文件方便排查
        debug_file = BASE_DIR / "logs" / "last_score_response.json"
        debug_file.parent.mkdir(parents=True, exist_ok=True)
        debug_file.write_text(data, encoding="utf-8")
        logger.debug(f"原始成绩数据已保存到 {debug_file}")

    def run_once(self, xnm: str = None, xqm: str = None, send_email: bool = False) -> None:
        """查询一次成绩并打印结果，指定 send_email 同时发邮件"""
        if xnm is not None:
            if not self._login_only():
                logger.error("初始化失败")
                return
        elif not self.initialize():
            logger.error("初始化失败")
            return
        data = self.gzhu_login.query_scores(xnm=xnm, xqm=xqm)
        if data:
            try:
                self._print_score_report(data)
                if send_email:
                    scores = parse_course_scores(data)
                    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    self.notifier.send(
                        subject=config.EMAIL_SUBJECT,
                        body=query_scores(scores, now),
                        is_html=True,
                    )
                    print(f"成绩邮件已发送（{len(scores)} 门课程）")
            except ScoreParseError:
                logger.error("解析成绩数据失败")
            except EmailSendError:
                logger.error("发送邮件失败")
        else:
            logger.error("查询成绩失败")

    def run_test(self) -> None:
        """发送测试邮件验证配置"""
        if not config.GZHU_USERNAME or not config.GZHU_PASSWORD:
            logger.error("教务系统账号密码未配置，请检查.env文件")
            return
        if not self.notifier:
            logger.error("邮件通知器初始化失败")
            return
        self.gzhu_login = GZHULogin(
            config.GZHU_USERNAME,
            config.GZHU_PASSWORD,
            email_notifier=self.notifier,
        )
        if self.gzhu_login.login():
            print("登录成功，测试邮件已发送")
        else:
            print("登录失败，请检查账号密码和网络连接")

    def run(self) -> None:
        """
        运行监控循环
        """
        if not self.initialize():
            logger.error("初始化失败，程序退出")
            return

        self.running = True
        logger.info("开始监控成绩变化...")
        logger.info(f"检查间隔: {config.CHECK_INTERVAL}秒")

        try:
            while self.running:
                try:
                    self.check_scores()
                    self._check_and_send_heartbeat()
                    self.reconnect_count = 0
                except Exception as e:
                    logger.error(f"检查异常: {e}")
                    self._try_reconnect()
                time.sleep(config.CHECK_INTERVAL)
        except KeyboardInterrupt:
            logger.info("接收到中断信号，正在停止...")
        finally:
            self.stop()
    
    def stop(self) -> None:
        """
        停止监控
        """
        self.running = False
        logger.info("监控已停止")


def signal_handler(signum, frame):
    """信号处理函数"""
    logger.info(f"接收到信号 {signum}，准备退出...")
    sys.exit(0)


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="广州大学成绩监测系统")
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    parser.add_argument("--once", action="store_true", help="查询一次成绩并打印结果")
    parser.add_argument("--email", action="store_true", help="配合 --once，同时发送邮件报告")
    parser.add_argument("--test", action="store_true", help="发送测试邮件验证配置并退出")
    parser.add_argument("--semester", action="store_true", help="交互式选择查询学期")
    args = parser.parse_args()

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    monitor = ScoreMonitor()

    xnm = xqm = None
    if args.semester:
        if not monitor._login_only():
            sys.exit(1)
        xnm, xqm, xnmmc, xqmmc = _choose_semester_interactive(monitor.gzhu_login)
        if xnm is None:
            return
        print(f"已选择: {xnmmc} 学年第 {xqmmc} 学期\n")

    if args.test:
        monitor.run_test()
    elif args.once:
        monitor.run_once(xnm=xnm, xqm=xqm, send_email=args.email)
    else:
        monitor.run()


if __name__ == "__main__":
    main()
