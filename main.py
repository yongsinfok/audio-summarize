"""
語音轉文字工具 - 主程式進入點

使用方法:
    python main.py

需求:
    - Windows 作業系統
    - Python 3.10 ~ 3.13
    - OpenAI API 金鑰
    - 麥克風裝置
"""
import sys
import warnings

# 忽略 PyAudio 警告
warnings.filterwarnings("ignore", message=".*PyAudio.*")


def check_python_version():
    """檢查 Python 版本"""
    version = sys.version_info
    if version.major == 3 and version.minor >= 14:
        print("=" * 50)
        print("❌ 錯誤: 不支援 Python 3.14")
        print("=" * 50)
        print()
        print("PyAudio 目前不支援 Python 3.14，請使用以下方式之一：")
        print()
        print("方式一: 使用 Conda (推薦)")
        print("  conda create -n audio-summarize python=3.13")
        print("  conda activate audio-summarize")
        print("  pip install -r requirements.txt")
        print()
        print("方式二: 降級到 Python 3.13")
        print("  從 https://www.python.org/downloads/ 下載 Python 3.13")
        print()
        print("=" * 50)
        sys.exit(1)
    elif version.major < 3 or (version.major == 3 and version.minor < 10):
        print("❌ 錯誤: 需要 Python 3.10 或更高版本")
        print(f"   目前版本: Python {version.major}.{version.minor}.{version.micro}")
        sys.exit(1)


check_python_version()

from ui.app_window import AppWindow


def main():
    """主程式進入點"""
    try:
        app = AppWindow()
        app.run()
    except KeyboardInterrupt:
        print("\n程式已終止")
        sys.exit(0)
    except Exception as e:
        print(f"程式發生錯誤: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
