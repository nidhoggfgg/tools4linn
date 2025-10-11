import sys
from pathlib import Path

# 添加项目根目录到路径
sys.path.append(str(Path(__file__).parent))

from ui.main_window import MainWindow


def main():
    """主函数 - 启动 GUI 应用"""
    try:
        app = MainWindow()
        app.run()
    except Exception as e:
        print(f"启动应用时发生错误: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
