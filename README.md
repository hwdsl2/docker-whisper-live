[English](README.md) | [简体中文](README-zh.md) | [繁體中文](README-zh-Hant.md) | [Русский](README-ru.md)

# WhisperLive Real-Time Speech-to-Text on Docker

[![Build Status](https://github.com/hwdsl2/docker-whisper-live/actions/workflows/main.yml/badge.svg)](https://github.com/hwdsl2/docker-whisper-live/actions/workflows/main.yml) &nbsp;[![Docker Pulls](https://raw.githubusercontent.com/hwdsl2/badges/main/img/docker-pulls-whisper-live-server.svg)](https://hub.docker.com/r/hwdsl2/whisper-live-server) &nbsp;[![License: MIT](docs/images/license.svg)](https://opensource.org/licenses/MIT) &nbsp;[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://vpnsetup.net/whisper-live-notebook)

Part of the [Docker AI Stack](https://github.com/hwdsl2/docker-ai-stack) — deploy a complete self-hosted AI stack with a single command.

Docker image to run a [WhisperLive](https://github.com/collabora/WhisperLive) real-time speech-to-text server, powered by [faster-whisper](https://github.com/SYSTRAN/faster-whisper). Provides WebSocket streaming for live audio transcription and an OpenAI-compatible REST API for file transcription. Based on Debian (python:3.12-slim). Designed to be simple, private, and self-hosted.

**Features:**

- Real-time WebSocket streaming — transcribe live microphone audio or audio streams with near-instant results
- OpenAI-compatible REST API — `POST /v1/audio/transcriptions` for file transcription; any app using the OpenAI Whisper API switches with a one-line change
- Supports all Whisper models: `tiny`, `base`, `small`, `medium`, `large-v3`, `large-v3-turbo` and more
- Voice Activity Detection (VAD) — automatically skips silence for faster, cleaner transcription
- Model management via a helper script (`whisper_live_manage`)
- Audio stays on your server — no data sent to third parties
- NVIDIA GPU (CUDA) acceleration for faster inference (`:cuda` image tag)
- Offline/air-gapped mode — run without internet access using pre-cached models (`WHISPERLIVE_LOCAL_ONLY`)
- Automatically built and published via [GitHub Actions](https://github.com/hwdsl2/docker-whisper-live/actions/workflows/main.yml)
- Persistent model cache via a Docker volume
- Multi-arch: `linux/amd64`, `linux/arm64`

**Also available:**

- Try it online: [Open in Colab](https://vpnsetup.net/whisper-live-notebook) — no Docker or installation required
- AI/Audio: [Whisper (batch STT)](https://github.com/hwdsl2/docker-whisper), [Kokoro (TTS)](https://github.com/hwdsl2/docker-kokoro), [Embeddings](https://github.com/hwdsl2/docker-embeddings), [LiteLLM](https://github.com/hwdsl2/docker-litellm), [Ollama (LLM)](https://github.com/hwdsl2/docker-ollama), [Docling](https://github.com/hwdsl2/docker-docling)
- VPN: [WireGuard](https://github.com/hwdsl2/docker-wireguard), [OpenVPN](https://github.com/hwdsl2/docker-openvpn), [IPsec VPN](https://github.com/hwdsl2/docker-ipsec-vpn-server), [Headscale](https://github.com/hwdsl2/docker-headscale)
- Tools: [MCP Gateway](https://github.com/hwdsl2/docker-mcp-gateway)

**Tip:** WhisperLive, Kokoro, Embeddings, LiteLLM, Ollama, Docling, and MCP Gateway can be [used together](#using-with-other-ai-services) to build a complete, self-hosted AI stack on your own server.

## Community

- Subscribe for project updates (1–2 emails/month): [Self-Hosted Stack](https://selfhostedstack.beehiiv.com/subscribe?utm_campaign=ai)
- Community discussions and showcases: [r/selfhostedstack](https://www.reddit.com/r/selfhostedstack/)

## When to use WhisperLive vs. Whisper

| | [docker-whisper](https://github.com/hwdsl2/docker-whisper) | **docker-whisper-live** |
|---|---|---|
| **Use case** | Transcribe complete audio files | Live microphone / real-time audio streaming |
| **Protocol** | HTTP REST | WebSocket (streaming) + HTTP REST |
| **Latency** | Full file, then response | Near-real-time, word by word |
| **Best for** | Meeting recordings, uploaded audio | Browser capture, RTSP streams, live captions |
| **Image size** | ~190 MB (~3.1 GB for `:cuda`) | ~750 MB (~4.5 GB for `:cuda`) |

## Quick start

Use this command to set up a WhisperLive server:

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
<summary><strong>GPU quick start (NVIDIA CUDA)</strong></summary>

If you have an NVIDIA GPU, use the `:cuda` image for hardware-accelerated inference:

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

**Requirements:** NVIDIA GPU, [NVIDIA driver](https://www.nvidia.com/en-us/drivers/) 535+, and the [NVIDIA Container Toolkit](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/latest/install-guide.html) installed on the host. The `:cuda` image is `linux/amd64` only.

</details>

**Note:** For internet-facing deployments, using a [reverse proxy](#using-a-reverse-proxy) to add HTTPS is **strongly recommended**. In that case, also replace `-p 9090:9090 -p 8000:8000` with `-p 127.0.0.1:9090:9090 -p 127.0.0.1:8000:8000` in the `docker run` command above, to prevent direct access to the unencrypted ports.

The Whisper `base` model (~145 MB) is downloaded and cached on first client connection. Check the logs to confirm the server is ready:

```bash
docker logs whisper-live
```

Once you see "WhisperLive real-time transcription server is ready":

**Connect a real-time WebSocket client:**

```
ws://your_server_ip:9090
```

**Or transcribe a file via the REST API:**

```bash
curl http://your_server_ip:8000/v1/audio/transcriptions \
    -F file=@audio.mp3 \
    -F model=whisper-1
```

**Response:**
```json
{"text": "Your transcribed text appears here."}
```

**Tip:** Need a sample audio file to test the REST API? Download this English speech sample (WAV, MIT License) from the [Azure Samples](https://github.com/Azure-Samples/cognitive-services-speech-sdk) repository:

```bash
curl -L -o sample_speech.wav \
    "https://github.com/Azure-Samples/cognitive-services-speech-sdk/raw/master/sampledata/audiofiles/katiesteve.wav"

curl http://your_server_ip:8000/v1/audio/transcriptions \
    -F file=@sample_speech.wav \
    -F model=whisper-1
```

## Requirements

- A Linux server (local or cloud) with Docker installed
- Supported architectures: `amd64` (x86_64), `arm64` (e.g. Raspberry Pi 4/5, AWS Graviton)
- Minimum RAM: ~700 MB free for the default `base` model (see [model table](#switching-models))
- Internet access for the initial model download (the model is cached locally afterwards). Not required if using `WHISPERLIVE_LOCAL_ONLY=true` with pre-cached models.

**For GPU acceleration (`:cuda` image):**

- NVIDIA GPU with CUDA support (Compute Capability 6.0+)
- [NVIDIA driver](https://www.nvidia.com/en-us/drivers/) 535 or later installed on the host
- [NVIDIA Container Toolkit](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/latest/install-guide.html) installed
- The `:cuda` image supports `linux/amd64` only

For internet-facing deployments, see [Using a reverse proxy](#using-a-reverse-proxy) to add HTTPS.

## Download

Get the trusted build from the [Docker Hub registry](https://hub.docker.com/r/hwdsl2/whisper-live-server/):

```bash
docker pull hwdsl2/whisper-live-server
```

For NVIDIA GPU acceleration, pull the `:cuda` tag instead:

```bash
docker pull hwdsl2/whisper-live-server:cuda
```

Alternatively, you may download from [Quay.io](https://quay.io/repository/hwdsl2/whisper-live-server):

```bash
docker pull quay.io/hwdsl2/whisper-live-server
docker image tag quay.io/hwdsl2/whisper-live-server hwdsl2/whisper-live-server
```

Supported platforms: `linux/amd64` and `linux/arm64`. The `:cuda` tag supports `linux/amd64` only.

## Environment variables

All variables are optional. If not set, secure defaults are used automatically.

This Docker image uses the following variables, that can be declared in an `env` file (see [example](whisper-live.env.example)):

| Variable | Description | Default |
|---|---|---|
| `WHISPERLIVE_MODEL` | Whisper model to use. See [model table](#switching-models) for options. | `base` |
| `WHISPERLIVE_LANGUAGE` | Default transcription language. BCP-47 code (e.g. `en`, `fr`, `de`, `zh`, `ja`) or `auto` to autodetect. | `auto` |
| `WHISPERLIVE_PORT` | WebSocket port for real-time streaming clients (1–65535). | `9090` |
| `WHISPERLIVE_REST_PORT` | HTTP port for the OpenAI-compatible REST API (1–65535). | `8000` |
| `WHISPERLIVE_MAX_CLIENTS` | Maximum number of simultaneous WebSocket client connections. | `4` |
| `WHISPERLIVE_MAX_CONNECTION_TIME` | Maximum WebSocket connection duration in seconds. Clients exceeding this are disconnected. | `600` |
| `WHISPERLIVE_USE_VAD` | Voice Activity Detection default. For the `faster_whisper` backend, VAD is controlled per WebSocket client via the connection handshake `use_vad` field. | `true` |
| `WHISPERLIVE_THREADS` | CPU threads for inference. Set to the number of physical cores for best latency. | `2` |
| `WHISPERLIVE_LOG_LEVEL` | Log level: `DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL`. | `INFO` |
| `WHISPERLIVE_LOCAL_ONLY` | When set to any non-empty value (e.g. `true`), disables all HuggingFace model downloads. For offline or air-gapped deployments with pre-cached models. | *(not set)* |

**Note:** In your `env` file, you may enclose values in single quotes, e.g. `VAR='value'`. Do not add spaces around `=`. If you change `WHISPERLIVE_PORT` or `WHISPERLIVE_REST_PORT`, update the `-p` flags in the `docker run` command accordingly.

Example using an `env` file:

```bash
cp whisper-live.env.example whisper-live.env
# Edit whisper-live.env with your settings, then:
docker run \
    --name whisper-live \
    --restart=always \
    -v whisper-live-data:/var/lib/whisper-live \
    -v ./whisper-live.env:/whisper-live.env:ro \
    -p 9090:9090 \
    -p 8000:8000 \
    -d hwdsl2/whisper-live-server
```

The env file is bind-mounted into the container, so changes are picked up on every restart without recreating the container.

<details>
<summary>Alternatively, pass it with <code>--env-file</code></summary>

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

## Using docker-compose

```bash
cp whisper-live.env.example whisper-live.env
# Edit whisper-live.env as needed, then:
docker compose up -d
docker logs whisper-live
```

Example `docker-compose.yml` (already included):

```yaml
services:
  whisper-live:
    image: hwdsl2/whisper-live-server
    container_name: whisper-live
    restart: always
    ports:
      - "9090:9090/tcp"  # WebSocket — for a host-based reverse proxy, change to "127.0.0.1:9090:9090/tcp"
      - "8000:8000/tcp"  # REST API  — for a host-based reverse proxy, change to "127.0.0.1:8000:8000/tcp"
    volumes:
      - whisper-live-data:/var/lib/whisper-live
      - ./whisper-live.env:/whisper-live.env:ro

volumes:
  whisper-live-data:
    name: whisper-live-data
```

**Note:** For internet-facing deployments, using a [reverse proxy](#using-a-reverse-proxy) to add HTTPS is **strongly recommended**. In that case, also change `"9090:9090/tcp"` and `"8000:8000/tcp"` to their `127.0.0.1:` equivalents in `docker-compose.yml`.

<details>
<summary><strong>Using docker-compose with GPU (NVIDIA CUDA)</strong></summary>

A separate `docker-compose.cuda.yml` is provided for GPU deployments:

```bash
cp whisper-live.env.example whisper-live.env
# Edit whisper-live.env as needed, then:
docker compose -f docker-compose.cuda.yml up -d
docker logs whisper-live
```

Example `docker-compose.cuda.yml` (already included):

```yaml
services:
  whisper-live:
    image: hwdsl2/whisper-live-server:cuda
    container_name: whisper-live
    restart: always
    ports:
      - "9090:9090/tcp"  # WebSocket — for a host-based reverse proxy, change to "127.0.0.1:9090:9090/tcp"
      - "8000:8000/tcp"  # REST API  — for a host-based reverse proxy, change to "127.0.0.1:8000:8000/tcp"
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

## WebSocket streaming

The WebSocket endpoint at port `9090` supports real-time transcription of live audio streams. Clients send raw PCM audio chunks and receive transcription segments as they are decoded.

### Protocol

On connection, send a JSON configuration message first:

```json
{
  "uid": "unique-client-id",
  "language": "en",
  "model": "base",
  "use_vad": true
}
```

Then stream raw 16-bit PCM audio at 16 kHz sample rate as binary WebSocket frames. The server returns JSON transcription events:

```json
{"uid": "unique-client-id", "segments": [{"text": "Hello, how are you?", "start": 0.0, "end": 2.4, "completed": true}]}
```

### Python client example

```python
from whisper_live.client import TranscriptionClient

client = TranscriptionClient(
    "your_server_ip",
    9090,
    lang="en",
    translate=False,
    model="base",
    use_vad=True,
)

# Transcribe from a file
client("audio.mp3")

# Or transcribe from microphone
# client()
```

Install the client library:

```bash
pip install whisper-live
```

### Browser client example

```javascript
const ws = new WebSocket("ws://your_server_ip:9090");

ws.onopen = () => {
  // Send configuration
  ws.send(JSON.stringify({
    uid: "browser-client-1",
    language: "en",
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

// Send audio chunks as ArrayBuffer (16-bit PCM, 16 kHz)
// ws.send(audioBuffer);
```

## REST API reference

The REST API at port `8000` is fully compatible with [OpenAI's audio transcription endpoint](https://developers.openai.com/api/reference/resources/audio/subresources/transcriptions/methods/create). Any application already calling `https://api.openai.com/v1/audio/transcriptions` can switch to self-hosted by setting:

```
OPENAI_BASE_URL=http://your_server_ip:8000
```

### Transcribe audio

```
POST /v1/audio/transcriptions
Content-Type: multipart/form-data
```

**Parameters:**

| Parameter | Type | Required | Description |
|---|---|---|---|
| `file` | file | ✅ | Audio file. Supported formats: `mp3`, `mp4`, `m4a`, `wav`, `webm`, `ogg`, `flac` and all other formats supported by ffmpeg. |
| `model` | string | ✅ | Pass `whisper-1` (value is accepted but ignored; the active `WHISPERLIVE_MODEL` is always used). |
| `language` | string | — | BCP-47 language code (e.g. `en`, `fr`, `zh`). If omitted, language is autodetected. |

**Example:**

```bash
curl http://your_server_ip:8000/v1/audio/transcriptions \
    -F file=@meeting.m4a \
    -F model=whisper-1 \
    -F language=en
```

**Response:**
```json
{"text": "Your transcribed text appears here."}
```

### Interactive API docs

An interactive Swagger UI is available at:

```
http://your_server_ip:8000/docs
```

## Persistent data

All server data is stored in the Docker volume (`/var/lib/whisper-live` inside the container):

```
/var/lib/whisper-live/
├── models--Systran--faster-whisper-*/   # Cached Whisper model files (downloaded from HuggingFace)
├── .ws_port              # Active WebSocket port (used by whisper_live_manage)
├── .rest_port            # Active REST API port (used by whisper_live_manage)
├── .model                # Active model name (used by whisper_live_manage)
└── .server_addr          # Cached server IP (used by whisper_live_manage)
```

Back up the Docker volume to preserve downloaded models. Models are large (145 MB – 3 GB) and can take several minutes to download on first client connection; preserving the volume avoids re-downloading on container recreation.

**Tip:** The `/var/lib/whisper-live` volume uses the same HuggingFace cache layout as `docker-whisper`'s `/var/lib/whisper` volume. If you have already downloaded a model with `docker-whisper`, you can bind-mount the same volume directory to avoid re-downloading.

## Managing the server

Use `whisper_live_manage` inside the running container to inspect and manage the server.

**Show server info:**

```bash
docker exec whisper-live whisper_live_manage --showinfo
```

**List available models:**

```bash
docker exec whisper-live whisper_live_manage --listmodels
```

**Pre-download a model:**

```bash
docker exec whisper-live whisper_live_manage --downloadmodel large-v3-turbo
```

## Switching models

To change the active model:

1. *(Optional but recommended)* Pre-download the new model while the server is running:
   ```bash
   docker exec whisper-live whisper_live_manage --downloadmodel large-v3-turbo
   ```

2. Update `WHISPERLIVE_MODEL` in your `whisper-live.env` file (or add `-e WHISPERLIVE_MODEL=large-v3-turbo` to your `docker run` command).

3. Restart the container:
   ```bash
   docker restart whisper-live
   ```

**Available models:**

| Model | Disk | RAM (approx) | Notes |
|---|---|---|---|
| `tiny` | ~75 MB | ~250 MB | Fastest; lower accuracy |
| `tiny.en` | ~75 MB | ~250 MB | English-only |
| `base` | ~145 MB | ~700 MB | Good balance — **default** |
| `base.en` | ~145 MB | ~700 MB | English-only |
| `small` | ~465 MB | ~1.5 GB | Better accuracy |
| `small.en` | ~465 MB | ~1.5 GB | English-only |
| `medium` | ~1.5 GB | ~5 GB | High accuracy |
| `medium.en` | ~1.5 GB | ~5 GB | English-only |
| `large-v1` | ~3 GB | ~10 GB | Older large model |
| `large-v2` | ~3 GB | ~10 GB | Very high accuracy |
| `large-v3` | ~3 GB | ~10 GB | Best accuracy |
| `large-v3-turbo` | ~1.6 GB | ~6 GB | Fast + high accuracy ⭐ |
| `turbo` | ~1.6 GB | ~6 GB | Alias for `large-v3-turbo` |

> **Tip:** `large-v3-turbo` offers accuracy close to `large-v3` at roughly half the resource cost. It is the recommended upgrade path from `base` for most production deployments.

RAM figures are approximate and reflect INT8 quantization (default). Models are cached in the `/var/lib/whisper-live` Docker volume and only downloaded once.

## Using a reverse proxy

For internet-facing deployments, place a reverse proxy in front of the server to handle HTTPS and WSS (secure WebSocket) termination.

Use one of the following addresses to reach the container from your reverse proxy:

- **`whisper-live:9090`** / **`whisper-live:8000`** — if your reverse proxy runs as a container in the **same Docker network**.
- **`127.0.0.1:9090`** / **`127.0.0.1:8000`** — if your reverse proxy runs **on the host** and the ports are published.

**Example with [Caddy](https://caddyserver.com/docs/) ([Docker image](https://hub.docker.com/_/caddy))** (automatic TLS, WebSocket proxying in the same Docker network):

`Caddyfile`:
```
whisper-live.example.com {
  # WebSocket streaming (wss://)
  handle /ws* {
    reverse_proxy whisper-live:9090
  }
  # REST API (https://)
  reverse_proxy whisper-live:8000
}
```

**Example with nginx** (reverse proxy on the host):

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

    # WebSocket streaming
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

> **Important:** WebSocket proxying requires `proxy_http_version 1.1` and the `Upgrade`/`Connection` headers. Without these, real-time streaming will not work through nginx.

<details>
<summary><strong>Adding authentication at the proxy layer</strong></summary>

The server itself does not enforce API key authentication. For internet-facing deployments, you can add Bearer token or basic auth at the reverse proxy layer. Example with Caddy (`basicauth` protects the REST API):

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

Example with nginx (`auth_basic` on the REST API location):

```nginx
location /v1/ {
    auth_basic           "WhisperLive";
    auth_basic_user_file /etc/nginx/.htpasswd;
    proxy_pass           http://127.0.0.1:8000;
    proxy_set_header     Host $host;
    proxy_read_timeout   300s;
}
```

The WebSocket endpoint (`/`, port `9090`) does not support HTTP authentication headers; secure it by keeping the port bound to `127.0.0.1` and placing it behind the reverse proxy with network-level access controls.

</details>

## Update Docker image

To update the Docker image and container, first [download](#download) the latest version:

```bash
docker pull hwdsl2/whisper-live-server
```

If the Docker image is already up to date, you should see:

```
Status: Image is up to date for hwdsl2/whisper-live-server:latest
```

Otherwise, it will download the latest version. Remove and re-create the container:

```bash
docker rm -f whisper-live
# Then re-run the docker run command from Quick start with the same volumes and ports.
```

Your downloaded models are preserved in the `whisper-live-data` volume.

## Using with other AI services

The WhisperLive (real-time STT), Embeddings, LiteLLM, Kokoro (TTS), Ollama (LLM), Docling, and MCP Gateway images can be combined to build a complete, self-hosted AI stack on your own server — from live voice I/O to RAG-powered question answering. WhisperLive, Kokoro, and Embeddings run fully locally. Ollama runs all LLM inference locally, so no data is sent to third parties. When using LiteLLM with external providers (e.g., OpenAI, Anthropic), your data will be sent to those providers.

| Service | Role | Default port |
|---|---|---|
| **[WhisperLive (real-time STT)](https://github.com/hwdsl2/docker-whisper-live)** | Real-time WebSocket streaming transcription for live audio | `9090` (WS), `8000` (REST) |
| **[Embeddings](https://github.com/hwdsl2/docker-embeddings)** | Converts text to vectors for semantic search and RAG | `8000` |
| **[LiteLLM](https://github.com/hwdsl2/docker-litellm)** | AI gateway — routes requests to Ollama, OpenAI, Anthropic, and 100+ providers | `4000` |
| **[Kokoro (TTS)](https://github.com/hwdsl2/docker-kokoro)** | Converts text to natural-sounding speech | `8880` |
| **[Ollama (LLM)](https://github.com/hwdsl2/docker-ollama)** | Runs local LLM models (llama3, qwen, mistral, etc.) | `11434` |
| **[MCP Gateway](https://github.com/hwdsl2/docker-mcp-gateway)** | Exposes AI services as MCP tools for AI assistants (Claude, Cursor, etc.) | `3000` |
| **[Docling](https://github.com/hwdsl2/docker-docling)** | Converts documents (PDF, DOCX, etc.) to structured text/Markdown | `5001` |

**See also: [Docker AI Stack](https://github.com/hwdsl2/docker-ai-stack)** — deploy the full stack with a single command, with ready-made configurations and pipeline examples.

## Technical details

- Base image: `python:3.12-slim` (Debian)
- Runtime: Python 3 (virtual environment at `/opt/venv`)
- STT engine: [WhisperLive](https://github.com/collabora/WhisperLive) + [faster-whisper](https://github.com/SYSTRAN/faster-whisper) with CTranslate2 (INT8 on CPU, FP16 on CUDA)
- VAD: [Silero VAD](https://github.com/snakers4/silero-vad) via PyTorch (CPU or CUDA, auto-detected)
- WebSocket server: Python `websockets` library
- REST API framework: [FastAPI](https://fastapi.tiangolo.com/) + [Uvicorn](https://www.uvicorn.org/)
- Data directory: `/var/lib/whisper-live` (Docker volume)
- Model storage: HuggingFace Hub format inside the volume — downloaded once, reused on restarts

## License

**Note:** The software components inside the pre-built image (such as WhisperLive, faster-whisper, PyTorch, and their dependencies) are under the respective licenses chosen by their respective copyright holders. As for any pre-built image usage, it is the image user's responsibility to ensure that any use of this image complies with any relevant licenses for all software contained within.

Copyright (C) 2026 Lin Song   
This work is licensed under the [MIT License](https://opensource.org/licenses/MIT).

**WhisperLive** is Copyright (C) Vineet Suryan, Collabora Ltd., and is distributed under the [MIT License](https://github.com/collabora/WhisperLive/blob/main/LICENSE).

**faster-whisper** is Copyright (C) SYSTRAN, and is distributed under the [MIT License](https://github.com/SYSTRAN/faster-whisper/blob/master/LICENSE).

This project is an independent Docker setup and is not affiliated with, endorsed by, or sponsored by OpenAI, Collabora, or SYSTRAN.