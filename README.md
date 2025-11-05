Absolutely — here's a **cleaned, merged, clearer, and more professional** README that keeps your styling but avoids duplication, clarifies features, and improves flow & SEO.

---

# 🎙️ Speech-To-Text & Auto-Captions Converter

**Local Whisper-powered subtitle generator — Audio & Video → TXT / SRT / VTT**

A powerful, privacy-first Python tool to convert **audio or video** into:

✅ Text (`.txt`)
✅ SRT Subtitles (`.srt`)
✅ WebVTT Captions (`.vtt`)

Powered by **Faster-Whisper** (CPU-optimized) with **OpenAI Whisper fallback** — no internet required.

Supports **MP3, WAV, MP4, MKV, MOV, FLAC, OGG, M4A** and more.

> Output files are saved **in the same folder as the script by default** (configurable).

---

## ✨ Features

| Capability                  | Details                                             |
| --------------------------- | --------------------------------------------------- |
| 🎥 Video → Audio → Captions | Automatically extracts 16k mono WAV w/ FFmpeg       |
| 🎧 Audio Transcription      | MP3 / WAV / M4A / FLAC / OGG / AAC ...              |
| ⚡ Faster-Whisper            | Fast CPU inference (int8) + optional VAD            |
| 🧠 Whisper Fallback         | Uses official Whisper if Faster-Whisper unavailable |
| 🗂 GUI File Picker          | Select file if `--file` not provided                |
| 🛠 Command Line             | Scriptable for automations / batch workflows        |
| 🌍 Language Support         | Auto-detect or manually specify `--lang`            |
| 📦 Outputs                  | `.txt` `.srt` `.vtt` with timestamps                |
| 🔐 Private & Local          | No cloud usage, no API keys — fully offline         |

---

## 📦 Requirements

### Python

```
Python 3.8+
```

### Install Dependencies

```bash
pip install -U faster-whisper openai-whisper onnxruntime
```

> `onnxruntime` is optional but enables **Voice Activity Detection (VAD)**.

### Install FFmpeg

Required for extracting audio from video.

**Windows**

```bash
winget install Gyan.FFmpeg
```

**macOS**

```bash
brew install ffmpeg
```

**Linux**

```bash
sudo apt install ffmpeg
```

---

## 🚀 Usage

### GUI Mode — File Picker

Just run the script:

```bash
python Speech_To_Text.py
```

### Command-Line Example

```bash
python Speech_To_Text.py --file video.mp4 --model small --lang en
```

### CLI Options

| Flag            | Description                                                |
| --------------- | ---------------------------------------------------------- |
| `--file`, `-f`  | Input audio/video file path                                |
| `--model`, `-m` | Whisper model (`tiny`, `base`, `small`, `medium`, `large`) |
| `--lang`, `-l`  | Force language (optional)                                  |
| `--out`, `-o`   | Custom output directory (default = script folder)          |

---

## 📂 Output Example

```
movie.mp4
 ├─ movie.srt
 ├─ movie.vtt
 └─ movie.txt
```

---

## 🧠 Whisper Model Guide

| Model                 | Speed | Accuracy | Recommended For              |
| --------------------- | ----- | -------- | ---------------------------- |
| `tiny` / `base`       | ⚡⚡⚡   | ⭐⭐       | Fastest, notes, drafts       |
| `small` (default)     | ⚡⚡    | ⭐⭐⭐⭐     | Best overall CPU balance     |
| `medium`              | ⚡     | ⭐⭐⭐⭐⭐    | High-quality transcription   |
| `large-v2 / large-v3` | 🐢    | ⭐⭐⭐⭐⭐⭐   | Best quality, slowest on CPU |

---

## ✅ Why This Tool?

* No API keys or cloud accounts
* Works offline — **ideal for private recordings**
* Handles media files automatically
* Accurate timestamped subtitles
* Drop-in CLI and GUI workflow

---

## 🗺️ Roadmap

* [ ] Progress bar GUI
* [ ] Batch folder transcription
* [ ] Subtitle hard-burn into video
* [ ] Paragraph-formatted transcript mode
* [ ] Speaker diarization (label speakers)

---

## ❤️ Credits

* [OpenAI Whisper](https://github.com/openai/whisper)
* [Faster-Whisper](https://github.com/guillaumekln/faster-whisper)
* FFmpeg project

---

## 📜 License

MIT License — free to use, modify, and distribute.

---


