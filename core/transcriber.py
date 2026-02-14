"""
轉錄模組 - 處理 Z.AI GLM-ASR 音訊轉文字
"""
from pathlib import Path
from typing import Optional, List
import wave
import io
import tempfile
import os

# Z.AI (智譜 AI) API 設定
ZAI_MODEL = "glm-asr"  # 官方 SDK 模型名稱
MAX_AUDIO_DURATION = 30  # 秒 - GLM-ASR 單次請求最長 30 秒


class AudioSegmenter:
    """音訊分割器 - 將長音訊分割成 30 秒片段"""

    def __init__(self, chunk_duration_sec: int = MAX_AUDIO_DURATION):
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
            # 取得音訊參數
            frames = wav_file.getnframes()
            rate = wav_file.getframerate()
            width = wav_file.getsampwidth()
            channels = wav_file.getnchannels()

            # 計算每個片段的框架數
            chunk_frames = int(self.chunk_duration * rate)

            # 讀取所有框架
            all_frames = wav_file.readframes(frames)

        # 分割音訊
        for i in range(0, len(all_frames), chunk_frames * width * channels):
            chunk_data = all_frames[i:i + chunk_frames * width * channels]

            if len(chunk_data) == 0:
                break

            # 建立新的 WAV 格式片段
            output = io.BytesIO()
            with wave.open(output, 'wb') as chunk_wav:
                chunk_wav.setnchannels(channels)
                chunk_wav.setsampwidth(width)
                chunk_wav.setframerate(rate)
                chunk_wav.writeframes(chunk_data)

            chunks.append(output.getvalue())

        return chunks


class Transcriber:
    """轉錄器 - 使用 Z.AI GLM-ASR 進行音訊轉文字"""

    def __init__(self, api_key: str):
        """
        初始化轉錄器

        Args:
            api_key: Z.AI API 金鑰 (格式: id.secret)
        """
        self.api_key = api_key
        self.segmenter = AudioSegmenter()
        self._client = None
        self._init_client()

    def _init_client(self):
        """初始化 ZhipuAI 客戶端"""
        try:
            from zhipuai import ZhipuAI
            self._client = ZhipuAI(api_key=self.api_key)
        except ImportError:
            print("警告: zhipuai 套件未安裝，請執行: pip install zhipuai")
            self._client = None
        except Exception as e:
            print(f"初始化 ZhipuAI 客戶端失敗: {e}")
            self._client = None

    def _transcribe_chunk(self, audio_data: bytes) -> Optional[str]:
        """
        轉錄單一音訊片段

        Args:
            audio_data: WAV 格式音訊資料

        Returns:
            Optional[str]: 轉錄後的文字，失敗回傳 None
        """
        if self._client is None:
            print("ZhipuAI 客戶端未初始化")
            return None

        try:
            # 使用官方 SDK
            audio_file = io.BytesIO(audio_data)
            audio_file.name = "audio.wav"

            response = self._client.audio.transcriptions.create(
                model=ZAI_MODEL,
                file=audio_file,
                stream=False
            )

            # SDK 回應格式: 回傳一個物件串列
            # 每個物件有 choices[0].message.content 包含轉錄文字
            if response and len(response) > 0:
                result = response[0]
                if hasattr(result, 'choices') and len(result.choices) > 0:
                    content = result.choices[0].message.content
                    return content

            return None

        except Exception as e:
            print(f"轉錄片段失敗: {type(e).__name__}: {e}")
            return None

    def transcribe(self, audio_file: Path) -> Optional[str]:
        """
        轉錄完整音訊檔案（自動分割處理）

        Args:
            audio_file: 音訊檔案路徑

        Returns:
            Optional[str]: 轉錄後的文字，失敗回傳 None
        """
        # 分割音訊
        chunks = self.segmenter.split_audio(audio_file)

        if not chunks:
            print("無法分割音訊檔案")
            return None

        print(f"音訊已分割成 {len(chunks)} 個片段，開始轉錄...")

        # 轉錄每個片段
        transcripts = []
        for i, chunk in enumerate(chunks):
            print(f"正在轉錄片段 {i + 1}/{len(chunks)}...")
            text = self._transcribe_chunk(chunk)
            if text:
                transcripts.append(text)
            else:
                print(f"片段 {i + 1} 轉錄失敗")

        # 合併結果
        if transcripts:
            # GLM-ASR-2512 有內建上下文理解，直接拼接即可
            full_text = ''.join(transcripts)
            return full_text.strip()
        else:
            return None

    def process(self, audio_file: Path) -> Optional[str]:
        """
        完整處理流程：轉錄（GLM-ASR-2512 已內建潤飾功能）

        Args:
            audio_file: 音訊檔案路徑

        Returns:
            Optional[str]: 最終文字，失敗回傳 None
        """
        return self.transcribe(audio_file)
