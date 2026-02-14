"""
設定管理模組 - 處理 API 金鑰加密儲存與使用者設定
"""
import json
import os
from pathlib import Path
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64

# 設定檔路徑
CONFIG_DIR = Path.home() / ".audio-summarize"
CONFIG_FILE = CONFIG_DIR / "config.json"

# 預設設定
DEFAULT_CONFIG = {
    "api_key_encrypted": "",
    "timeout_minutes": 30,
    "selected_microphone": None,
    "hotkey": "right alt + space",
    "transcription_engine": "whisper_local",  # whisper_local, groq
    "whisper_model": "base",  # tiny, base, small, medium, large
}


class ConfigManager:
    """設定管理器 - 處理加密儲存與讀取"""

    def __init__(self):
        self.config = {}
        self._fernet = None
        self._load_or_create_config()

    def _get_machine_key(self) -> bytes:
        """取得機器特定的金鑰 (基於使用者與機器資訊)"""
        import platform
        import getpass

        # 使用使用者名稱與機器名稱產生鹽值
        salt = f"{getpass.getuser()}_{platform.node()}".encode()
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(b"audio-summarize-key"))
        return key

    def _load_or_create_config(self):
        """載入或建立設定檔"""
        CONFIG_DIR.mkdir(parents=True, exist_ok=True)

        if CONFIG_FILE.exists():
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                self.config = json.load(f)
        else:
            self.config = DEFAULT_CONFIG.copy()
            self._save_config()

        # 初始化加密器
        key = self._get_machine_key()
        self._fernet = Fernet(key)

    def _save_config(self):
        """儲存設定到檔案"""
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(self.config, f, indent=2, ensure_ascii=False)

    def set_api_key(self, api_key: str):
        """加密並儲存 API 金鑰"""
        encrypted = self._fernet.encrypt(api_key.encode())
        self.config["api_key_encrypted"] = encrypted.decode()
        self._save_config()

    def get_api_key(self) -> str | None:
        """解密並回傳 API 金鑰"""
        encrypted = self.config.get("api_key_encrypted", "")
        if not encrypted:
            return None
        try:
            decrypted = self._fernet.decrypt(encrypted.encode())
            return decrypted.decode()
        except Exception:
            return None

    def has_api_key(self) -> bool:
        """檢查是否有設定 API 金鑰"""
        return bool(self.config.get("api_key_encrypted"))

    def set_timeout(self, minutes: int):
        """設定超時時間 (分鐘)"""
        self.config["timeout_minutes"] = max(1, min(120, minutes))
        self._save_config()

    def get_timeout(self) -> int:
        """取得超時時間 (分鐘)"""
        return self.config.get("timeout_minutes", 30)

    def set_microphone(self, device_name: str | None):
        """設定選擇的麥克風"""
        self.config["selected_microphone"] = device_name
        self._save_config()

    def get_microphone(self) -> str | None:
        """取得選擇的麥克風"""
        return self.config.get("selected_microphone")

    def set_transcription_engine(self, engine: str):
        """設定轉錄引擎"""
        self.config["transcription_engine"] = engine
        self._save_config()

    def get_transcription_engine(self) -> str:
        """取得轉錄引擎"""
        return self.config.get("transcription_engine", "whisper_local")

    def set_whisper_model(self, model: str):
        """設定 Whisper 模型"""
        valid_models = ["tiny", "base", "small", "medium", "large"]
        if model in valid_models:
            self.config["whisper_model"] = model
            self._save_config()

    def get_whisper_model(self) -> str:
        """取得 Whisper 模型"""
        return self.config.get("whisper_model", "base")
