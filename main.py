"""
語音轉文字工具 - 主程式進入點

使用方法:
    python main.py

需求:
    - Windows 作業系統
    - OpenAI API 金鑰
    - 麥克風裝置
"""
import sys
import warnings

# 忽略 PyAudio 警告
warnings.filterwarnings("ignore", message=".*PyAudio.*")

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
