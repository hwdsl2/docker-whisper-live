[English](README.md) | [简体中文](README-zh.md) | [繁體中文](README-zh-Hant.md) | [Русский](README-ru.md)

# WhisperLive 即時語音轉文字 Docker 映像

[![建置狀態](https://github.com/hwdsl2/docker-whisper-live/actions/workflows/main.yml/badge.svg)](https://github.com/hwdsl2/docker-whisper-live/actions/workflows/main.yml) &nbsp;[![Docker Pulls](https://raw.githubusercontent.com/hwdsl2/badges/main/img/docker-pulls-whisper-live-server.svg)](https://hub.docker.com/r/hwdsl2/whisper-live-server) &nbsp;[![License: MIT](docs/images/license.svg)](https://opensource.org/licenses/MIT) &nbsp;[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://vpnsetup.net/whisper-live-notebook)

[Docker AI Stack](https://github.com/hwdsl2/docker-ai-stack/blob/main/README-zh-Hant.md) 的一部分 ─ 一條命令部署完整的自託管 AI 技術棧。

使用 [faster-whisper](https://github.com/SYSTRAN/faster-whisper) 在 Docker 容器中執行 [WhisperLive](https://github.com/collabora/WhisperLive) 即時語音轉文字伺服器。提供用於即時音訊轉錄的 WebSocket 串流，以及用於檔案轉錄的 OpenAI 相容 REST API。基於 Debian (python:3.12-slim)，簡單、私密、可自架。

**功能特色：**

- 即時 WebSocket 串流 — 以近乎即時的方式轉錄即時麥克風音訊或音訊串流
- OpenAI 相容 REST API — 提供 `POST /v1/audio/transcriptions` 檔案轉錄端點；任何呼叫 OpenAI Whisper API 的應用程式只需修改一行設定即可切換
- 支援所有 Whisper 模型：`tiny`、`base`、`small`、`medium`、`large-v3`、`large-v3-turbo` 等
- 語音活動偵測（VAD）— 自動略過靜音段，實現更快、更乾淨的轉錄
- 透過輔助腳本 (`whisper_live_manage`) 管理模型
- 音訊資料保留在您的伺服器上，不傳送給第三方
- NVIDIA GPU (CUDA) 加速推論（使用 `:cuda` 映像標籤）
- 離線/隔離網路模式 — 使用預先快取的模型，無需網際網路存取 (`WHISPERLIVE_LOCAL_ONLY`)
- 透過 [GitHub Actions](https://github.com/hwdsl2/docker-whisper-live/actions/workflows/main.yml) 自動建置和發佈
- 透過 Docker 資料卷持久化模型快取
- 多架構支援：`linux/amd64`、`linux/arm64`

**另提供：**

- 線上試用：[在 Colab 中開啟](https://vpnsetup.net/whisper-live-notebook)——無需 Docker 或安裝
- AI/音訊：[Whisper（批次 STT）](https://github.com/hwdsl2/docker-whisper/blob/main/README-zh-Hant.md)、[Kokoro (TTS)](https://github.com/hwdsl2/docker-kokoro/blob/main/README-zh-Hant.md)、[Embeddings](https://github.com/hwdsl2/docker-embeddings/blob/main/README-zh-Hant.md)、[LiteLLM](https://github.com/hwdsl2/docker-litellm/blob/main/README-zh-Hant.md)、[Ollama (LLM)](https://github.com/hwdsl2/docker-ollama/blob/main/README-zh-Hant.md)、[Docling](https://github.com/hwdsl2/docker-docling/blob/main/README-zh-Hant.md)
- VPN：[WireGuard](https://github.com/hwdsl2/docker-wireguard/blob/main/README-zh-Hant.md)、[OpenVPN](https://github.com/hwdsl2/docker-openvpn/blob/main/README-zh-Hant.md)、[IPsec VPN](https://github.com/hwdsl2/docker-ipsec-vpn-server/blob/master/README-zh-Hant.md)、[Headscale](https://github.com/hwdsl2/docker-headscale/blob/main/README-zh-Hant.md)
- 工具：[MCP Gateway](https://github.com/hwdsl2/docker-mcp-gateway/blob/main/README-zh-Hant.md)

**提示：** WhisperLive、Kokoro、Embeddings、LiteLLM、Ollama、Docling 和 MCP 閘道可以[搭配使用](#與其他-ai-服務搭配使用)，在您自己的伺服器上建立完整的自託管 AI 系統。

## 社群

- 📬 [訂閱專案更新](https://selfhostedstack.beehiiv.com/subscribe?utm_campaign=ai-zh-hant)（每月 1–2 封郵件）——獲取免費的 AI 和 VPN 部署指南（PDF，英文）
- 💬 加入 [r/selfhostedstack](https://www.reddit.com/r/selfhostedstack/) 社群，參與討論與專案展示
- ⭐ 如果你覺得本專案有用，請為儲存庫加星——這能幫助更多人發現它。

## WhisperLive 與 Whisper 的選擇

| | [docker-whisper](https://github.com/hwdsl2/docker-whisper/blob/main/README-zh-Hant.md) | **docker-whisper-live** |
|---|---|---|
| **使用情境** | 轉錄完整音訊檔案 | 即時麥克風/音訊串流 |
| **協定** | HTTP REST | WebSocket（串流）+ HTTP REST |
| **延遲** | 完整檔案處理後回傳結果 | 近即時，逐字輸出 |
| **適合** | 會議錄音、上傳的音訊檔案 | 瀏覽器擷取、RTSP 串流、即時字幕 |
| **映像大小** | ~190 MB（`:cuda` 約 3.1 GB） | ~750 MB（`:cuda` 約 4.5 GB） |

## 快速開始

使用以下指令啟動 WhisperLive 伺服器：

```bash
docker run \
    --name whisper-live \
    --restart=always \
    -v whisper-live-data:/var/lib/whisper-live \
    -p 9090:9090 \
    -p 8000:8000 \
    -d hwdsl2/whisper-live-server
```

<details>
<summary><strong>GPU 快速開始（NVIDIA CUDA）</strong></summary>

如果您有 NVIDIA GPU，可使用 `:cuda` 映像進行硬體加速推論：

```bash
docker run \
    --name whisper-live \
    --restart=always \
    --gpus=all \
    -v whisper-live-data:/var/lib/whisper-live \
    -p 9090:9090 \
    -p 8000:8000 \
    -d hwdsl2/whisper-live-server:cuda
```

**需求：** NVIDIA GPU、[NVIDIA 驅動程式](https://www.nvidia.com/en-us/drivers/) 535+，以及主機上已安裝 [NVIDIA Container Toolkit](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/latest/install-guide.html)。`:cuda` 映像僅支援 `linux/amd64`。

</details>

**重要：** 此映像執行預設 `base` 模型需要至少 700 MB 可用記憶體。記憶體為 512 MB 或更少的系統不受支援。

**注意：** 如需面向網際網路的部署，**強烈建議**使用[反向代理](#使用反向代理)來新增 HTTPS。此時，還應將上述 `docker run` 指令中的 `-p 9090:9090 -p 8000:8000` 替換為 `-p 127.0.0.1:9090:9090 -p 127.0.0.1:8000:8000`，以防止從外部直接存取未加密的連接埠。

首次用戶端連線時，Whisper `base` 模型（約 145 MB）將自動下載並快取。查看記錄確認伺服器已就緒：

```bash
docker logs whisper-live
```

看到 "WhisperLive real-time transcription server is ready" 後：

**連接即時 WebSocket 用戶端：**

```
ws://您的伺服器IP:9090
```

**或透過 REST API 轉錄檔案：**

```bash
curl http://您的伺服器IP:8000/v1/audio/transcriptions \
    -F file=@audio.mp3 \
    -F model=whisper-1
```

**回應：**
```json
{"text": "轉錄的文字內容顯示在這裡。"}
```

**提示：** 需要範例音訊檔案測試 REST API？可以使用來自 [Azure Samples](https://github.com/Azure-Samples/cognitive-services-speech-sdk) 儲存庫的英語語音範例（WAV 格式，MIT 授權）：

```bash
curl -L -o sample_speech.wav \
    "https://github.com/Azure-Samples/cognitive-services-speech-sdk/raw/master/sampledata/audiofiles/katiesteve.wav"

curl http://您的伺服器IP:8000/v1/audio/transcriptions \
    -F file=@sample_speech.wav \
    -F model=whisper-1
```

## 系統需求

- 已安裝 Docker 的 Linux 伺服器（本地或雲端）
- 支援的架構：`amd64`（x86_64）、`arm64`（例如 Raspberry Pi 4/5、AWS Graviton）
- 最低記憶體：預設 `base` 模型約需 700 MB 可用記憶體（請參閱[模型清單](#切換模型)）
- 首次啟動需要存取網際網路以下載模型（之後模型將快取在本地）。使用預先快取的模型並設定 `WHISPERLIVE_LOCAL_ONLY=true` 時不需要網路存取。

**GPU 加速（`:cuda` 映像）需求：**

- 支援 CUDA 的 NVIDIA GPU（運算能力 6.0+）
- 主機已安裝 [NVIDIA 驅動程式](https://www.nvidia.com/en-us/drivers/) 535 或更高版本
- 已安裝 [NVIDIA Container Toolkit](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/latest/install-guide.html)
- `:cuda` 映像僅支援 `linux/amd64`

如需面向公網部署，請參閱[使用反向代理](#使用反向代理)以啟用 HTTPS。

## 下載

從 [Docker Hub](https://hub.docker.com/r/hwdsl2/whisper-live-server/) 取得可信任的建置版本：

```bash
docker pull hwdsl2/whisper-live-server
```

如需 NVIDIA GPU 加速，請拉取 `:cuda` 標籤：

```bash
docker pull hwdsl2/whisper-live-server:cuda
```

也可從 [Quay.io](https://quay.io/repository/hwdsl2/whisper-live-server) 下載：

```bash
docker pull quay.io/hwdsl2/whisper-live-server
docker image tag quay.io/hwdsl2/whisper-live-server hwdsl2/whisper-live-server
```

支援平台：`linux/amd64` 和 `linux/arm64`。`:cuda` 標籤僅支援 `linux/amd64`。

## 環境變數

所有變數均為選填。如未設定，將自動使用安全的預設值。

此 Docker 映像使用以下變數，可在 `env` 檔案中宣告（參見[範例](whisper-live.env.example)）：

| 變數 | 說明 | 預設值 |
|---|---|---|
| `WHISPERLIVE_MODEL` | 使用的 Whisper 模型。請參閱[模型清單](#切換模型)。 | `base` |
| `WHISPERLIVE_LANGUAGE` | 預設轉錄語言。使用 BCP-47 語言代碼（如 `zh`、`en`、`ja`）或 `auto` 自動偵測。 | `auto` |
| `WHISPERLIVE_PORT` | 即時串流用戶端的 WebSocket 連接埠（1–65535）。 | `9090` |
| `WHISPERLIVE_REST_PORT` | OpenAI 相容 REST API 的 HTTP 連接埠（1–65535）。 | `8000` |
| `WHISPERLIVE_MAX_CLIENTS` | 最大同時 WebSocket 用戶端連線數。 | `4` |
| `WHISPERLIVE_MAX_CONNECTION_TIME` | WebSocket 最大連線時長（秒）。超過此時長的用戶端將被自動斷線。 | `600` |
| `WHISPERLIVE_USE_VAD` | 啟用語音活動偵測。設為 `true` 時自動偵測並略過靜音段。設為 `false` 持續處理所有音訊。 | `true` |
| `WHISPERLIVE_THREADS` | 推理使用的 CPU 執行緒數。設為實體核心數可獲得最佳延遲。 | `2` |
| `WHISPERLIVE_LOG_LEVEL` | 記錄層級：`DEBUG`、`INFO`、`WARNING`、`ERROR`、`CRITICAL`。 | `INFO` |
| `WHISPERLIVE_LOCAL_ONLY` | 設為任意非空值（如 `true`）時，禁止所有 HuggingFace 模型下載。適用於預先快取模型的離線或隔離網路部署。 | *（未設定）* |

**注意：** 在 `env` 檔案中，值可用單引號括起，例如 `VAR='value'`。`=` 兩側不要有空格。如更改 `WHISPERLIVE_PORT` 或 `WHISPERLIVE_REST_PORT`，請相應更新 `docker run` 指令中的 `-p` 參數。

使用 `env` 檔案的範例：

```bash
cp whisper-live.env.example whisper-live.env
# 編輯 whisper-live.env 設定您的選項，然後：
docker run \
    --name whisper-live \
    --restart=always \
    -v whisper-live-data:/var/lib/whisper-live \
    -v ./whisper-live.env:/whisper-live.env:ro \
    -p 9090:9090 \
    -p 8000:8000 \
    -d hwdsl2/whisper-live-server
```

`env` 檔案以繫結掛載方式傳入容器，每次重新啟動時自動生效，無需重建容器。

<details>
<summary>也可透過 <code>--env-file</code> 傳入</summary>

```bash
docker run \
    --name whisper-live \
    --restart=always \
    -v whisper-live-data:/var/lib/whisper-live \
    -p 9090:9090 \
    -p 8000:8000 \
    --env-file=whisper-live.env \
    -d hwdsl2/whisper-live-server
```

</details>

## 使用 docker-compose

```bash
cp whisper-live.env.example whisper-live.env
# 依需求編輯 whisper-live.env，然後：
docker compose up -d
docker logs whisper-live
```

示例 `docker-compose.yml`（已包含在專案中）：

```yaml
services:
  whisper-live:
    image: hwdsl2/whisper-live-server
    container_name: whisper-live
    restart: always
    ports:
      - "9090:9090/tcp"  # WebSocket — 如使用主機反向代理，改為 "127.0.0.1:9090:9090/tcp"
      - "8000:8000/tcp"  # REST API  — 如使用主機反向代理，改為 "127.0.0.1:8000:8000/tcp"
    volumes:
      - whisper-live-data:/var/lib/whisper-live
      - ./whisper-live.env:/whisper-live.env:ro

volumes:
  whisper-live-data:
    name: whisper-live-data
```

**注意：** 如需面向公網部署，強烈建議使用[反向代理](#使用反向代理)啟用 HTTPS。此時請將 `docker-compose.yml` 中的連接埠改為其 `127.0.0.1:` 形式。

<details>
<summary><strong>使用 docker-compose 部署 GPU（NVIDIA CUDA）</strong></summary>

專案提供了單獨的 `docker-compose.cuda.yml` 用於 GPU 部署：

```bash
cp whisper-live.env.example whisper-live.env
# 依需求編輯 whisper-live.env，然後：
docker compose -f docker-compose.cuda.yml up -d
docker logs whisper-live
```

示例 `docker-compose.cuda.yml`（已包含在專案中）：

```yaml
services:
  whisper-live:
    image: hwdsl2/whisper-live-server:cuda
    container_name: whisper-live
    restart: always
    ports:
      - "9090:9090/tcp"  # WebSocket — 如使用主機反向代理，改為 "127.0.0.1:9090:9090/tcp"
      - "8000:8000/tcp"  # REST API  — 如使用主機反向代理，改為 "127.0.0.1:8000:8000/tcp"
    volumes:
      - whisper-live-data:/var/lib/whisper-live
      - ./whisper-live.env:/whisper-live.env:ro
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: 1
              capabilities: [gpu]

volumes:
  whisper-live-data:
    name: whisper-live-data
```

</details>

## WebSocket 串流

`9090` 連接埠的 WebSocket 端點支援即時音訊串流轉錄。用戶端傳送原始 PCM 音訊區塊，伺服器在解碼時回傳轉錄段落。

### 協議

連線後，首先傳送 JSON 設定訊息：

```json
{
  "uid": "unique-client-id",
  "language": "zh",
  "model": "base",
  "use_vad": true
}
```

然後以二進位 WebSocket 幀形式串流傳輸 16 kHz 取樣率的 16 位元 PCM 原始音訊。伺服器回傳 JSON 轉錄事件：

```json
{"uid": "unique-client-id", "segments": [{"text": "您好，最近怎麼樣？", "start": 0.0, "end": 2.4, "completed": true}]}
```

### Python 用戶端範例

```python
from whisper_live.client import TranscriptionClient

client = TranscriptionClient(
    "您的伺服器IP",
    9090,
    lang="zh",
    translate=False,
    model="base",
    use_vad=True,
)

# 轉錄檔案
client("audio.mp3")

# 或從麥克風轉錄
# client()
```

安裝用戶端函式庫：

```bash
pip install whisper-live
```

### 瀏覽器用戶端範例

```javascript
const ws = new WebSocket("ws://您的伺服器IP:9090");

ws.onopen = () => {
  // 傳送設定資訊
  ws.send(JSON.stringify({
    uid: "browser-client-1",
    language: "zh",
    model: "base",
    use_vad: true,
  }));
};

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  if (data.segments) {
    data.segments.forEach(seg => console.log(seg.text));
  }
};

// 以 ArrayBuffer 形式傳送音訊區塊（16 位元 PCM，16 kHz）
// ws.send(audioBuffer);
```

## REST API 參考

`8000` 連接埠的 REST API 與 [OpenAI 音訊轉錄端點](https://developers.openai.com/api/reference/resources/audio/subresources/transcriptions/methods/create)完全相容。任何已呼叫 `https://api.openai.com/v1/audio/transcriptions` 的應用程式，只需設定以下環境變數即可切換到自架伺服器：

```
OPENAI_BASE_URL=http://您的伺服器IP:8000
```

### 轉錄音訊

```
POST /v1/audio/transcriptions
Content-Type: multipart/form-data
```

**參數：**

| 參數 | 類型 | 必填 | 說明 |
|---|---|---|---|
| `file` | 檔案 | ✅ | 音訊檔案。支援格式：`mp3`、`mp4`、`m4a`、`wav`、`webm`、`ogg`、`flac` 及 ffmpeg 支援的所有格式。 |
| `model` | 字串 | ✅ | 傳入 `whisper-1`（值被接受，但始終使用當前活躍模型）。 |
| `language` | 字串 | — | BCP-47 語言代碼（如 `zh`、`en`、`ja`）。如不填，則自動偵測語言。 |

**範例：**

```bash
curl http://您的伺服器IP:8000/v1/audio/transcriptions \
    -F file=@meeting.m4a \
    -F model=whisper-1 \
    -F language=zh
```

**回應：**
```json
{"text": "轉錄的文字內容顯示在這裡。"}
```

### 互動式 API 文件

互動式 Swagger UI 可在以下位址存取：

```
http://您的伺服器IP:8000/docs
```

## 持久化資料

所有伺服器資料儲存在 Docker 資料卷（容器內的 `/var/lib/whisper-live`）中：

```
/var/lib/whisper-live/
├── models--Systran--faster-whisper-*/   # 快取的 Whisper 模型檔案（從 HuggingFace 下載）
├── .ws_port              # 當前 WebSocket 連接埠（供 whisper_live_manage 使用）
├── .rest_port            # 當前 REST API 連接埠（供 whisper_live_manage 使用）
├── .model                # 當前模型名稱（供 whisper_live_manage 使用）
└── .server_addr          # 快取的伺服器 IP（供 whisper_live_manage 使用）
```

請備份 Docker 資料卷以保留已下載的模型。模型體積較大（145 MB – 3 GB），首次用戶端連線時下載可能需要數分鐘；保留資料卷可避免在重新建立容器時重複下載。

**提示：** `/var/lib/whisper-live` 資料卷與 `docker-whisper` 的 `/var/lib/whisper` 資料卷使用相同的 HuggingFace 快取配置。如果已透過 `docker-whisper` 下載了模型，可繫結掛載相同的資料卷目錄以避免重複下載。

## 管理伺服器

在執行中的容器內使用 `whisper_live_manage` 來查看和管理伺服器。

```bash
docker exec whisper-live whisper_live_manage --showinfo
docker exec whisper-live whisper_live_manage --listmodels
docker exec whisper-live whisper_live_manage --downloadmodel large-v3-turbo
```

## 切換模型

1. *（選填但建議）* 預先下載新模型：
   ```bash
   docker exec whisper-live whisper_live_manage --downloadmodel large-v3-turbo
   ```
2. 在 `whisper-live.env` 檔案中更新 `WHISPERLIVE_MODEL`。
3. 重新啟動容器：
   ```bash
   docker restart whisper-live
   ```

**可用模型：**

| 模型 | 磁碟占用 | 記憶體（約） | 說明 |
|---|---|---|---|
| `tiny` | ~75 MB | ~250 MB | 最快；精確度較低 |
| `tiny.en` | ~75 MB | ~250 MB | 僅英語 |
| `base` | ~145 MB | ~700 MB | 良好平衡 — **預設** |
| `base.en` | ~145 MB | ~700 MB | 僅英語 |
| `small` | ~465 MB | ~1.5 GB | 更高精確度 |
| `small.en` | ~465 MB | ~1.5 GB | 僅英語 |
| `medium` | ~1.5 GB | ~5 GB | 高精確度 |
| `medium.en` | ~1.5 GB | ~5 GB | 僅英語 |
| `large-v1` | ~3 GB | ~10 GB | 舊版大型模型 |
| `large-v2` | ~3 GB | ~10 GB | 非常高精確度 |
| `large-v3` | ~3 GB | ~10 GB | 最高精確度 |
| `large-v3-turbo` | ~1.6 GB | ~6 GB | 高速 + 高精確度 ⭐ |
| `turbo` | ~1.6 GB | ~6 GB | `large-v3-turbo` 的別名 |

> **提示：** `large-v3-turbo` 的精確度接近 `large-v3`，但資源消耗約為其一半。對於大多數正式部署，推薦從 `base` 升級到此模型。

記憶體數值為近似值，基於 INT8 量化（預設）。模型快取於 `/var/lib/whisper-live` Docker 資料卷中，僅需下載一次。

## 保護你的伺服器

如果你的 WhisperLive 伺服器可從公用網際網路存取 —— 即使只是短暫可達 —— 也請至少採取以下保護措施。WhisperLive 對 CPU/GPU 資源消耗較大，未做防護的介面可能被濫用，浪費你的運算資源。

**1. 在代理處新增身分驗證。** 伺服器沒有內建 API 金鑰。對於面向公網的部署，請在反向代理層新增 Bearer 權杖或基本身分驗證——請參閱[使用反向代理](#使用反向代理)章節中的「在代理層新增身分驗證」展開內容。將 WebSocket 連接埠（`9090`）繫結到 `127.0.0.1`，使其只能透過代理存取。

**2. 在反向代理後方時繫結到 localhost。** 將 `-p 9090:9090 -p 8000:8000` 替換為 `-p 127.0.0.1:9090:9090 -p 127.0.0.1:8000:8000`（或在 `docker-compose.yml` 中將兩個連接埠對應改為各自的 `127.0.0.1:` 等效形式），使未加密連接埠無法從主機外部直接存取。

**3. 在代理處限制上傳大小。** 音訊檔案可能很大；設定反向代理以拒絕過大的上傳（例如 nginx `client_max_body_size 100M;`），從而限制單一請求佔用的磁碟和記憶體。

**4. 注意日誌等級。** `WHISPERLIVE_LOG_LEVEL=DEBUG` 可能會將轉錄文字寫入日誌。在共用系統上請保持 `INFO` 或更高等級。

**5. 在代理處限制 WebSocket 來源。** 來自不受信任瀏覽器來源的 WebSocket 連線可在反向代理處被攔截。對於 nginx，在升級連線前檢查 `$http_origin`；對於 Caddy，使用 `header` 指令驗證 `Origin` 標頭。

**6. 考慮限流。** 在伺服器前部署限流（如 nginx `limit_req_zone`、Caddy `rate_limit`），限制每個用戶端 IP 的並行轉錄請求數。

## 使用反向代理

可使用以下位址從反向代理存取容器：

- **`whisper-live:9090`** / **`whisper-live:8000`** — 如果反向代理以容器形式執行在**相同 Docker 網路**中。
- **`127.0.0.1:9090`** / **`127.0.0.1:8000`** — 如果反向代理執行在**主機上**且連接埠已發佈。

**使用 [Caddy](https://caddyserver.com/docs/)（[Docker 映像](https://hub.docker.com/_/caddy)）的範例**（自動 TLS，同一 Docker 網路中的 WebSocket 代理）：

`Caddyfile`：
```
whisper-live.example.com {
  # WebSocket 串流（wss://）
  handle /ws* {
    reverse_proxy whisper-live:9090
  }
  # REST API（https://）
  reverse_proxy whisper-live:8000
}
```

**使用 nginx 的範例**（反向代理執行在主機上）：

```nginx
server {
    listen 443 ssl;
    server_name whisper-live.example.com;

    ssl_certificate     /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;

    # REST API
    location /v1/ {
        proxy_pass         http://127.0.0.1:8000;
        proxy_set_header   Host $host;
        proxy_set_header   X-Real-IP $remote_addr;
        proxy_set_header   X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header   X-Forwarded-Proto $scheme;
        proxy_read_timeout 300s;
    }

    # WebSocket 串流
    location / {
        proxy_pass         http://127.0.0.1:9090;
        proxy_http_version 1.1;
        proxy_set_header   Upgrade $http_upgrade;
        proxy_set_header   Connection "upgrade";
        proxy_set_header   Host $host;
        proxy_read_timeout 600s;
    }
}
```

> **重要：** WebSocket 代理需要 `proxy_http_version 1.1` 以及 `Upgrade`/`Connection` 請求標頭。若缺少這些設定，即時串流將無法透過 nginx 正常運作。

<details>
<summary><strong>在代理層新增身份驗證</strong></summary>

伺服器本身不強制要求 API 金鑰驗證。對於面向網際網路的部署，可以在反向代理層新增 Bearer 令牌或基本身份驗證。使用 Caddy 的範例（`basicauth` 保護 REST API）：

```
whisper-live.example.com {
  handle /v1/* {
    basicauth {
      user $2a$14$<bcrypt-hash-of-password>
    }
    reverse_proxy whisper-live:8000
  }
  handle /ws* {
    reverse_proxy whisper-live:9090
  }
  reverse_proxy whisper-live:8000
}
```

使用 nginx 的範例（在 REST API location 上啟用 `auth_basic`）：

```nginx
location /v1/ {
    auth_basic           "WhisperLive";
    auth_basic_user_file /etc/nginx/.htpasswd;
    proxy_pass           http://127.0.0.1:8000;
    proxy_set_header     Host $host;
    proxy_read_timeout   300s;
}
```

WebSocket 端點（`/`，連接埠 `9090`）不支援 HTTP 身份驗證標頭；請將其連接埠繫結至 `127.0.0.1` 並透過反向代理進行存取控制來保護它。

</details>

## 更新 Docker 映像

```bash
docker pull hwdsl2/whisper-live-server
docker rm -f whisper-live
# 然後使用相同的資料卷和連接埠重新執行快速開始中的 docker run 指令。
```

您下載的模型將保留在 `whisper-live-data` 資料卷中。

## 與其他 AI 服務搭配使用

WhisperLive（即時 STT）、Embeddings、LiteLLM、Kokoro (TTS)、Ollama (LLM)、Docling 和 MCP 閘道 映像可以組合使用，在您自己的伺服器上建立完整的自託管 AI 系統——從即時語音輸入/輸出到檢索增強生成（RAG）。WhisperLive、Kokoro 和 Embeddings 完全在本地端執行。Ollama 在本地端執行所有 LLM 推論，無需向第三方傳送資料。如果您將 LiteLLM 設定為使用外部提供商（例如 OpenAI、Anthropic），您的資料將被傳送至這些提供商處理。

| 服務 | 功能 | 預設連接埠 |
|---|---|---|
| **[WhisperLive（即時 STT）](https://github.com/hwdsl2/docker-whisper-live/blob/main/README-zh-Hant.md)** | 即時 WebSocket 串流轉錄 | `9090`（WS）、`8000`（REST） |
| **[Embeddings](https://github.com/hwdsl2/docker-embeddings/blob/main/README-zh-Hant.md)** | 將文字轉換為向量，用於語意搜尋和 RAG | `8000` |
| **[LiteLLM](https://github.com/hwdsl2/docker-litellm/blob/main/README-zh-Hant.md)** | AI 閘道——將請求路由至 OpenAI、Anthropic、Ollama 及 100+ 其他提供商 | `4000` |
| **[Kokoro (TTS)](https://github.com/hwdsl2/docker-kokoro/blob/main/README-zh-Hant.md)** | 將文字轉換為自然語音 | `8880` |
| **[Ollama (LLM)](https://github.com/hwdsl2/docker-ollama/blob/main/README-zh-Hant.md)** | 執行本地 LLM 模型（llama3、qwen、mistral 等） | `11434` |
| **[MCP 閘道](https://github.com/hwdsl2/docker-mcp-gateway/blob/main/README-zh-Hant.md)** | 將 AI 服務作為 MCP 工具提供給 AI 助手（Claude、Cursor 等） | `3000` |
| **[Docling](https://github.com/hwdsl2/docker-docling/blob/main/README-zh-Hant.md)** | 將文件（PDF、DOCX 等）轉換為結構化文字/Markdown | `5001` |

**另請參閱：[Docker AI Stack](https://github.com/hwdsl2/docker-ai-stack)** — 一條命令即可部署完整技術堆疊，提供現成的設定和流水線範例。

## 技術細節

- 基礎映像：`python:3.12-slim`（Debian）
- 執行環境：Python 3（虛擬環境位於 `/opt/venv`）
- STT 引擎：[WhisperLive](https://github.com/collabora/WhisperLive) + [faster-whisper](https://github.com/SYSTRAN/faster-whisper) + CTranslate2（CPU 預設 INT8，CUDA 預設 FP16）
- VAD：透過 PyTorch（CPU 或 CUDA，自動偵測）使用 [Silero VAD](https://github.com/snakers4/silero-vad)
- WebSocket 伺服器：Python `websockets` 函式庫
- REST API 框架：[FastAPI](https://fastapi.tiangolo.com/) + [Uvicorn](https://www.uvicorn.org/)
- 資料目錄：`/var/lib/whisper-live`（Docker 資料卷）
- 模型儲存：HuggingFace Hub 格式，存於資料卷中——下載一次，重新啟動後複用

## 授權條款

**注意：** 預建映像中包含的軟體元件（如 WhisperLive、faster-whisper、PyTorch 及其相依套件）均受各自版權持有者所選授權條款約束。使用預建映像時，使用者有責任確保其使用方式符合映像內所有軟體的相關授權條款要求。

版權所有 (C) 2026 Lin Song   
本作品採用 [MIT 授權條款](https://opensource.org/licenses/MIT)授權。

**WhisperLive** 版權歸 Vineet Suryan、Collabora Ltd. 所有，依據 [MIT 授權條款](https://github.com/collabora/WhisperLive/blob/main/LICENSE)散布。

**faster-whisper** 版權歸 SYSTRAN 所有，依據 [MIT 授權條款](https://github.com/SYSTRAN/faster-whisper/blob/master/LICENSE)散布。

本專案是獨立的 Docker 封裝，與 OpenAI、Collabora 或 SYSTRAN 無關聯，未獲其背書或贊助。