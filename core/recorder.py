"""
錄音模組 - 處理音訊錄製與裝置列舉
"""
import pyaudio
import wave
import threading
import time
from pathlib import Path
from typing import List, Callable, Optional

# 音訊參數
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 16000  # Whisper 推薦的取樣率
CHUNK = 1024


class AudioRecorder:
    """音訊錄音器"""

    def __init__(self):
        self.pyaudio = pyaudio.PyAudio()
        self.is_recording = False
        self.recording_thread: Optional[threading.Thread] = None
        self.stream = None
        self.temp_dir = Path.home() / ".audio-summarize" / "temp"
        self.temp_dir.mkdir(parents=True, exist_ok=True)
        self.current_file: Optional[Path] = None

    def list_microphones(self) -> List[dict]:
        """
        列出所有可用的麥克風裝置

        Returns:
            List[dict]: 裝置列表，每個裝置包含 name 和 index
        """
        devices = []
        for i in range(self.pyaudio.get_device_count()):
            info = self.pyaudio.get_device_info_by_index(i)
            # 只列出輸入裝置且至少有一個通道
            if info["maxInputChannels"] > 0:
                devices.append({
                    "name": info["name"],
                    "index": i
                })
        return devices

    def get_default_microphone_index(self) -> int:
        """取得預設麥克風索引"""
        try:
            device_info = self.pyaudio.get_default_input_device_info()
            return int(device_info["index"])
        except Exception:
            # 如果沒有預設裝置，嘗試找到第一個輸入裝置
            devices = self.list_microphones()
            if devices:
                return devices[0]["index"]
            raise Exception("找不到可用的麥克風裝置")

    def find_microphone_by_name(self, name: str) -> int | None:
        """根據名稱尋找麥克風索引"""
        devices = self.list_microphones()
        for device in devices:
            if device["name"] == name:
                return device["index"]
        return None

    def start_recording(self, device_index: Optional[int] = None) -> bool:
        """
        開始錄音

        Args:
            device_index: 麥克風裝置索引，None 使用預設

        Returns:
            bool: 是否成功開始錄音
        """
        if self.is_recording:
            return False

        try:
            if device_index is None:
                device_index = self.get_default_microphone_index()

            self.stream = self.pyaudio.open(
                format=FORMAT,
                channels=CHANNELS,
                rate=RATE,
                input=True,
                input_device_index=device_index,
                frames_per_buffer=CHUNK
            )

            self.is_recording = True
            self.frames = []

            # 在新執行緒中錄音
            self.recording_thread = threading.Thread(target=self._record_loop)
            self.recording_thread.daemon = True
            self.recording_thread.start()

            return True

        except Exception as e:
            print(f"啟動錄音失敗: {e}")
            return False

    def _record_loop(self):
        """錄音迴圈 (在獨立執行緒中執行)"""
        while self.is_recording:
            try:
                data = self.stream.read(CHUNK, exception_on_overflow=False)
                self.frames.append(data)
            except Exception:
                break

    def stop_recording(self) -> Optional[Path]:
        """
        停止錄音並儲存檔案

        Returns:
            Optional[Path]: 儲存的音訊檔案路徑，失敗回傳 None
        """
        if not self.is_recording:
            return None

        self.is_recording = False

        # 等待錄音執行緒結束
        if self.recording_thread:
            self.recording_thread.join(timeout=2)

        # 關閉串流
        if self.stream:
            self.stream.stop_stream()
            self.stream.close()
            self.stream = None

        # 儲存檔案
        if hasattr(self, "frames") and self.frames:
            timestamp = int(time.time() * 1000)
            filename = f"recording_{timestamp}.wav"
            filepath = self.temp_dir / filename

            try:
                with wave.open(str(filepath), "wb") as wf:
                    wf.setnchannels(CHANNELS)
                    wf.setsampwidth(self.pyaudio.get_sample_size(FORMAT))
                    wf.setframerate(RATE)
                    wf.writeframes(b"".join(self.frames))

                self.current_file = filepath
                return filepath

            except Exception as e:
                print(f"儲存錄音失敗: {e}")
                return None

        return None

    def cleanup_temp_files(self):
        """清理所有暫存檔案"""
        try:
            for file in self.temp_dir.glob("*.wav"):
                file.unlink()
        except Exception:
            pass

    def __del__(self):
        """解構函數，釋放資源"""
        if hasattr(self, "pyaudio"):
            self.pyaudio.terminate()
