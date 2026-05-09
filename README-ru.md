[English](README.md) | [简体中文](README-zh.md) | [繁體中文](README-zh-Hant.md) | [Русский](README-ru.md)

# WhisperLive — Распознавание речи в реальном времени на Docker

[![Статус сборки](https://github.com/hwdsl2/docker-whisper-live/actions/workflows/main.yml/badge.svg)](https://github.com/hwdsl2/docker-whisper-live/actions/workflows/main.yml) &nbsp;[![License: MIT](docs/images/license.svg)](https://opensource.org/licenses/MIT) &nbsp;[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://vpnsetup.net/whisper-live-notebook)

Docker-образ для запуска сервера [WhisperLive](https://github.com/collabora/WhisperLive) с транскрибированием речи в реальном времени на базе [faster-whisper](https://github.com/SYSTRAN/faster-whisper). Предоставляет потоковую передачу через WebSocket для распознавания живого аудио и совместимый с OpenAI REST API для транскрибирования файлов. Основан на Debian (python:3.12-slim). Простой, приватный, для самостоятельного развёртывания.

**Возможности:**

- Потоковая передача через WebSocket в реальном времени — транскрибирование живого аудио с микрофона или потоков с минимальной задержкой
- Совместимый с OpenAI REST API — `POST /v1/audio/transcriptions` для файлового транскрибирования; любое приложение, использующее OpenAI Whisper API, переключается одной строкой
- Поддержка всех моделей Whisper: `tiny`, `base`, `small`, `medium`, `large-v3`, `large-v3-turbo` и других
- Обнаружение голосовой активности (VAD) — автоматически пропускает тишину для более быстрого и чистого транскрибирования
- Управление моделями через вспомогательный скрипт (`whisper_live_manage`)
- Аудио остаётся на вашем сервере — данные не передаются третьим сторонам
- Ускорение на GPU NVIDIA (CUDA) для более быстрого инференса (тег образа `:cuda`)
- Офлайн-режим — работа без доступа к интернету с предварительно загруженными моделями (`WHISPERLIVE_LOCAL_ONLY`)
- Автоматическая сборка и публикация через [GitHub Actions](https://github.com/hwdsl2/docker-whisper-live/actions/workflows/main.yml)
- Постоянный кэш моделей через Docker-том
- Мультиархитектурная поддержка: `linux/amd64`, `linux/arm64`

**Также доступно:**

- Попробовать онлайн: [Открыть в Colab](https://vpnsetup.net/whisper-live-notebook) — Docker и установка не требуются
- ИИ/Аудио: [Whisper (пакетный STT)](https://github.com/hwdsl2/docker-whisper/blob/main/README-ru.md), [Kokoro (TTS)](https://github.com/hwdsl2/docker-kokoro/blob/main/README-ru.md), [Embeddings](https://github.com/hwdsl2/docker-embeddings/blob/main/README-ru.md), [LiteLLM](https://github.com/hwdsl2/docker-litellm/blob/main/README-ru.md), [Ollama (LLM)](https://github.com/hwdsl2/docker-ollama/blob/main/README-ru.md)
- VPN: [WireGuard](https://github.com/hwdsl2/docker-wireguard/blob/main/README-ru.md), [OpenVPN](https://github.com/hwdsl2/docker-openvpn/blob/main/README-ru.md), [IPsec VPN](https://github.com/hwdsl2/docker-ipsec-vpn-server/blob/master/README-ru.md), [Headscale](https://github.com/hwdsl2/docker-headscale/blob/main/README-ru.md)
- Инструменты: [MCP Gateway](https://github.com/hwdsl2/docker-mcp-gateway/blob/main/README-ru.md)

**Совет:** WhisperLive, Kokoro, Embeddings, LiteLLM, Ollama и MCP-шлюз можно [использовать совместно](#использование-с-другими-ai-сервисами) для построения полного self-hosted AI-стека на собственном сервере. См. [Docker AI Stack](https://github.com/hwdsl2/docker-ai-stack) — готовые конфигурации и примеры конвейеров.

## WhisperLive или Whisper?

| | [docker-whisper](https://github.com/hwdsl2/docker-whisper/blob/main/README-ru.md) | **docker-whisper-live** |
|---|---|---|
| **Назначение** | Транскрибирование готовых аудиофайлов | Живой микрофон / потоковое аудио в реальном времени |
| **Протокол** | HTTP REST | WebSocket (потоковый) + HTTP REST |
| **Задержка** | Ответ после обработки всего файла | Почти мгновенно, слово за словом |
| **Подходит для** | Записи совещаний, загруженные аудиофайлы | Захват в браузере, RTSP-потоки, живые субтитры |
| **Размер образа** | ~180 МБ (~3 ГБ для `:cuda`) | ~730 МБ (~4,5 ГБ для `:cuda`) |

## Быстрый старт

Запустите сервер WhisperLive:

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
<summary><strong>Быстрый старт с GPU (NVIDIA CUDA)</strong></summary>

Если у вас есть GPU NVIDIA, используйте образ `:cuda` для аппаратного ускорения инференса:

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

**Требования:** GPU NVIDIA, [драйвер NVIDIA](https://www.nvidia.com/en-us/drivers/) 535+, установленный на хосте [NVIDIA Container Toolkit](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/latest/install-guide.html). Образ `:cuda` поддерживает только `linux/amd64`.

</details>

**Важно:** Для работы образа с моделью `base` по умолчанию требуется не менее 700 МБ свободной оперативной памяти. Системы с 512 МБ ОЗУ и менее не поддерживаются.

**Примечание:** Для развёртывания с доступом из интернета **настоятельно рекомендуется** использовать [обратный прокси](#использование-обратного-прокси) для добавления HTTPS. В этом случае также замените `-p 9090:9090 -p 8000:8000` на `-p 127.0.0.1:9090:9090 -p 127.0.0.1:8000:8000`.

При первом подключении клиента модель Whisper `base` (~145 МБ) скачивается и кэшируется. Проверьте логи:

```bash
docker logs whisper-live
```

После появления "WhisperLive real-time transcription server is ready":

**Подключение WebSocket-клиента в реальном времени:**

```
ws://ip_вашего_сервера:9090
```

**Или транскрибирование файла через REST API:**

```bash
curl http://ip_вашего_сервера:8000/v1/audio/transcriptions \
    -F file=@audio.mp3 \
    -F model=whisper-1
```

**Ответ:**
```json
{"text": "Транскрибированный текст появляется здесь."}
```

**Совет:** Нужен образец аудиофайла для тестирования REST API? Можно использовать этот образец английской речи (WAV, лицензия MIT) из репозитория [Azure Samples](https://github.com/Azure-Samples/cognitive-services-speech-sdk):

```bash
curl -L -o sample_speech.wav \
    "https://github.com/Azure-Samples/cognitive-services-speech-sdk/raw/master/sampledata/audiofiles/katiesteve.wav"

curl http://ip_вашего_сервера:8000/v1/audio/transcriptions \
    -F file=@sample_speech.wav \
    -F model=whisper-1
```

## Требования

- Сервер Linux (локальный или облачный) с установленным Docker
- Поддерживаемые архитектуры: `amd64` (x86_64), `arm64` (например, Raspberry Pi 4/5, AWS Graviton)
- Минимум ОЗУ: ~700 МБ свободной памяти для модели `base` по умолчанию (см. [таблицу моделей](#смена-модели))
- Доступ к интернету для первоначальной загрузки модели (после чего она кэшируется локально). Не требуется при использовании `WHISPERLIVE_LOCAL_ONLY=true` с предварительно загруженными моделями.

**Для ускорения на GPU (образ `:cuda`):**

- GPU NVIDIA с поддержкой CUDA (Compute Capability 6.0+)
- [Драйвер NVIDIA](https://www.nvidia.com/en-us/drivers/) версии 535 или новее на хосте
- Установленный [NVIDIA Container Toolkit](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/latest/install-guide.html)
- Образ `:cuda` поддерживает только `linux/amd64`

Для развёртывания с выходом в интернет см. раздел [Использование обратного прокси](#использование-обратного-прокси) для включения HTTPS.

## Загрузка

Получить проверенную сборку из [Docker Hub](https://hub.docker.com/r/hwdsl2/whisper-live-server/):

```bash
docker pull hwdsl2/whisper-live-server
```

Для GPU-ускорения NVIDIA используйте тег `:cuda`:

```bash
docker pull hwdsl2/whisper-live-server:cuda
```

Или из [Quay.io](https://quay.io/repository/hwdsl2/whisper-live-server):

```bash
docker pull quay.io/hwdsl2/whisper-live-server
docker image tag quay.io/hwdsl2/whisper-live-server hwdsl2/whisper-live-server
```

Поддерживаемые платформы: `linux/amd64` и `linux/arm64`. Тег `:cuda` поддерживает только `linux/amd64`.

## Переменные окружения

Все переменные необязательны. При отсутствии используются безопасные значения по умолчанию.

| Переменная | Описание | По умолчанию |
|---|---|---|
| `WHISPERLIVE_MODEL` | Модель Whisper. См. [таблицу моделей](#смена-модели). | `base` |
| `WHISPERLIVE_LANGUAGE` | Язык транскрибирования по умолчанию. Код BCP-47 (например, `ru`, `en`) или `auto` для автоопределения. | `auto` |
| `WHISPERLIVE_PORT` | Порт WebSocket для потоковых клиентов (1–65535). | `9090` |
| `WHISPERLIVE_REST_PORT` | HTTP-порт совместимого с OpenAI REST API (1–65535). | `8000` |
| `WHISPERLIVE_MAX_CLIENTS` | Максимальное количество одновременных WebSocket-подключений. | `4` |
| `WHISPERLIVE_MAX_CONNECTION_TIME` | Максимальная длительность WebSocket-подключения в секундах. | `600` |
| `WHISPERLIVE_USE_VAD` | Включить обнаружение голосовой активности. `true` — пропускать тишину, `false` — обрабатывать всё аудио непрерывно. | `true` |
| `WHISPERLIVE_THREADS` | Потоки CPU для инференса. Установите равным количеству физических ядер для минимальной задержки. | `2` |
| `WHISPERLIVE_LOG_LEVEL` | Уровень логирования: `DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL`. | `INFO` |
| `WHISPERLIVE_LOCAL_ONLY` | При установке любого непустого значения (например, `true`) отключает загрузку моделей с HuggingFace. Для офлайн-развёртываний. | *(не задано)* |

Пример использования env-файла:

```bash
cp whisper-live.env.example whisper-live.env
# Отредактируйте whisper-live.env и запустите:
docker run \
    --name whisper-live \
    --restart=always \
    -v whisper-live-data:/var/lib/whisper-live \
    -v ./whisper-live.env:/whisper-live.env:ro \
    -p 9090:9090 \
    -p 8000:8000 \
    -d hwdsl2/whisper-live-server
```

Файл `env` монтируется в контейнер, изменения применяются при каждом перезапуске без пересоздания контейнера.

<details>
<summary>Либо передайте его через <code>--env-file</code></summary>

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

## Использование docker-compose

```bash
cp whisper-live.env.example whisper-live.env
# Отредактируйте whisper-live.env при необходимости, затем:
docker compose up -d
docker logs whisper-live
```

Пример `docker-compose.yml` (уже включён в проект):

```yaml
services:
  whisper-live:
    image: hwdsl2/whisper-live-server
    container_name: whisper-live
    restart: always
    ports:
      - "9090:9090/tcp"  # WebSocket — для хостового обратного прокси измените на "127.0.0.1:9090:9090/tcp"
      - "8000:8000/tcp"  # REST API  — для хостового обратного прокси измените на "127.0.0.1:8000:8000/tcp"
    volumes:
      - whisper-live-data:/var/lib/whisper-live
      - ./whisper-live.env:/whisper-live.env:ro

volumes:
  whisper-live-data:
    name: whisper-live-data
```

**Примечание:** Для развёртывания с выходом в интернет настоятельно рекомендуется использовать [обратный прокси](#использование-обратного-прокси) для добавления HTTPS. В этом случае также измените порты на их `127.0.0.1:` варианты в `docker-compose.yml`.

<details>
<summary><strong>Использование docker-compose с GPU (NVIDIA CUDA)</strong></summary>

Для развёртывания с GPU используется отдельный файл `docker-compose.cuda.yml`:

```bash
cp whisper-live.env.example whisper-live.env
# Отредактируйте whisper-live.env при необходимости, затем:
docker compose -f docker-compose.cuda.yml up -d
docker logs whisper-live
```

Пример `docker-compose.cuda.yml` (уже включён в проект):

```yaml
services:
  whisper-live:
    image: hwdsl2/whisper-live-server:cuda
    container_name: whisper-live
    restart: always
    ports:
      - "9090:9090/tcp"  # WebSocket — для хостового обратного прокси измените на "127.0.0.1:9090:9090/tcp"
      - "8000:8000/tcp"  # REST API  — для хостового обратного прокси измените на "127.0.0.1:8000:8000/tcp"
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

## Потоковая передача через WebSocket

WebSocket-эндпоинт на порту `9090` поддерживает транскрибирование живых аудиопотоков.

### Протокол

При подключении сначала отправьте JSON-конфигурацию:

```json
{
  "uid": "unique-client-id",
  "language": "ru",
  "model": "base",
  "use_vad": true
}
```

Затем передавайте сырое 16-битное PCM-аудио на частоте 16 кГц бинарными WebSocket-фреймами. Сервер возвращает JSON-события транскрибирования:

```json
{"uid": "unique-client-id", "segments": [{"text": "Привет, как дела?", "start": 0.0, "end": 2.4, "completed": true}]}
```

### Пример Python-клиента

```python
from whisper_live.client import TranscriptionClient

client = TranscriptionClient(
    "ip_вашего_сервера",
    9090,
    lang="ru",
    translate=False,
    model="base",
    use_vad=True,
)

# Транскрибирование файла
client("audio.mp3")

# Или с микрофона
# client()
```

Установка клиентской библиотеки:

```bash
pip install whisper-live
```

### Пример браузерного клиента

```javascript
const ws = new WebSocket("ws://ip_вашего_сервера:9090");

ws.onopen = () => {
  // Отправляем конфигурацию
  ws.send(JSON.stringify({
    uid: "browser-client-1",
    language: "ru",
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

// Отправляем аудиофрагменты как ArrayBuffer (16-бит PCM, 16 кГц)
// ws.send(audioBuffer);
```

## REST API

REST API на порту `8000` полностью совместим с [эндпоинтом OpenAI для транскрибирования аудио](https://developers.openai.com/api/reference/resources/audio/subresources/transcriptions/methods/create). Любое приложение, уже вызывающее `https://api.openai.com/v1/audio/transcriptions`, может переключиться на самостоятельно размещённый сервер, установив:

```
OPENAI_BASE_URL=http://ip_вашего_сервера:8000
```

### Транскрибирование аудио

```
POST /v1/audio/transcriptions
Content-Type: multipart/form-data
```

**Параметры:**

| Параметр | Тип | Обязательно | Описание |
|---|---|---|---|
| `file` | файл | ✅ | Аудиофайл. Поддерживаемые форматы: `mp3`, `mp4`, `m4a`, `wav`, `webm`, `ogg`, `flac` и все форматы, поддерживаемые ffmpeg. |
| `model` | строка | ✅ | Передайте `whisper-1` (значение принимается, но всегда используется активная модель). |
| `language` | строка | — | Код языка BCP-47 (например, `ru`, `en`, `zh`). Если не указан, язык определяется автоматически. |

**Пример:**

```bash
curl http://ip_вашего_сервера:8000/v1/audio/transcriptions \
    -F file=@meeting.m4a \
    -F model=whisper-1 \
    -F language=ru
```

**Ответ:**
```json
{"text": "Транскрибированный текст появляется здесь."}
```

### Интерактивная документация API

Интерактивная документация Swagger UI:

```
http://ip_вашего_сервера:8000/docs
```

## Постоянные данные

Все данные сервера хранятся в Docker-томе (`/var/lib/whisper-live` внутри контейнера):

```
/var/lib/whisper-live/
├── models--Systran--faster-whisper-*/   # Кэшированные файлы модели Whisper (загружены с HuggingFace)
├── .ws_port              # Активный порт WebSocket (используется whisper_live_manage)
├── .rest_port            # Активный порт REST API (используется whisper_live_manage)
├── .model                # Активное имя модели (используется whisper_live_manage)
└── .server_addr          # Кэшированный IP сервера (используется whisper_live_manage)
```

Загруженные модели сохраняются в томе `whisper-live-data`. Создавайте резервные копии Docker-тома для сохранения загруженных моделей. Модели занимают от 145 МБ до 3 ГБ и могут загружаться несколько минут при первом подключении клиента; сохранение тома позволяет избежать повторной загрузки при пересоздании контейнера.

**Совет:** Том `/var/lib/whisper-live` использует ту же схему кэша HuggingFace, что и том `/var/lib/whisper` проекта `docker-whisper`. Если вы уже скачали модель с помощью `docker-whisper`, можно примонтировать тот же каталог тома, чтобы избежать повторной загрузки.

## Управление сервером

```bash
docker exec whisper-live whisper_live_manage --showinfo
docker exec whisper-live whisper_live_manage --listmodels
docker exec whisper-live whisper_live_manage --downloadmodel large-v3-turbo
```

## Смена модели

1. *(Опционально, но рекомендуется)* Предварительно скачайте новую модель:
   ```bash
   docker exec whisper-live whisper_live_manage --downloadmodel large-v3-turbo
   ```
2. Обновите `WHISPERLIVE_MODEL` в файле `whisper-live.env`.
3. Перезапустите контейнер:
   ```bash
   docker restart whisper-live
   ```

**Доступные модели:**

| Модель | Диск | ОЗУ (примерно) | Примечания |
|---|---|---|---|
| `tiny` | ~75 МБ | ~250 МБ | Самая быстрая; низкая точность |
| `tiny.en` | ~75 МБ | ~250 МБ | Только английский |
| `base` | ~145 МБ | ~700 МБ | Хороший баланс — **по умолчанию** |
| `base.en` | ~145 МБ | ~700 МБ | Только английский |
| `small` | ~465 МБ | ~1,5 ГБ | Повышенная точность |
| `small.en` | ~465 МБ | ~1,5 ГБ | Только английский |
| `medium` | ~1,5 ГБ | ~5 ГБ | Высокая точность |
| `medium.en` | ~1,5 ГБ | ~5 ГБ | Только английский |
| `large-v1` | ~3 ГБ | ~10 ГБ | Старая большая модель |
| `large-v2` | ~3 ГБ | ~10 ГБ | Очень высокая точность |
| `large-v3` | ~3 ГБ | ~10 ГБ | Наивысшая точность |
| `large-v3-turbo` | ~1,6 ГБ | ~6 ГБ | Быстрая + высокая точность ⭐ |
| `turbo` | ~1,6 ГБ | ~6 ГБ | Псевдоним для `large-v3-turbo` |

> **Совет:** `large-v3-turbo` обеспечивает точность, близкую к `large-v3`, при вдвое меньшем потреблении ресурсов. Для большинства производственных развёртываний это рекомендуемый вариант обновления с `base`.

Данные по памяти являются приблизительными и учитывают квантование INT8 (по умолчанию). Модели кэшируются в Docker-томе `/var/lib/whisper-live` и загружаются только один раз.

## Использование обратного прокси

Используйте один из следующих адресов для доступа к контейнеру из обратного прокси:

- **`whisper-live:9090`** / **`whisper-live:8000`** — если обратный прокси работает как контейнер в **той же Docker-сети**.
- **`127.0.0.1:9090`** / **`127.0.0.1:8000`** — если обратный прокси работает **на хосте** и порты опубликованы.

**Пример с [Caddy](https://caddyserver.com/docs/) ([Docker-образ](https://hub.docker.com/_/caddy))** (автоматический TLS, проксирование WebSocket в той же Docker-сети):

`Caddyfile`:
```
whisper-live.example.com {
  # WebSocket-поток (wss://)
  handle /ws* {
    reverse_proxy whisper-live:9090
  }
  # REST API (https://)
  reverse_proxy whisper-live:8000
}
```

**Пример с nginx** (обратный прокси на хосте):

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

    # WebSocket-поток
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

> **Важно:** Для проксирования WebSocket необходимы `proxy_http_version 1.1` и заголовки `Upgrade`/`Connection`. Без них потоковая передача в реальном времени через nginx работать не будет.

<details>
<summary><strong>Добавление аутентификации на уровне прокси</strong></summary>

Сервер сам по себе не требует API-ключ. Для развёртываний с доступом из интернета можно добавить Bearer-токен или базовую аутентификацию на уровне обратного прокси. Пример с Caddy (`basicauth` защищает REST API):

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

Пример с nginx (`auth_basic` на location REST API):

```nginx
location /v1/ {
    auth_basic           "WhisperLive";
    auth_basic_user_file /etc/nginx/.htpasswd;
    proxy_pass           http://127.0.0.1:8000;
    proxy_set_header     Host $host;
    proxy_read_timeout   300s;
}
```

WebSocket-эндпоинт (`/`, порт `9090`) не поддерживает HTTP-заголовки аутентификации; защитите его, привязав порт к `127.0.0.1` и разместив за обратным прокси с контролем доступа на сетевом уровне.

</details>

## Обновление Docker-образа

```bash
docker pull hwdsl2/whisper-live-server
docker rm -f whisper-live
# Затем повторно выполните команду docker run из раздела «Быстрый старт» с теми же томами и портами.
```

Загруженные модели сохраняются в томе `whisper-live-data`.

## Использование с другими AI-сервисами

[WhisperLive (STT в реальном времени)](https://github.com/hwdsl2/docker-whisper-live/blob/main/README-ru.md), [Embeddings](https://github.com/hwdsl2/docker-embeddings/blob/main/README-ru.md), [LiteLLM](https://github.com/hwdsl2/docker-litellm/blob/main/README-ru.md), [Kokoro (TTS)](https://github.com/hwdsl2/docker-kokoro/blob/main/README-ru.md), [Ollama (LLM)](https://github.com/hwdsl2/docker-ollama/blob/main/README-ru.md) и [MCP-шлюз](https://github.com/hwdsl2/docker-mcp-gateway/blob/main/README-ru.md) можно объединить для построения полного self-hosted AI-стека на собственном сервере — от голосового ввода/вывода в реальном времени до RAG-поиска с ответами. WhisperLive, Kokoro и Embeddings работают полностью локально. Ollama выполняет весь инференс LLM локально, данные не отправляются третьим сторонам. Если вы настроите LiteLLM с внешними провайдерами (например, OpenAI, Anthropic), ваши данные будут переданы этим провайдерам для обработки.

| Сервис | Назначение | Порт по умолчанию |
|---|---|---|
| **[WhisperLive (STT в реальном времени)](https://github.com/hwdsl2/docker-whisper-live/blob/main/README-ru.md)** | Потоковое транскрибирование через WebSocket | `9090` (WS), `8000` (REST) |
| **[Embeddings](https://github.com/hwdsl2/docker-embeddings/blob/main/README-ru.md)** | Преобразование текста в векторы для семантического поиска и RAG | `8000` |
| **[LiteLLM](https://github.com/hwdsl2/docker-litellm/blob/main/README-ru.md)** | AI-шлюз — маршрутизация запросов к OpenAI, Anthropic, Ollama и 100+ другим провайдерам | `4000` |
| **[Kokoro (TTS)](https://github.com/hwdsl2/docker-kokoro/blob/main/README-ru.md)** | Преобразование текста в естественную речь | `8880` |
| **[Ollama (LLM)](https://github.com/hwdsl2/docker-ollama/blob/main/README-ru.md)** | Запускает локальные LLM-модели (llama3, qwen, mistral и др.) | `11434` |
| **[MCP-шлюз](https://github.com/hwdsl2/docker-mcp-gateway/blob/main/README-ru.md)** | Предоставляет сервисы ИИ как MCP-инструменты для ИИ-ассистентов (Claude, Cursor и др.) | `3000` |

**См. также: [Docker AI Stack](https://github.com/hwdsl2/docker-ai-stack)** — готовые docker-compose конфигурации и примеры конвейеров. Узнайте больше о развёртывании полного AI-стека.

## Техническая информация

- Базовый образ: `python:3.12-slim` (Debian)
- Среда выполнения: Python 3 (виртуальное окружение в `/opt/venv`)
- STT-движок: [WhisperLive](https://github.com/collabora/WhisperLive) + [faster-whisper](https://github.com/SYSTRAN/faster-whisper) с CTranslate2 (INT8 на CPU, FP16 на CUDA)
- VAD: [Silero VAD](https://github.com/snakers4/silero-vad) через PyTorch (CPU или CUDA, определяется автоматически)
- WebSocket-сервер: библиотека Python `websockets`
- REST API: [FastAPI](https://fastapi.tiangolo.com/) + [Uvicorn](https://www.uvicorn.org/)
- Директория данных: `/var/lib/whisper-live` (Docker-том)
- Хранение моделей: формат HuggingFace Hub внутри тома — загружается один раз, переиспользуется при перезапусках

## Лицензия

**Примечание:** Программные компоненты внутри готового образа (такие как WhisperLive, faster-whisper, PyTorch и их зависимости) распространяются под соответствующими лицензиями, выбранными их правообладателями. При использовании готового образа пользователь несёт ответственность за соблюдение всех применимых лицензий.

Copyright (C) 2026 Lin Song   
Данная работа распространяется под [лицензией MIT](https://opensource.org/licenses/MIT).

**WhisperLive** является собственностью Vineet Suryan, Collabora Ltd. и распространяется под [лицензией MIT](https://github.com/collabora/WhisperLive/blob/main/LICENSE).

**faster-whisper** является собственностью SYSTRAN и распространяется под [лицензией MIT](https://github.com/SYSTRAN/faster-whisper/blob/master/LICENSE).

Данный проект является независимой Docker-обёрткой и не связан с OpenAI, Collabora или SYSTRAN, не одобрен и не спонсируется ими.

