# Install required packages first:
# pip install openai-whisper moviepy

import os
from tkinter import Tk, filedialog, messagebox, Toplevel, Label, Button
from tkinter.ttk import Progressbar
import whisper
from moviepy.editor import VideoFileClip
import threading
import subprocess

os.environ["CUDA_VISIBLE_DEVICES"] = ""  # Force CPU

def format_timestamp(seconds):
    # Round to nearest millisecond to avoid cumulative truncation drift
    total_ms = int(round(seconds * 1000))
    h = total_ms // 3600000
    m = (total_ms % 3600000) // 60000
    s = (total_ms % 60000) // 1000
    ms = total_ms % 1000
    return f"{h:02}:{m:02}:{s:02},{ms:03}"

def extract_audio_ffmpeg(input_file, output_audio):
    """Extract audio with FFmpeg to preserve original timing and sampling.

    Uses mono, 16 kHz WAV which works well with Whisper models.
    """
    cmd = [
        "ffmpeg",
        "-y",  # overwrite
        "-i",
        input_file,
        "-vn",
        "-ac",
        "1",
        "-ar",
        "16000",
        output_audio,
    ]
    # Let CalledProcessError bubble up to the caller for GUI error handling
    subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

def burn_subtitles(video_file, srt_file, output_file):
    """Burn SRT subtitles into video using FFmpeg."""
    cmd = [
        "ffmpeg",
        "-i", video_file,
        "-vf", f"subtitles={srt_file}",
        "-c:a", "copy",
        output_file
    ]
    subprocess.run(cmd, check=True)

def generate_subtitles(input_file, progress_window, burn=False):
    """Generate bilingual subtitles (auto-detect English + Setswana)"""
    try:
        folder = os.path.dirname(input_file)
        base_name = os.path.splitext(os.path.basename(input_file))[0]
        temp_audio = os.path.join(folder, base_name + "_temp_audio.wav")
        output_srt = os.path.join(folder, base_name + "_bilingual.srt")
        output_video = os.path.join(folder, base_name + "_subtitled.mp4")

        print(f"🎬 Processing: {input_file}")

        if input_file.lower().endswith((".mp4", ".mov", ".avi", ".mkv")):
            # Prefer FFmpeg extraction to preserve exact timing and avoid MoviePy re-encoding quirks
            try:
                extract_audio_ffmpeg(input_file, temp_audio)
            except subprocess.CalledProcessError as e:
                raise RuntimeError("FFmpeg audio extraction failed. Is FFmpeg installed and on PATH?") from e
            audio_path = temp_audio
        else:
            audio_path = input_file

        model = whisper.load_model("medium")  # high accuracy

        result = model.transcribe(audio_path, language=None, temperature=[0.0, 0.2], beam_size=10)

        with open(output_srt, "w", encoding="utf-8") as f:
            for i, segment in enumerate(result["segments"], start=1):
                start = format_timestamp(segment["start"])
                end = format_timestamp(segment["end"])
                text = segment["text"].strip()
                # optional: flag low-confidence
                if segment.get("avg_logprob", -1) < -1.0:
                    text = f"[??] {text}"
                f.write(f"{i}\n{start} --> {end}\n{text}\n\n")

        print(f"✅ Subtitles saved as: {output_srt}")

        if burn:
            burn_subtitles(input_file, output_srt, output_video)
            print(f"🎥 Subtitled video saved as: {output_video}")

        if os.path.exists(temp_audio):
            os.remove(temp_audio)

        # Update GUI
        for widget in progress_window.winfo_children():
            widget.destroy()
        Label(progress_window, text="✅ Transcription Done!", font=("Arial", 12)).pack(pady=10)
        Button(progress_window, text="Close", command=progress_window.destroy).pack(pady=10)

    except Exception as e:
        messagebox.showerror("Error", str(e))
        progress_window.destroy()

def start_transcription(input_file):
    progress_window = Toplevel()
    progress_window.title("Transcribing...")
    progress_window.geometry("300x120")
    Label(progress_window, text="Transcribing audio, please wait...").pack(pady=10)
    progress_bar = Progressbar(progress_window, mode='indeterminate')
    progress_bar.pack(pady=10, padx=20, fill='x')
    progress_bar.start(10)

    # Ask user if they want to burn subtitles into video
    burn = messagebox.askyesno("Burn Subtitles?", "Do you want to burn the subtitles into the video?")
    thread = threading.Thread(target=generate_subtitles, args=(input_file, progress_window, burn))
    thread.start()

def select_file_and_transcribe():
    root = Tk()
    root.withdraw()
    file_path = filedialog.askopenfilename(
        title="Select a video or audio file",
        filetypes=[("Media files", "*.mp4 *.mov *.avi *.mkv *.mp3 *.wav *.m4a"), ("All files", "*.*")]
    )
    
    if file_path:
        start_transcription(file_path)
        root.mainloop()
    else:
        messagebox.showwarning("No File Selected", "Please select a file to continue.")

if __name__ == "__main__":
    select_file_and_transcribe()
