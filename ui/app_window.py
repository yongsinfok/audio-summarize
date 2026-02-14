"""
主視窗模組 - CustomTkinter GUI
"""
import customtkinter as ctk
import threading
import time
from pathlib import Path
from typing import Optional, List

from core.recorder import AudioRecorder
from core.transcriber import Transcriber, ENGINES, WHISPER_MODELS
from core.hotkey import GlobalHotkey
from utils.config import ConfigManager
from utils.clipboard import copy_to_clipboard


class AppWindow(ctk.CTk):
    """主應用程式視窗"""

    # 狀態顏色
    COLOR_IDLE = "#4CAF50"      # 綠色 - 待命中
    COLOR_RECORDING = "#F44336" # 紅色 - 錄音中
    COLOR_PROCESSING = "#FF9800" # 橘色 - 處理中
    COLOR_ERROR = "#9E9E9E"     # 灰色 - 錯誤

    def __init__(self):
        super().__init__()

        # 初始化設定
        self.config = ConfigManager()
        self.recorder = AudioRecorder()
        self.transcriber: Optional[Transcriber] = None
        self.hotkey: Optional[GlobalHotkey] = None

        # 狀態變數
        self.is_recording = False
        self.recording_start_time: Optional[float] = None
        self.timeout_timer: Optional[threading.Thread] = None

        # 建立視窗
        self._setup_window()
        self._build_ui()

        # 初始化轉錄器
        self._init_transcriber()

        # 註冊全域快捷鍵
        self.hotkey = GlobalHotkey("right alt + space")
        self.hotkey.register(self._on_hotkey_pressed)

    def _setup_window(self):
        """設定視窗屬性"""
        self.title("語音轉文字工具")
        self.geometry("480x600")
        self.resizable(False, False)

        # 設定外觀主題
        ctk.set_appearance_mode("light")
        ctk.set_default_color_theme("blue")

    def _build_ui(self):
        """建立 UI 元件"""
        # 主容器
        main_frame = ctk.CTkScrollableFrame(self, fg_color="transparent")
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)

        # 標題
        title_label = ctk.CTkLabel(
            main_frame,
            text="🎤 語音轉文字工具",
            font=ctk.CTkFont(size=22, weight="bold")
        )
        title_label.pack(pady=(0, 15))

        # 轉錄引擎選擇
        engine_frame = ctk.CTkFrame(main_frame)
        engine_frame.pack(fill="x", pady=8)

        engine_label = ctk.CTkLabel(
            engine_frame,
            text="轉錄引擎:",
            font=ctk.CTkFont(size=13)
        )
        engine_label.pack(side="left", padx=(12, 8))

        self.engine_combo = ctk.CTkComboBox(
            engine_frame,
            values=list(ENGINES.values()),
            width=280,
            command=self._on_engine_change
        )
        self.engine_combo.pack(side="left", padx=(0, 12))

        # Whisper 模型選擇 (僅在選擇本地 Whisper 時顯示)
        self.whisper_model_frame = ctk.CTkFrame(main_frame)
        self.whisper_model_frame.pack(fill="x", pady=8)

        whisper_label = ctk.CTkLabel(
            self.whisper_model_frame,
            text="Whisper 模型:",
            font=ctk.CTkFont(size=13)
        )
        whisper_label.pack(side="left", padx=(12, 8))

        self.whisper_model_combo = ctk.CTkComboBox(
            self.whisper_model_frame,
            values=list(WHISPER_MODELS.values()),
            width=280,
            command=self._on_whisper_model_change
        )
        self.whisper_model_combo.pack(side="left", padx=(0, 12))

        # 麥克風選擇
        mic_frame = ctk.CTkFrame(main_frame)
        mic_frame.pack(fill="x", pady=8)

        mic_label = ctk.CTkLabel(
            mic_frame,
            text="麥克風:",
            font=ctk.CTkFont(size=13)
        )
        mic_label.pack(side="left", padx=(12, 8))

        self.mic_combo = ctk.CTkComboBox(
            mic_frame,
            values=[],
            width=280,
            command=self._on_microphone_change
        )
        self.mic_combo.pack(side="left", padx=(0, 12))

        # 超時設定
        timeout_frame = ctk.CTkFrame(main_frame)
        timeout_frame.pack(fill="x", pady=8)

        timeout_label = ctk.CTkLabel(
            timeout_frame,
            text="超時設定:",
            font=ctk.CTkFont(size=13)
        )
        timeout_label.pack(side="left", padx=(12, 8))

        self.timeout_slider = ctk.CTkSlider(
            timeout_frame,
            from_=1,
            to=120,
            number_of_steps=119,
            command=self._on_timeout_change
        )
        self.timeout_slider.pack(side="left", padx=(0, 8))

        self.timeout_value_label = ctk.CTkLabel(
            timeout_frame,
            text="30 分鐘",
            font=ctk.CTkFont(size=11),
            width=55
        )
        self.timeout_value_label.pack(side="left", padx=(0, 12))

        # 快捷鍵提示
        hotkey_frame = ctk.CTkFrame(main_frame)
        hotkey_frame.pack(fill="x", pady=8)

        hotkey_label = ctk.CTkLabel(
            hotkey_frame,
            text="快捷鍵:",
            font=ctk.CTkFont(size=13)
        )
        hotkey_label.pack(side="left", padx=(12, 8))

        hotkey_value = ctk.CTkLabel(
            hotkey_frame,
            text="Right Alt + Space",
            font=ctk.CTkFont(size=11, weight="bold")
        )
        hotkey_value.pack(side="left")

        # 狀態顯示
        self.status_frame = ctk.CTkFrame(main_frame, height=70)
        self.status_frame.pack(fill="x", pady=15)
        self.status_frame.pack_propagate(False)

        self.status_label = ctk.CTkLabel(
            self.status_frame,
            text="● 待命中",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=self.COLOR_IDLE
        )
        self.status_label.pack(expand=True)

        # 按鈕區
        button_frame = ctk.CTkFrame(main_frame)
        button_frame.pack(fill="x", pady=(10, 10))

        self.api_key_button = ctk.CTkButton(
            button_frame,
            text="API 金鑰",
            command=self._show_api_key_dialog,
            width=95
        )
        self.api_key_button.pack(side="left", padx=(15, 8), pady=12)

        self.save_button = ctk.CTkButton(
            button_frame,
            text="儲存設定",
            command=self._save_settings,
            width=95
        )
        self.save_button.pack(side="left", padx=(0, 8), pady=12)

        self.exit_button = ctk.CTkButton(
            button_frame,
            text="退出",
            command=self._on_exit,
            width=95,
            fg_color="#F44336",
            hover_color="#D32F2F"
        )
        self.exit_button.pack(side="right", padx=(8, 15), pady=12)

        # 載入設定
        self._load_settings()

    def _init_transcriber(self):
        """初始化轉錄器"""
        engine = self.config.get_transcription_engine()
        whisper_model = self.config.get_whisper_model()
        api_key = self.config.get_api_key()

        engine_config = {}
        if engine == "whisper_local":
            engine_config["model"] = whisper_model
        elif engine == "groq":
            engine_config["api_key"] = api_key or ""

        try:
            self.transcriber = Transcriber(engine, engine_config)
            print(f"轉錄器初始化完成: {engine}")
        except Exception as e:
            print(f"轉錄器初始化失敗: {e}")

    def _on_engine_change(self, choice: str):
        """轉錄引擎變更"""
        # 根據顯示的名稱找到對應的引擎 key
        engine_key = next((k for k, v in ENGINES.items() if v == choice), None)
        if engine_key:
            if engine_key == "groq":
                # 檢查是否有 API 金鑰
                if not self.config.get_api_key():
                    self._show_api_key_dialog("Groq")
            self.config.set_transcription_engine(engine_key)

    def _on_whisper_model_change(self, choice: str):
        """Whisper 模型變更"""
        model_key = next((k for k, v in WHISPER_MODELS.items() if v == choice), None)
        if model_key:
            self.config.set_whisper_model(model_key)

    def _on_microphone_change(self, choice: str):
        """麥克風選擇變更"""
        pass

    def _on_timeout_change(self, value: float):
        """超時滑桿變更"""
        minutes = int(value)
        self.timeout_value_label.configure(text=f"{minutes} 分鐘")

    def _load_settings(self):
        """載入設定到 UI"""
        # 載入轉錄引擎
        engine = self.config.get_transcription_engine()
        engine_display = ENGINES.get(engine, ENGINES["whisper_local"])
        self.engine_combo.set(engine_display)

        # 顯示/隱藏 Whisper 模型選擇
        if engine == "whisper_local":
            self.whisper_model_frame.pack(fill="x", pady=8)
            whisper_model = self.config.get_whisper_model()
            whisper_display = WHISPER_MODELS.get(whisper_model, WHISPER_MODELS["base"])
            self.whisper_model_combo.set(whisper_display)
        else:
            self.whisper_model_frame.pack_forget()

        # 載入超時設定
        timeout = self.config.get_timeout()
        self.timeout_slider.set(timeout)
        self.timeout_value_label.configure(text=f"{timeout} 分鐘")

        # 載入麥克風列表
        self._refresh_microphones()

        # 設定選中的麥克風
        saved_mic = self.config.get_microphone()
        if saved_mic:
            self.mic_combo.set(saved_mic)

    def _refresh_microphones(self):
        """重新掃描麥克風列表"""
        devices = self.recorder.list_microphones()
        mic_names = [d["name"] for d in devices]
        self.mic_combo.configure(values=mic_names)

        if mic_names and not self.mic_combo.get():
            self.mic_combo.set(mic_names[0])

    def _save_settings(self):
        """儲存設定"""
        # 儲存超時
        timeout = int(self.timeout_slider.get())
        self.config.set_timeout(timeout)

        # 儲存麥克風
        mic_name = self.mic_combo.get()
        self.config.set_microphone(mic_name if mic_name else None)

        # 重新初始化轉錄器
        self._init_transcriber()

        # 顯示儲存成功
        self._show_status("✓ 設定已儲存", self.COLOR_IDLE)

    def _show_api_key_dialog(self, engine_name: str = "Groq"):
        """顯示 API 金鑰輸入對話框"""
        dialog = ctk.CTkToplevel(self)
        dialog.title(f"設定 {engine_name} API 金鑰")
        dialog.geometry("450x280")
        dialog.resizable(False, False)

        dialog.transient(self)
        dialog.grab_set()

        current_key = self.config.get_api_key()

        # 說明文字
        if engine_name == "Groq":
            info_text = "請輸入您的 Groq API 金鑰\n(格式: gsk_...)"
            url = "https://console.groq.com/keys"
        else:
            info_text = f"請輸入您的 {engine_name} API 金鑰"
            url = ""

        if current_key:
            masked = current_key[:8] + "..." if len(current_key) > 8 else "***"
            info_text = f"目前金鑰: {masked}\n\n請輸入新的 API 金鑰"

        info_label = ctk.CTkLabel(
            dialog,
            text=info_text,
            font=ctk.CTkFont(size=12)
        )
        info_label.pack(pady=(20, 15))

        api_key_entry = ctk.CTkEntry(
            dialog,
            placeholder_text="gsk_..." if engine_name == "Groq" else "API Key",
            width=380,
            show="*"
        )
        api_key_entry.pack(pady=(0, 15))
        api_key_entry.focus()

        if url:
            hint_label = ctk.CTkLabel(
                dialog,
                text=f"前往 {url} 取得 API 金鑰",
                font=ctk.CTkFont(size=10),
                text_color="gray"
            )
            hint_label.pack(pady=(0, 10))

        def save_api_key():
            api_key = api_key_entry.get().strip()
            if api_key:
                self.config.set_api_key(api_key)
                self._show_status(f"✓ {engine_name} API 金鑰已更新", self.COLOR_IDLE)
                dialog.destroy()
                self._init_transcriber()
            else:
                api_key_entry.configure(border_color="#F44336", border_width=2)

        api_key_entry.bind("<Return>", lambda e: save_api_key())

        button_frame = ctk.CTkFrame(dialog, fg_color="transparent")
        button_frame.pack(pady=10)

        ctk.CTkButton(
            button_frame,
            text="取消",
            command=dialog.destroy,
            width=100
        ).pack(side="left", padx=5)

        ctk.CTkButton(
            button_frame,
            text="確認",
            command=save_api_key,
            width=100
        ).pack(side="left", padx=5)

    def _on_hotkey_pressed(self):
        """快捷鍵被按下時的處理"""
        if self.is_recording:
            self._stop_recording()
        else:
            self._start_recording()

    def _start_recording(self):
        """開始錄音"""
        mic_name = self.mic_combo.get()
        mic_index = None
        if mic_name:
            mic_index = self.recorder.find_microphone_by_name(mic_name)

        if self.recorder.start_recording(mic_index):
            self.is_recording = True
            self.recording_start_time = time.time()
            self._show_status("● 錄音中...", self.COLOR_RECORDING)

            timeout_minutes = self.config.get_timeout()
            self.timeout_timer = threading.Thread(
                target=self._timeout_monitor,
                args=(timeout_minutes,),
                daemon=True
            )
            self.timeout_timer.start()
        else:
            self._show_status("✗ 錄音啟動失敗", self.COLOR_ERROR)

    def _timeout_monitor(self, minutes: int):
        """監控錄音超時"""
        time.sleep(minutes * 60)
        if self.is_recording:
            self.after(0, self._stop_recording)

    def _stop_recording(self):
        """停止錄音並處理"""
        if not self.is_recording:
            return

        self.is_recording = False
        self._show_status("● 處理中...", self.COLOR_PROCESSING)

        audio_file = self.recorder.stop_recording()

        if audio_file and self.transcriber:
            threading.Thread(
                target=self._process_transcription,
                args=(audio_file,),
                daemon=True
            ).start()
        else:
            self._show_status("✗ 轉錄失敗", self.COLOR_ERROR)

    def _process_transcription(self, audio_file: Path):
        """處理轉錄 (在執行緒中執行)"""
        try:
            result = self.transcriber.process(audio_file)

            if result:
                copy_to_clipboard(result)
                audio_file.unlink()

                self.after(0, lambda: self._show_status(
                    "✓ 已複製到剪貼簿",
                    self.COLOR_IDLE
                ))

                self.after(3000, lambda: self._show_status(
                    "● 待命中",
                    self.COLOR_IDLE
                ))
            else:
                self.after(0, lambda: self._show_status(
                    "✗ 轉錄失敗",
                    self.COLOR_ERROR
                ))

        except Exception as e:
            print(f"處理轉錄時發生錯誤: {e}")
            self.after(0, lambda: self._show_status(
                "✗ 處理失敗",
                self.COLOR_ERROR
            ))

    def _show_status(self, text: str, color: str):
        """顯示狀態文字"""
        self.status_label.configure(text=text, text_color=color)

    def _on_exit(self):
        """退出程式"""
        if self.is_recording:
            self.recorder.stop_recording()

        self.recorder.cleanup_temp_files()

        self.quit()
        self.destroy()

    def run(self):
        """執行應用程式"""
        self.mainloop()
