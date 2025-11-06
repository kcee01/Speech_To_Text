# Install required packages first:
# pip install openai-whisper moviepy

import os
from tkinter import Tk, filedialog, messagebox
import whisper
from moviepy.editor import VideoFileClip

os.environ["CUDA_VISIBLE_DEVICES"] = ""  # Disable GPU

def generate_subtitles(input_file):
    """
    Generates subtitles from a video or audio file and saves them as an SRT file
    in the same folder as the input file.
    """
    # Get the folder and base name
    folder = os.path.dirname(input_file)
    base_name = os.path.splitext(os.path.basename(input_file))[0]
    output_srt = os.path.join(folder, base_name + ".srt")
    temp_audio = os.path.join(folder, base_name + "_temp_audio.wav")

    print(f"🎬 Processing: {input_file}")
    print(f"📝 Output file will be: {output_srt}")

    # Load Whisper model (choose "base" for balance)
    model = whisper.load_model("base")

    # Extract audio if input is a video
    if input_file.lower().endswith((".mp4", ".mov", ".avi", ".mkv")):
        video = VideoFileClip(input_file)
        video.audio.write_audiofile(temp_audio, verbose=False, logger=None)
        audio_path = temp_audio
    else:
        audio_path = input_file

    # Transcribe audio
    result = model.transcribe(audio_path)

    # Helper for timestamp formatting
    def format_timestamp(seconds):
        h = int(seconds // 3600)
        m = int((seconds % 3600) // 60)
        s = int(seconds % 60)
        ms = int((seconds - int(seconds)) * 1000)
        return f"{h:02}:{m:02}:{s:02},{ms:03}"

    # Write SRT file next to original file
    with open(output_srt, "w", encoding="utf-8") as f:
        for i, segment in enumerate(result["segments"], start=1):
            start = format_timestamp(segment["start"])
            end = format_timestamp(segment["end"])
            text = segment["text"].strip()
            f.write(f"{i}\n{start} --> {end}\n{text}\n\n")

    print(f"✅ Subtitles saved as: {output_srt}")

    # Cleanup temporary audio
    if os.path.exists(temp_audio):
        os.remove(temp_audio)

def select_file():
    """Open file dialog to select a video or audio file."""
    root = Tk()
    root.withdraw()
    file_path = filedialog.askopenfilename(
        title="Select a video or audio file",
        filetypes=[
            ("Media files", "*.mp4 *.mov *.avi *.mkv *.mp3 *.wav *.m4a"),
            ("All files", "*.*"),
        ],
    )
    root.destroy()
    return file_path

if __name__ == "__main__":
    file_path = select_file()
    if file_path:
        generate_subtitles(file_path)
        output_path = os.path.splitext(file_path)[0] + ".srt"
        messagebox.showinfo(
            "Done",
            f"✅ Subtitles generated successfully!\n\nSaved at:\n{output_path}",
        )
    else:
        messagebox.showwarning("No File Selected", "Please select a file to continue.")
