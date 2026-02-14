"""
剪貼簿模組 - 處理複製文字到剪貼簿
"""
import subprocess


def copy_to_clipboard(text: str) -> bool:
    """
    複製文字到系統剪貼簿

    Args:
        text: 要複製的文字

    Returns:
        bool: 是否成功
    """
    try:
        # Windows
        subprocess.run(
            ["clip"],
            input=text.encode("utf-8"),
            check=True,
            shell=True
        )
        return True
    except Exception:
        return False
