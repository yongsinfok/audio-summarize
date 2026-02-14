"""
轉錄模組 - 處理 Z.AI GLM-ASR-2512 音訊轉文字
"""
import requests
from pathlib import Path
from typing import Optional, List
import wave
import io
import tempfile
import os

# Z.AI API 設定
ZAI_API_URL = "https://api.z.ai/api/paas/v4/audio/transcriptions"
ZAI_MODEL = "glm-asr-2512"
# GLM-ASR-2512 限制：最長 30 秒
MAX_AUDIO_DURATION = 30  # 秒


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
    """轉錄器 - 使用 Z.AI GLM-ASR-2512 進行音訊轉文字"""

    def __init__(self, api_key: str):
        """
        初始化轉錄器

        Args:
            api_key: Z.AI API 金鑰 (格式: id.secret)
        """
        self.api_key = api_key
        self.segmenter = AudioSegmenter()
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "multipart/form-data"
        }

    def _transcribe_chunk(self, audio_data: bytes) -> Optional[str]:
        """
        轉錄單一音訊片段

        Args:
            audio_data: WAV 格式音訊資料

        Returns:
            Optional[str]: 轉錄後的文字，失敗回傳 None
        """
        try:
            # 準備檔案
            files = {
                'file': ('audio.wav', audio_data, 'audio/wav')
            }
            data = {
                'model': ZAI_MODEL
            }

            # 移除 Content-Type，讓 requests 自動處理 multipart boundary
            headers = {"Authorization": f"Bearer {self.api_key}"}

            response = requests.post(
                ZAI_API_URL,
                files=files,
                data=data,
                headers=headers,
                timeout=60
            )

            if response.status_code == 200:
                result = response.json()
                return result.get('text', '')
            else:
                print(f"Z.AI API 錯誤: {response.status_code} - {response.text}")
                return None

        except Exception as e:
            print(f"轉錄片段失敗: {e}")
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
