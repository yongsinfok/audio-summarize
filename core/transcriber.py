"""
轉錄模組 - 支援多種語音轉文字引擎
"""
import os
from pathlib import Path
from typing import Optional, List
import wave
import io

# 引擎設定
ENGINES = {
    "whisper_local": "本地 Whisper (免費, 需要硬體)",
    "groq": "Groq API (免費額度, 快速)",
}

# Whisper 模型說明
WHISPER_MODELS = {
    "tiny": "Tiny (1GB VRAM, 最快, 較低準確度)",
    "base": "Base (1.5GB VRAM, 平衡)",
    "small": "Small (2GB VRAM, 較好準確度)",
    "medium": "Medium (5GB VRAM, 高準確度)",
    "large": "Large (10GB VRAM, 最高準確度)",
}


class AudioSegmenter:
    """音訊分割器 - 將長音訊分割成片段"""

    def __init__(self, chunk_duration_sec: int = 30):
        """
        初始化分割器

        Args:
            chunk_duration_sec: 每個片段的秒數
        """
        self.chunk_duration = chunk_duration_sec

    def split_audio(self, audio_file: Path) -> List[bytes]:
        """
        將 WAV 檔案分割成多個片段

        Args:
            audio_file: WAV 音訊檔案路徑

        Returns:
            List[bytes]: 分割後的音訊資料串列 (WAV 格式)
        """
        chunks = []

        with wave.open(str(audio_file), 'rb') as wav_file:
            frames = wav_file.getnframes()
            rate = wav_file.getframerate()
            width = wav_file.getsampwidth()
            channels = wav_file.getnchannels()
            chunk_frames = int(self.chunk_duration * rate)
            all_frames = wav_file.readframes(frames)

        for i in range(0, len(all_frames), chunk_frames * width * channels):
            chunk_data = all_frames[i:i + chunk_frames * width * channels]
            if len(chunk_data) == 0:
                break
            output = io.BytesIO()
            with wave.open(output, 'wb') as chunk_wav:
                chunk_wav.setnchannels(channels)
                chunk_wav.setsampwidth(width)
                chunk_wav.setframerate(rate)
                chunk_wav.writeframes(chunk_data)
            chunks.append(output.getvalue())

        return chunks


class WhisperLocalTranscriber:
    """本地 Whisper 轉錄器"""

    def __init__(self, model: str = "base"):
        """
        初始化 Whisper 轉錄器

        Args:
            model: Whisper 模型大小 (tiny, base, small, medium, large)
        """
        self.model = model
        self._model_loaded = False
        self._whisper_model = None

    def _load_model(self):
        """延遲載入模型"""
        if self._model_loaded:
            return

        try:
            import whisper
            print(f"正在載入 Whisper {self.model} 模型...")
            self._whisper_model = whisper.load_model(self.model)
            self._model_loaded = True
            print(f"Whisper {self.model} 模型載入完成")
        except ImportError:
            print("錯誤: whisper 套件未安裝")
            print("請執行: pip install openai-whisper")
            raise
        except Exception as e:
            print(f"載入 Whisper 模型失敗: {e}")
            raise

    def transcribe(self, audio_file: Path) -> Optional[str]:
        """
        轉錄音訊檔案

        Args:
            audio_file: 音訊檔案路徑

        Returns:
            Optional[str]: 轉錄後的文字
        """
        try:
            self._load_model()

            # 確保檔案存在
            if not audio_file.exists():
                print(f"音訊檔案不存在: {audio_file}")
                return None

            print(f"正在轉錄檔案: {audio_file}")

            # 直接載入音訊陣列，避免 ffmpeg 依賴
            import numpy as np

            # 使用 wave 讀取音訊
            import wave
            with wave.open(str(audio_file), "rb") as wf:
                frames = wf.getnframes()
                rate = wf.getframerate()
                # 讀取音訊資料
                audio_data = wf.readframes(frames)

            # 轉換為 numpy 陣列
            audio_array = np.frombuffer(audio_data, dtype=np.int16).astype(np.float32) / 32768.0

            # 直接使用 numpy 陣列進行轉錄
            result = self._whisper_model.transcribe(
                audio_array,
                language="zh",  # 中文
                task="transcribe",
                fp16=False  # CPU 不支援 FP16
            )
            return result.get("text", "").strip()
        except Exception as e:
            print(f"Whisper 轉錄失敗: {type(e).__name__}: {e}")
            import traceback
            traceback.print_exc()
            return None


class GroqTranscriber:
    """Groq API 轉錄器 (使用 Whisper 模型)"""

    def __init__(self, api_key: str):
        """
        初始化 Groq 轉錄器

        Args:
            api_key: Groq API 金鑰
        """
        self.api_key = api_key
        self.api_url = "https://api.groq.com/openai/v1/audio/transcriptions"

    def transcribe(self, audio_file: Path) -> Optional[str]:
        """
        轉錄音訊檔案

        Args:
            audio_file: 音訊檔案路徑

        Returns:
            Optional[str]: 轉錄後的文字
        """
        try:
            import requests

            with open(audio_file, "rb") as f:
                files = {"file": ("audio.wav", f, "audio/wav")}
                data = {
                    "model": "whisper-large-v3",
                    "response_format": "text"
                }
                headers = {
                    "Authorization": f"Bearer {self.api_key}"
                }

                response = requests.post(
                    self.api_url,
                    files=files,
                    data=data,
                    headers=headers,
                    timeout=120
                )

            if response.status_code == 200:
                return response.text.strip()
            else:
                print(f"Groq API 錯誤: {response.status_code} - {response.text}")
                return None

        except Exception as e:
            print(f"Groq 轉錄失敗: {e}")
            return None


class Transcriber:
    """轉錄器 - 支援多種引擎"""

    def __init__(self, engine: str = "whisper_local", engine_config: dict = None):
        """
        初始化轉錄器

        Args:
            engine: 轉錄引擎 (whisper_local, groq)
            engine_config: 引擎設定 {"api_key": "...", "model": "base"}
        """
        self.engine = engine
        self.engine_config = engine_config or {}
        self.segmenter = AudioSegmenter()
        self._transcriber = None
        self._init_transcriber()

    def _init_transcriber(self):
        """初始化轉錄器"""
        if self.engine == "whisper_local":
            model = self.engine_config.get("model", "base")
            self._transcriber = WhisperLocalTranscriber(model)
        elif self.engine == "groq":
            api_key = self.engine_config.get("api_key", "")
            if not api_key:
                print("警告: Groq API 金鑰未設定")
            self._transcriber = GroqTranscriber(api_key)
        else:
            print(f"未知的轉錄引擎: {self.engine}")

    def transcribe(self, audio_file: Path) -> Optional[str]:
        """
        轉錄音訊檔案

        Args:
            audio_file: 音訊檔案路徑

        Returns:
            Optional[str]: 轉錄後的文字
        """
        if self._transcriber is None:
            print("轉錄器未初始化")
            return None

        return self._transcriber.transcribe(audio_file)

    def process(self, audio_file: Path) -> Optional[str]:
        """
        完整處理流程

        Args:
            audio_file: 音訊檔案路徑

        Returns:
            Optional[str]: 最終文字
        """
        return self.transcribe(audio_file)
