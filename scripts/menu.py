"""
交互式菜单 — 不用记命令，选数字即可操作
用法: python scripts/menu.py
"""
import os
import subprocess
import sys
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parent.parent
VENV_PYTHON = PROJECT_DIR / ".venv" / "Scripts" / "python.exe"
if sys.platform != "win32":
    VENV_PYTHON = PROJECT_DIR / ".venv" / "bin" / "python"
PYTHON = str(VENV_PYTHON) if VENV_PYTHON.exists() else sys.executable


def _build_args(*flags: str) -> list[str]:
    args = [PYTHON, "-m", "src.main", *flags]
    if sys.platform == "win32":
        args.insert(1, "-X")
        args.insert(2, "utf8")
    return args


def _run(*flags: str) -> None:
    env = {**os.environ}
    if sys.platform == "win32":
        env["PYTHONIOENCODING"] = "utf-8"
    subprocess.run(_build_args(*flags), cwd=str(PROJECT_DIR), env=env)


def main() -> None:
    while True:
        print()
        print("=" * 40)
        print("1 - 查本学期成绩")
        print("2 - 查其他学期（方向键选择）")
        print("3 - 开启持续监测（成绩变化自动发邮件）")
        print("4 - 退出")
        print("=" * 40)
        choice = input("> ").strip()

        if choice == "1":
            _run("--once")
        elif choice == "2":
            _run("--once", "--semester")
        elif choice == "3":
            _run()
        elif choice == "4":
            break
        else:
            print("无效选项，请重新输入")


if __name__ == "__main__":
    main()
