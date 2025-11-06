Here’s an updated **README** tailored to your current script with the progress bar and GUI improvements:

---

# 🎙️ Speech-To-Text & Auto-Captions Converter

**Local Whisper-powered subtitle generator — Audio & Video → TXT / SRT**

A Python tool to convert **audio or video** into timestamped subtitles (`.srt`) or text (`.txt`), entirely offline.

Supports **MP3, WAV, MP4, MKV, MOV, FLAC, OGG, M4A** and more.

> Output files are saved **in the same folder as the selected file**.

---

## ✨ Features

* 🎥 **Video → Audio → Captions**: Automatically extracts audio using FFmpeg.
* 🎧 **Audio Transcription**: Supports popular formats like MP3, WAV, M4A, FLAC, OGG, AAC.
* 🗂 **GUI File Picker**: Select a file via Tkinter dialog.
* ⚡ **Indeterminate Progress Bar**: Shows live processing status.
* ✅ **Done Button**: Allows closing the progress window when finished.
* 🔐 **Fully Local & Private**: No cloud services or API keys required.

---

## 📦 Requirements

### Python

```
Python 3.8+
```

### Install Dependencies

```bash
pip install openai-whisper moviepy
```

### Install FFmpeg

Required for extracting audio from videos.

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

Simply run:

```bash
python Speech_To_Text.py
```

* A file picker dialog will appear.
* Select your audio or video file.
* A progress bar will appear during transcription.
* When finished, a **Done** message and **Close** button will appear.
* The `.srt` file will be saved in the same folder as the selected file.

### Example Output

```
Screen Recording 2025-11-04 203719.mp4
 └─ Screen Recording 2025-11-04 203719.srt
```

---

## 🧠 Notes

* The SRT file is named **exactly like the input file**, just with `.srt` extension.
* Video files have their audio automatically extracted to a temporary WAV file during processing.
* Whisper’s `base` model is used by default for a good balance of speed and accuracy.
* GPU is disabled by default for maximum compatibility. Modify `os.environ["CUDA_VISIBLE_DEVICES"]` to enable if desired.

---

## ❤️ Credits

* [OpenAI Whisper](https://github.com/openai/whisper)
* [MoviePy](https://zulko.github.io/moviepy/)
* FFmpeg project

---

## 📜 License

MIT License — free to use, modify, and distribute.

---



