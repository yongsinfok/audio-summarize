# 語音轉文字工具 🎤

一個 Windows 桌面應用程式，透過全域快捷鍵快速錄音並轉換為整理好的文字，自動複製到剪貼簿。

## 功能特點

- **全域快捷鍵**: 按 `Right Alt + Space` 即可開始/停止錄音
- **自動轉錄**: 使用 OpenAI Whisper (whisper-1) 進行語音轉文字
- **智能潤飾**: 使用 GPT-4o-mini 去除贅字並整理語句
- **自動複製**: 轉錄完成後自動複製到剪貼簿
- **麥克風選擇**: 支援多麥克風裝置選擇
- **超時保護**: 可設定 1-120 分鐘的自動停止時間
- **加密儲存**: API 金鑰加密儲存在本地

## 系統需求

- **作業系統**: Windows 10/11
- **Python**: 3.10 或更高版本
- **麥克風**: 至少一個錄音裝置
- **網路**: 需要連網以呼叫 OpenAI API

## 安裝步驟

### 1. 安裝 Python

確保您的系統已安裝 Python 3.10+。可從 [python.org](https://www.python.org/downloads/) 下載。

### 2. 下載專案

```bash
git clone <repository-url>
cd audio-summarize
```

### 3. 安裝依賴套件

```bash
pip install -r requirements.txt
```

#### 關於 PyAudio 的安裝

如果在安裝 `pyaudio` 時遇到問題，請嘗試以下方式：

**方式一: 使用預編譯的 wheel 檔案**
```bash
pip install pipwin
pipwin install pyaudio
```

**方式二: 手動下載 wheel 檔案**
1. 前往 [https://www.lfd.uci.edu/~gohlke/pythonlibs/#pyaudio](https://www.lfd.uci.edu/~gohlke/pythonlibs/#pyaudio)
2. 下載符合您 Python 版本的 wheel 檔案 (如 `PyAudio‑0.2.14‑cp311‑cp311‑win_amd64.whl`)
3. 執行 `pip install <下載的檔案名稱.whl>`

### 4. 取得 OpenAI API 金鑰

1. 前往 [OpenAI Platform](https://platform.openai.com/api-keys)
2. 登入並建立新的 API 金鑰
3. 複製金鑰 (以 `sk-` 開頭)

## 使用方法

### 啟動程式

```bash
python main.py
```

首次啟動時，程式會要求您輸入 OpenAI API 金鑰。

### 設定麥克風與超時時間

1. **麥克風選擇**: 在下拉選單中選擇要使用的麥克風
2. **超時設定**: 拖動滑桿設定自動停止時間 (1-120 分鐘)
3. 點擊「儲存設定」儲存您的設定

### 錄音流程

1. 按下 `Right Alt + Space` 開始錄音
2. 視窗狀態會顯示「● 錄音中...」
3. 再次按下 `Right Alt + Space` 停止錄音
4. 程式會自動處理並複製結果到剪貼簿
5. 狀態顯示「✓ 已複製到剪貼簿」後即可貼上使用

### 注意事項

- 程式視窗可以最小化到工作列，不會影響全域快捷鍵運作
- 錄音檔案會暫存在 `~/.audio-summarize/temp/` 目錄下，處理完成後會自動刪除
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
│   ├── transcriber.py   # 轉錄處理
│   └── hotkey.py        # 全域快捷鍵
└── utils/               # 工具模組
    ├── config.py        # 設定管理
    └── clipboard.py     # 剪貼簿操作
```

## 故障排除

### 麥克風無法使用

- 確認麥克風已正確連接
- 在 Windows 設定中確認麥克風權限已開啟
- 嘗試重新選擇麥克風裝置

### 轉錄失敗

- 確認網路連線正常
- 確認 OpenAI API 金鑰有效且有足夠額度
- 檢查錄音檔案是否過大 (建議單次錄音不超過 25MB)

### 快捷鍵無效

- 確認程式正在執行中
- 檢查是否有其他程式佔用了相同的快捷鍵
- 嘗試以管理員權限執行程式

## 授權

MIT License

## 問題回報

如遇到問題或有建議，請開啟 Issue 回報。
