"""
全域快捷鍵模組 - 處理全域熱鍵註冊與回呼
"""
import keyboard
import threading
from typing import Callable, Optional


class GlobalHotkey:
    """全域快捷鍵管理器"""

    def __init__(self, hotkey_string: str):
        """
        初始化快捷鍵管理器

        Args:
            hotkey_string: 快捷鍵字串，如 "right alt + space"
        """
        self.hotkey_string = hotkey_string
        self.callback: Optional[Callable] = None
        self.is_registered = False

    def register(self, callback: Callable) -> bool:
        """
        註冊快捷鍵

        Args:
            callback: 按下快捷鍵時的回呼函數

        Returns:
            bool: 是否成功註冊
        """
        try:
            self.callback = callback
            keyboard.add_hotkey(self.hotkey_string, self._on_trigger)
            self.is_registered = True

            # 在獨立執行緒中監聽
            threading.Thread(
                target=keyboard.wait,
                daemon=True
            ).start()

            return True

        except Exception as e:
            print(f"註冊快捷鍵失敗: {e}")
            return False

    def _on_trigger(self):
        """快捷鍵觸發時的內部處理"""
        if self.callback:
            self.callback()

    def unregister(self):
        """取消註冊快捷鍵"""
        if self.is_registered:
            try:
                keyboard.remove_hotkey(self.hotkey_string)
            except Exception:
                pass
            self.is_registered = False
