
# 🎙️ Speech-To-Text & Auto-Captions Converter

A powerful Python tool to transcribe **audio or video** into:

✅ **Text** (.txt)
✅ **SRT Subtitles** (.srt)
✅ **WebVTT Captions** (.vtt)

Supports **audio + video**, **auto-speech extraction**, **accurate timestamps**, **Whisper / Faster-Whisper**, and GUI or CLI usage.

Convert **MP3, WAV, MP4, MKV, MOV, M4A, OGG, FLAC** → readable captions or subtitle files.

---

### ✨ Features

| Feature                         | Description                                  |
| ------------------------------- | -------------------------------------------- |
| 🎥 **Video → Audio → Captions** | Auto-extracts audio from video (FFmpeg)      |
| 🎧 **Audio transcription**      | MP3, WAV, OGG, FLAC, M4A etc.                |
| ⚡ **Faster-Whisper support**    | GPU-accelerated real-time transcription      |
| 🧠 **OpenAI Whisper fallback**  | Uses whisper if faster-whisper not installed |
| 📂 **File Picker UI**           | Tkinter file prompt if run without args      |
| 🗣️ **Language selection**      | Auto-detect or force language                |
| 🛠 **CLI usage**                | Scriptable for workflows                     |
| 📜 **Outputs**                  | `.srt`, `.vtt`, `.txt`                       |

---

### 📦 Installation

> Python 3.8+

#### 1️⃣ Create and activate a virtual environment (recommended)

```bash
python -m venv venv
source venv/bin/activate   # macOS/Linux
venv\Scripts\activate      # Windows
```

---

#### 2️⃣ Install required packages

```bash
pip install -U openai-whisper faster-whisper moviepy
```

---

#### 3️⃣ Install FFmpeg

FFmpeg is required for audio extraction.

**Windows (winget)**

```bash
winget install Gyan.FFmpeg
```

**macOS (Homebrew)**

```bash
brew install ffmpeg
```

**Linux (apt)**

```bash
sudo apt install ffmpeg
```

---

### 🚀 Usage

#### **GUI mode (file picker)**

```bash
python Speech_To_Text.py
```

#### **Command line**

```bash
python Speech_To_Text.py --file video.mp4 --model small --lang en
```

#### Options

| Flag              | Description                                                |
| ----------------- | ---------------------------------------------------------- |
| `--file`, `-f`    | Input audio/video file                                     |
| `--model`, `-m`   | Whisper model (`tiny`, `base`, `small`, `medium`, `large`) |
| `--lang`, `-l`    | Force language (optional)                                  |
| `--out-dir`, `-o` | Output folder                                              |

---

### 📝 Example Outputs

```
video.mp4
 ├─ video.srt
 ├─ video.vtt
 └─ video.txt
```

---

### ✅ Recommended Whisper Models

| Speed              | Model              | Notes                       |
| ------------------ | ------------------ | --------------------------- |
| 🔥 Fastest         | `tiny` / `base`    | Good accuracy, fast on CPU  |
| 🎯 Balanced        | `small`            | Best overall choice         |
| 🧠 Highest quality | `medium` / `large` | Slow on CPU, great accuracy |

---

### 🎯 Roadmap

* [ ] Add GUI progress bar
* [ ] Add speaker diarization (who spoke when)
* [ ] Option to burn subtitles into video
* [ ] Support batch folder transcription

---

### ❤️ Credits

* [OpenAI Whisper](https://github.com/openai/whisper)
* [Faster-Whisper](https://github.com/guillaumekln/faster-whisper)
* FFmpeg team

---

### 📄 License

MIT License — free to use, modify, distribute.
