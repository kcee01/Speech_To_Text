#!/usr/bin/env python3
"""
speech_to_captions.py

Usage examples:
    python speech_to_captions.py            # interactive file picker
    python speech_to_captions.py --file video.mp4 --model small --lang en

Requirements:
- ffmpeg installed and on PATH (for extracting audio from video)
- Either faster-whisper (recommended) or openai-whisper installed:
    pip install faster-whisper
  or
    pip install openai-whisper
- moviepy (optional) if you want to fallback to it for extraction:
    pip install moviepy
"""

import argparse
import os
import subprocess
import sys
import tempfile
from tkinter import Tk, filedialog
from pathlib import Path
from typing import List

# Try faster_whisper first (preferred for speed); fall back to openai-whisper
USE_FASTER_WHISPER = False
MODEL = None
try:
    from faster_whisper import WhisperModel
    USE_FASTER_WHISPER = True
except Exception:
    try:
        import whisper  # openai-whisper
    except Exception:
        whisper = None

def extract_audio_from_video(input_path: str, out_path: str):
    """
    Extract audio using ffmpeg. Overwrites out_path if exists.
    Requires ffmpeg installed in PATH.
    """
    if not shutil_which("ffmpeg"):
        raise RuntimeError("ffmpeg not found on PATH. Please install ffmpeg.")
    cmd = [
        "ffmpeg",
        "-y",  # overwrite
        "-i", input_path,
        "-vn",  # no video
        "-acodec", "pcm_s16le",  # WAV PCM
        "-ar", "16000",  # sample rate 16k
        "-ac", "1",  # mono
        out_path
    ]
    print(f"🔊 Extracting audio with ffmpeg -> {out_path}")
    completed = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if completed.returncode != 0:
        # Show ffmpeg stderr for debugging
        print("ffmpeg failed:\n", completed.stderr.decode(errors="ignore"))
        raise RuntimeError("ffmpeg failed to extract audio.")
    print("✅ Audio extracted.")

def shutil_which(name):
    """Simple wrapper for shutil.which to avoid import at top (compat)."""
    try:
        from shutil import which
        return which(name)
    except Exception:
        return None

def format_timestamp_srt(seconds: float) -> str:
    """
    Format seconds to SRT timestamp: "HH:MM:SS,mmm"
    """
    ms = int(round(seconds * 1000))
    h = ms // (3600 * 1000)
    ms -= h * 3600 * 1000
    m = ms // (60 * 1000)
    ms -= m * 60 * 1000
    s = ms // 1000
    ms -= s * 1000
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"

def format_timestamp_vtt(seconds: float) -> str:
    """
    Format seconds to VTT timestamp: "HH:MM:SS.mmm"
    """
    ms = int(round(seconds * 1000))
    h = ms // (3600 * 1000)
    ms -= h * 3600 * 1000
    m = ms // (60 * 1000)
    ms -= m * 60 * 1000
    s = ms // 1000
    ms -= s * 1000
    return f"{h:02d}:{m:02d}:{s:02d}.{ms:03d}"

def write_srt(segments: List[dict], out_srt: str):
    """
    segments: list of dicts with keys 'start', 'end', 'text'
    """
    with open(out_srt, "w", encoding="utf-8") as f:
        for i, seg in enumerate(segments, start=1):
            start = format_timestamp_srt(seg["start"])
            end = format_timestamp_srt(seg["end"])
            # strip leading/trailing whitespace and replace newlines
            text = seg["text"].strip().replace("\n", " ")
            f.write(f"{i}\n{start} --> {end}\n{text}\n\n")
    print(f"✅ SRT saved: {out_srt}")

def write_vtt(segments: List[dict], out_vtt: str):
    with open(out_vtt, "w", encoding="utf-8") as f:
        f.write("WEBVTT\n\n")
        for seg in segments:
            start = format_timestamp_vtt(seg["start"])
            end = format_timestamp_vtt(seg["end"])
            text = seg["text"].strip().replace("\n", " ")
            f.write(f"{start} --> {end}\n{text}\n\n")
    print(f"✅ VTT saved: {out_vtt}")

def write_txt(segments: List[dict], out_txt: str):
    with open(out_txt, "w", encoding="utf-8") as f:
        for seg in segments:
            f.write(seg["text"].strip() + "\n")
    print(f"✅ TXT saved: {out_txt}")

def transcribe_with_faster_whisper(audio_path: str, model_size: str, language: str = None):
    """
    Returns list of segments: [{'start': float, 'end': float, 'text': str}, ...]
    """
    print(f"🛰️ Using faster-whisper model: {model_size}")
    # Let faster_whisper auto-select device; user can set environment variables if desired
    model = WhisperModel(model_size, device="auto", compute_type="float16")
    segments_all = []
    # transcribe returns iterator of segments
    for segment in model.transcribe(audio_path, language=language, vad_filter=True):
        # segment has start, end, text
        segments_all.append({"start": float(segment.start), "end": float(segment.end), "text": segment.text})
        print(f"⏱ {segment.start:.2f}-{segment.end:.2f}: {segment.text[:80]}")
    return segments_all

def transcribe_with_whisper(audio_path: str, model_size: str, language: str = None):
    """
    Use openai-whisper (whisper package)
    Returns list of segments
    """
    print(f"🛰️ Using whisper (openai-whisper) model: {model_size}")
    model = whisper.load_model(model_size)
    # the transcribe call returns a dict with 'segments'
    result = model.transcribe(audio_path, language=language, verbose=False)
    segments_all = []
    for seg in result.get("segments", []):
        segments_all.append({"start": float(seg["start"]), "end": float(seg["end"]), "text": seg["text"]})
        print(f"⏱ {seg['start']:.2f}-{seg['end']:.2f}: {seg['text'][:80]}")
    return segments_all

def transcribe(audio_or_video_path: str, model_size: str = "small", language: str = None):
    """
    Orchestrates audio extraction (if video) and transcription.
    Returns list of segments.
    """
    p = Path(audio_or_video_path)
    if not p.exists():
        raise FileNotFoundError(f"Input file not found: {audio_or_video_path}")

    suffix = p.suffix.lower()
    # audio formats supported by ffmpeg: .mp3 .wav .m4a .aac .flac etc.
    audio_exts = {'.mp3', '.wav', '.m4a', '.aac', '.flac', '.ogg', '.wma'}
    work_audio = None
    temp_dir = tempfile.mkdtemp(prefix="tts_transcribe_")
    try:
        if suffix in audio_exts:
            # use it directly (ensure compatible format for model)
            # convert to WAV 16k mono for best compatibility (optional)
            work_audio = os.path.join(temp_dir, "input.wav")
            cmd = [
                "ffmpeg", "-y", "-i", str(p),
                "-ac", "1",
                "-ar", "16000",
                "-vn",
                work_audio
            ]
            if not shutil_which("ffmpeg"):
                raise RuntimeError("ffmpeg not found on PATH. Please install ffmpeg.")
            print(f"🔊 Normalizing audio with ffmpeg -> {work_audio}")
            subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
        else:
            # assume video, extract audio
            work_audio = os.path.join(temp_dir, "extracted.wav")
            extract_audio_from_video(str(p), work_audio)

        # choose transcription backend
        if USE_FASTER_WHISPER:
            segments = transcribe_with_faster_whisper(work_audio, model_size, language)
        else:
            if whisper is None:
                raise RuntimeError("No whisper backend available. Install faster-whisper or openai-whisper.")
            segments = transcribe_with_whisper(work_audio, model_size, language)

        return segments

    finally:
        # we won't delete temp_dir so user can inspect if needed
        pass

def main():
    parser = argparse.ArgumentParser(description="Convert audio/video → captions (SRT/VTT/TXT)")
    parser.add_argument("--file", "-f", help="Input audio/video file")
    parser.add_argument("--model", "-m", default="small", help="Whisper model size (tiny, base, small, medium, large)")
    parser.add_argument("--lang", "-l", default=None, help="Language code (e.g. en). Auto-detect if omitted.")
    parser.add_argument("--out-dir", "-o", default=None, help="Output directory (default: same folder as input)")
    args = parser.parse_args()

    input_path = args.file
    if not input_path:
        # GUI picker
        root = Tk(); root.withdraw()
        print("📂 Pick an audio or video file...")
        input_path = filedialog.askopenfilename(title="Select audio/video",
                                                filetypes=[("Media files", "*.mp3 *.wav *.m4a *.mp4 *.mkv *.mov *.avi *.flac *.ogg *.webm"),
                                                           ("All files", "*.*")])
        root.destroy()
        if not input_path:
            print("❌ No file selected. Exiting.")
            return

    input_path = os.path.abspath(input_path)
    out_dir = args.out_dir or os.path.dirname(input_path)
    os.makedirs(out_dir, exist_ok=True)

    base_name = os.path.splitext(os.path.basename(input_path))[0]
    srt_path = os.path.join(out_dir, f"{base_name}.srt")
    vtt_path = os.path.join(out_dir, f"{base_name}.vtt")
    txt_path = os.path.join(out_dir, f"{base_name}.txt")

    print(f"📁 Input: {input_path}")
    print(f"📤 Output dir: {out_dir}")
    print(f"🧠 Model: {args.model}")
    if args.lang:
        print(f"🌐 Language: {args.lang} (forced)")

    try:
        segments = transcribe(input_path, model_size=args.model, language=args.lang)
        if not segments:
            print("⚠️ No segments returned from transcription.")
            return
        write_srt(segments, srt_path)
        write_vtt(segments, vtt_path)
        write_txt(segments, txt_path)
        print("\n🎉 Transcription + captions complete.")
        print(f"• SRT: {srt_path}")
        print(f"• VTT: {vtt_path}")
        print(f"• TXT: {txt_path}")
    except Exception as e:
        print("❌ Error during transcription:", e)
        sys.exit(1)

if __name__ == "__main__":
    main()
