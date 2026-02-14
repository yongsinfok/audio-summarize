# 語音轉文字工具 🎤

一個 Windows 桌面應用程式，透過全域快捷鍵快速錄音並轉換為整理好的文字，自動複製到剪貼簿。

## 功能特點

- **全域快捷鍵**: 按 `Right Alt + Space` 即可開始/停止錄音
- **多種轉錄引擎**: 支援本地 Whisper (免費) 和 Groq API (快速)
- **Whisper 模型選擇**: tiny/base/small/medium/large 根據硬體調整
- **智慧分割**: 自動將長音訊分割成片段處理
- **自動複製**: 轉錄完成後自動複製到剪貼簿
- **麥克風選擇**: 支援多麥克風裝置選擇
- **超時保護**: 可設定 1-120 分鐘的自動停止時間
- **加密儲存**: API 金鑰加密儲存在本地

## 系統需求

- **作業系統**: Windows 10/11
- **Python**: 3.10 ~ 3.13 (**不支援 3.14**)
- **麥克風**: 至少一個錄音裝置
- **網路**: Groq API 需要連網 (本地 Whisper 不需要)

> ⚠️ **重要提示**: 如果您使用 Python 3.14，PyAudio 無法正常安裝。請降級到 Python 3.13 或使用 conda 環境。

## 轉錄引擎比較

| 引擎 | 優點 | 缺點 | VRAM 需求 |
|------|------|------|-----------|
| **本地 Whisper (Tiny)** | 完全免費, 不需要網路 | 準確度較低 | 1GB |
| **本地 Whisper (Base)** | 免費, 平衡 | 需要硬體 | 1.5GB |
| **本地 Whisper (Small)** | 免費, 較好準確度 | 需要較好硬體 | 2GB |
| **本地 Whisper (Medium)** | 免費, 高準確度 | 需要 5GB+ VRAM | 5GB |
| **本地 Whisper (Large)** | 免費, 最高準確度 | 需要 10GB+ VRAM | 10GB |
| **Groq API** | 超快速, 使用 Large-v3 | 需要網路, 有額度限制 | 無 |

## 安裝步驟

### 1. 安裝 Python

確保您的系統已安裝 Python 3.10+。可從 [python.org](https://www.python.org/downloads/) 下載。

### 2. 下載專案

```bash
git clone https://github.com/yongsinfok/audio-summarize.git
cd audio-summarize
```

### 3. 安裝依賴套件

```bash
pip install -r requirements.txt
```

#### 關於 PyAudio 的安裝

**Python 3.14 使用者**: PyAudio 目前不支援 Python 3.14，請使用以下任一方式：

**方式一: 使用 Conda (推薦)**
```bash
# 安裝 Miniconda 或 Anaconda 後
conda create -n audio-summarize python=3.13
conda activate audio-summarize
conda install pyaudio
pip install -r requirements.txt
```

**方式二: 降級到 Python 3.13**
- 從 [python.org](https://www.python.org/downloads/) 下載 Python 3.13
- 使用 3.13 版本重新安裝

**方式三: 手動下載 wheel 檔案 (Python 3.10-3.13)**
1. 前往 [https://github.com/intxcc/pyaudio_portaudio/releases](https://github.com/intxcc/pyaudio_portaudio/releases)
2. 下載符合您 Python 版本的 wheel 檔案
3. 執行 `pip install <下載的檔案名稱.whl>`

### 4. 取得 Groq API 金鑰 (可選)

如果您想使用 Groq API 進行快速轉錄：

1. 前往 [Groq Console](https://console.groq.com/keys)
2. 註冊並取得 API 金鑰 (格式: `gsk_...`)
3. 在程式中點擊「API 金鑰」按鈕輸入

## 使用方法

### 啟動程式

```bash
python main.py
```

### 選擇轉錄引擎

1. **轉錄引擎**: 選擇本地 Whisper 或 Groq API
2. **Whisper 模型**: 僅在使用本地 Whisper 時顯示，根據您的顯卡 VRAM 選擇
   - 1GB VRAM → Tiny
   - 1.5GB VRAM → Base
   - 2GB VRAM → Small
   - 5GB VRAM → Medium
   - 10GB+ VRAM → Large
3. **麥克風**: 選擇要使用的麥克風裝置
4. **超時設定**: 拖動滑桿設定自動停止時間 (1-120 分鐘)
5. 點擊「儲存設定」儲存您的設定

### 錄音流程

1. 按下 `Right Alt + Space` 開始錄音
2. 視窗狀態會顯示「● 錄音中...」
3. 再次按下 `Right Alt + Space` 停止錄音
4. 程式會自動處理並複製結果到剪貼簿
5. 狀態顯示「✓ 已複製到剪貼簿」後即可貼上使用

### 注意事項

- 程式視窗可以最小化到工作列，不會影響全域快捷鍵運作
- 錄音檔案會暫存在 `~/.audio-summarize/temp/` 目錄下，處理完成後會自動刪除
- 首次使用本地 Whisper 時會下載模型，可能需要一些時間
- 建議在安靜環境下錄音以獲得最佳轉錄效果

## 快捷鍵

| 按鍵組合 | 功能 |
|----------|------|
| `Right Alt + Space` | 切換錄音開始/停止 |

## 檔案結構

```
audio-summarize/
├── main.py              # 程式進入點
├── requirements.txt     # 依賴套件
├── ui/                  # 使用者介面模組
├── core/                # 核心功能模組
│   ├── recorder.py      # 錄音管理
│   ├── transcriber.py   # 轉錄處理 (Whisper + Groq)
│   └── hotkey.py        # 全域快捷鍵
└── utils/               # 工具模組
    ├── config.py        # 設定管理
    └── clipboard.py     # 剪貼簿操作
```

## 技術說明

### 本地 Whisper

- **優點**: 完全免費, 隱私性好, 不需要網路
- **模型大小**: Tiny (39M) ~ Large (1550M) 參數
- **支援語言**: 多語言包括中文

### Groq API

- **優點**: 超快速推理, 使用 Whisper Large-v3-turbo 模型
- **免費額度**: 請參考 [Groq 定價](https://groq.com/)
- **API 限制**: 請遵守 Groq 使用條款

## 故障排除

### 麥克風無法使用

- 確認麥克風已正確連接
- 在 Windows 設定中確認麥克風權限已開啟
- 嘗試重新選擇麥克風裝置

### 轉錄失敗

- **本地 Whisper**: 確認有足夠的 VRAM/記憶體, 嘗試使用更小的模型
- **Groq API**: 確認網路連線正常, API 金鑰有效且有足夠額度
- 檢查錄音檔案是否正常

### Whisper 模型下載失敗

- 確認網路連線正常
- 模型會自動快取到 `~/.cache/whisper/` 或 `~/.cache/huggingface/`

### 快捷鍵無效

- 確認程式正在執行中
- 檢查是否有其他程式佔用了相同的快捷鍵
- 嘗試以管理員權限執行程式

## 授權

MIT License

## 問題回報

如遇到問題或有建議，請開啟 Issue 回報。
