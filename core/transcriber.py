"""
轉錄模組 - 處理 Whisper API 與 GPT 潤飾
"""
from pathlib import Path
from openai import OpenAI
from typing import Optional

# Whisper 轉錄提示詞 (可提升中文轉錄準確度)
WHISHER_PROMPT = "這是一段中文語音轉文字記錄。"

# GPT 潤飾提示詞
POLISH_PROMPT = """請將以下轉錄文字進行整理：
1. 去除口語贅字（如：嗯、啊、那個、就是、對、然后）
2. 修正標點符號，讓語句通順
3. 保持原意和語氣
4. 輸出整理後的純文字，不要有任何解釋

轉錄內容：
{transcript}"""


class Transcriber:
    """轉錄器 - 處理音訊轉文字與潤飾"""

    def __init__(self, api_key: str):
        """
        初始化轉錄器

        Args:
            api_key: OpenAI API 金鑰
        """
        self.client = OpenAI(api_key=api_key)

    def transcribe(self, audio_file: Path) -> Optional[str]:
        """
        使用 Whisper API 轉錄音訊

        Args:
            audio_file: 音訊檔案路徑

        Returns:
            Optional[str]: 轉錄後的文字，失敗回傳 None
        """
        try:
            with open(audio_file, "rb") as f:
                transcript = self.client.audio.transcriptions.create(
                    model="whisper-1",
                    file=f,
                    language="zh",  # 指定中文
                    prompt=WHISHER_PROMPT,
                    response_format="text"
                )
            return transcript

        except Exception as e:
            print(f"Whisper 轉錄失敗: {e}")
            return None

    def polish(self, text: str) -> Optional[str]:
        """
        使用 GPT-4o-mini 潤飾文字

        Args:
            text: 原始轉錄文字

        Returns:
            Optional[str]: 潤飾後的文字，失敗回傳 None
        """
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "user",
                        "content": POLISH_PROMPT.format(transcript=text)
                    }
                ],
                temperature=0.3,
            )
            return response.choices[0].message.content

        except Exception as e:
            print(f"GPT 潤飾失敗: {e}")
            # 失敗時回傳原始文字
            return text

    def process(self, audio_file: Path) -> Optional[str]:
        """
        完整處理流程：轉錄 + 潤飾

        Args:
            audio_file: 音訊檔案路徑

        Returns:
            Optional[str]: 最終文字，失敗回傳 None
        """
        # 先轉錄
        transcript = self.transcribe(audio_file)
        if not transcript:
            return None

        # 再潤飾
        polished = self.polish(transcript)
        return polished if polished else transcript
