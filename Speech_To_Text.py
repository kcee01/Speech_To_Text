#!/usr/bin/env python3
"""
Whisper CPU Speech-to-Text
Supports: faster-whisper → openai-whisper fallback
Creates: TXT / SRT / VTT
"""

import argparse, os, subprocess, tempfile
from tkinter import Tk, filedialog

# Try import faster-whisper
try:
    from faster_whisper import WhisperModel
    HAS_FASTER = True
except ImportError:
    HAS_FASTER = False

# Try import openai-whisper
try:
    import whisper
    HAS_WHISPER = True
except ImportError:
    HAS_WHISPER = False

### ---------- Utilities ---------- ###

def ffmpeg_exists():
    from shutil import which
    return which("ffmpeg") is not None

def extract_audio(in_file, out_file):
    if not ffmpeg_exists():
        raise RuntimeError("FFmpeg not installed / not in PATH")
    cmd = [
        "ffmpeg", "-y", "-i", in_file,
        "-ar", "16000", "-ac", "1", "-vn", out_file
    ]
    print(f"🔊 Extracting audio → {out_file}")
    subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
    print("✅ Audio extracted")

def ts_srt(t):
    ms = int(t * 1000)
    h = ms // 3600000; ms %= 3600000
    m = ms // 60000;   ms %= 60000
    s = ms // 1000; ms %= 1000
    return f"{h:02}:{m:02}:{s:02},{ms:03}"

def ts_vtt(t):
    ms = int(t * 1000)
    h = ms // 3600000; ms %= 3600000
    m = ms // 60000;   ms %= 60000
    s = ms // 1000; ms %= 1000
    return f"{h:02}:{m:02}:{s:02}.{ms:03}"

### ---------- Save Files ---------- ###

def save_srt(segments, file):
    with open(file, "w", encoding="utf8") as f:
        for i, s in enumerate(segments, 1):
            f.write(f"{i}\n{ts_srt(s['start'])} --> {ts_srt(s['end'])}\n{s['text'].strip()}\n\n")
    print(f"✅ SRT saved → {file}")

def save_vtt(segments, file):
    with open(file, "w", encoding="utf8") as f:
        f.write("WEBVTT\n\n")
        for s in segments:
            f.write(f"{ts_vtt(s['start'])} --> {ts_vtt(s['end'])}\n{s['text'].strip()}\n\n")
    print(f"✅ VTT saved → {file}")

def save_txt(segments, file):
    with open(file, "w", encoding="utf8") as f:
        for s in segments:
            f.write(s["text"].strip()+"\n")
    print(f"✅ TXT saved → {file}")

### ---------- Engine Backends ---------- ###

def run_faster(audio, model, lang):
    try:
        import onnxruntime
        vad = True
        print("✅ onnxruntime found → VAD enabled")
    except ImportError:
        vad = False
        print("⚠️ onnxruntime not found → VAD disabled")

    print(f"🚀 Using faster-whisper ({model}) [CPU int8], VAD={vad}")
    fw = WhisperModel(model, device="cpu", compute_type="int8")
    segments=[]

    for s in list(fw.transcribe(audio, language=lang, vad_filter=vad)):
        if vad:
            segments.append({"start": s.start, "end": s.end, "text": s.text})
            print(f"{s.start:.2f}-{s.end:.2f} {s.text[:70]}")
        else:
            try:
                segments.append({"start": s["start"], "end": s["end"], "text": s["text"]})
                print(f"{s['start']:.2f}-{s['end']:.2f} {s['text'][:70]}")
            except (TypeError, KeyError):
                segments.append({"start": 0, "end": 0, "text": str(s)})
                print(f"0.00-0.00 {str(s)[:70]}")
    return segments

def run_whisper(audio, model, lang):
    print(f"🎤 Using openai-whisper ({model})")
    w = whisper.load_model(model)
    result = w.transcribe(audio, language=lang)
    segments=[]
    for s in result.get("segments", []):
        segments.append({"start": s["start"], "end": s["end"], "text": s["text"]})
        print(f"{s['start']:.2f}-{s['end']:.2f} {s['text'][:70]}")
    return segments

### ---------- Master Transcribe ---------- ###

def transcribe(file, model, lang):
    # Always create audio temp folder inside script folder
    script_dir = os.path.dirname(os.path.abspath(__file__))
    audio_dir = os.path.join(script_dir, "audio_temp")
    os.makedirs(audio_dir, exist_ok=True)

    audio = os.path.join(audio_dir, "audio.wav")
    extract_audio(file, audio)

    if HAS_FASTER:
        try:
            return run_faster(audio, model, lang)
        except Exception as e:
            print("⚠️ faster-whisper failed:", e)

    if HAS_WHISPER:
        try:
            return run_whisper(audio, model, lang)
        except Exception as e:
            print("⚠️ openai-whisper failed:", e)

    raise RuntimeError("❌ No working speech-to-text backend installed.")


### ---------- CLI ---------- ###

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-f","--file")
    parser.add_argument("-m","--model", default="small")
    parser.add_argument("-l","--lang", default=None)
    parser.add_argument("-o","--out", default=None)
    args = parser.parse_args()

    if not args.file:
        Tk().withdraw()
        print("📂 Pick file…")
        args.file = filedialog.askopenfilename()
        if not args.file: return

    inp = os.path.abspath(args.file)

    # 🔥 Always save output to script’s folder unless -o is specified
    script_dir = os.path.dirname(os.path.abspath(__file__))
    out = args.out or script_dir
    os.makedirs(out, exist_ok=True)

    base = os.path.splitext(os.path.basename(inp))[0]
    srt = os.path.join(out, f"{base}.srt")
    vtt = os.path.join(out, f"{base}.vtt")
    txt = os.path.join(out, f"{base}.txt")

    print(f"📥 File: {inp}")
    print(f"📤 Output: {out}")
    print(f"🤖 Model: {args.model}")

    segments = transcribe(inp, args.model, args.lang)
    save_srt(segments, srt)
    save_vtt(segments, vtt)
    save_txt(segments, txt)

    print("🎯 Completed!")

if __name__=="__main__":
    main()
