"""
管理后台命令行工具
用法: python -m scripts.admin
"""
import sys
import json

from src.email_status_tracker import EmailStatusTracker
from src.admin_api import create_admin_api


def print_json(data: dict) -> None:
    """格式化打印JSON数据"""
    print(json.dumps(data, ensure_ascii=False, indent=2))


def main():
    """主函数"""
    print("=" * 60)
    print("成绩监测系统 - 管理后台")
    print("=" * 60)
    print()

    status_tracker = EmailStatusTracker()
    admin_api = create_admin_api(status_tracker)

    while True:
        print("请选择操作:")
        print("1. 查看所有邮件状态")
        print("2. 查看最近10条邮件状态")
        print("3. 查看测试邮件状态")
        print("4. 查看成绩通知邮件状态")
        print("5. 查看统计信息")
        print("6. 查看仪表板")
        print("7. 导出邮件状态到JSON文件")
        print("8. 清除旧记录（30天前）")
        print("0. 退出")
        print()

        choice = input("请输入选项 (0-8): ").strip()

        if choice == "0":
            print("退出管理后台")
            break

        elif choice == "1":
            print("\n所有邮件状态:")
            print("-" * 60)
            result = admin_api.get_all_status()
            print_json(result)
            print()

        elif choice == "2":
            print("\n最近10条邮件状态:")
            print("-" * 60)
            result = admin_api.get_recent_status(10)
            print_json(result)
            print()

        elif choice == "3":
            print("\n测试邮件状态:")
            print("-" * 60)
            result = admin_api.get_status_by_type("test")
            print_json(result)
            print()

        elif choice == "4":
            print("\n成绩通知邮件状态:")
            print("-" * 60)
            result = admin_api.get_status_by_type("score")
            print_json(result)
            print()

        elif choice == "5":
            print("\n统计信息:")
            print("-" * 60)
            result = admin_api.get_statistics()
            print_json(result)
            print()

        elif choice == "6":
            print("\n仪表板数据:")
            print("-" * 60)
            result = admin_api.get_dashboard_data()
            print_json(result)
            print()

        elif choice == "7":
            print("\n导出邮件状态:")
            print("-" * 60)
            result = admin_api.export_status_to_json()
            print_json(result)
            print()

        elif choice == "8":
            confirm = input("确认要清除30天前的记录吗？(y/n): ").strip().lower()
            if confirm == "y":
                print("\n清除旧记录:")
                print("-" * 60)
                result = admin_api.clear_old_status(30)
                print_json(result)
                print()
            else:
                print("已取消操作\n")

        else:
            print("无效选项，请重新输入\n")

        input("按回车键继续...")
        print("\n" * 2)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n程序已退出")
    except Exception as e:
        print(f"\n发生错误: {e}")
        sys.exit(1)
