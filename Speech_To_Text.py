# Install required packages first:
# pip install openai-whisper moviepy

import os
from tkinter import Tk, filedialog, messagebox, Toplevel, Label, Button
from tkinter.ttk import Progressbar
import whisper
from moviepy.editor import VideoFileClip
import threading

os.environ["CUDA_VISIBLE_DEVICES"] = ""  # Disable GPU

def generate_subtitles(input_file, progress_window):
    """
    Generates subtitles from a video or audio file and saves them as an SRT file
    in the same folder as the input file.
    """
    try:
        folder = os.path.dirname(input_file)
        base_name = os.path.splitext(os.path.basename(input_file))[0]
        output_srt = os.path.join(folder, base_name + ".srt")
        temp_audio = os.path.join(folder, base_name + "_temp_audio.wav")

        print(f"🎬 Processing: {input_file}")
        print(f"📝 Output file will be: {output_srt}")

        model = whisper.load_model("base")

        if input_file.lower().endswith((".mp4", ".mov", ".avi", ".mkv")):
            video = VideoFileClip(input_file)
            video.audio.write_audiofile(temp_audio, verbose=False, logger=None)
            audio_path = temp_audio
        else:
            audio_path = input_file

        result = model.transcribe(audio_path)

        def format_timestamp(seconds):
            h = int(seconds // 3600)
            m = int((seconds % 3600) // 60)
            s = int(seconds % 60)
            ms = int((seconds - int(seconds)) * 1000)
            return f"{h:02}:{m:02}:{s:02},{ms:03}"

        with open(output_srt, "w", encoding="utf-8") as f:
            for i, segment in enumerate(result["segments"], start=1):
                start = format_timestamp(segment["start"])
                end = format_timestamp(segment["end"])
                text = segment["text"].strip()
                f.write(f"{i}\n{start} --> {end}\n{text}\n\n")

        print(f"✅ Subtitles saved as: {output_srt}")

        if os.path.exists(temp_audio):
            os.remove(temp_audio)

        # Update the progress window to show "Done" and add a button
        for widget in progress_window.winfo_children():
            widget.destroy()

        Label(progress_window, text="✅ Transcription Done!", font=("Arial", 12)).pack(pady=10)
        Button(progress_window, text="Close", command=progress_window.destroy).pack(pady=10)

    except Exception as e:
        messagebox.showerror("Error", str(e))
        progress_window.destroy()

def start_transcription(input_file):
    """Create and display the progress bar window while processing."""
    progress_window = Toplevel()
    progress_window.title("Transcribing...")
    progress_window.geometry("300x100")
    Label(progress_window, text="Transcribing audio, please wait...").pack(pady=10)
    progress_bar = Progressbar(progress_window, mode='indeterminate')
    progress_bar.pack(pady=10, padx=20, fill='x')
    progress_bar.start(10)  # 10ms update interval

    # Run transcription in a separate thread
    thread = threading.Thread(target=generate_subtitles, args=(input_file, progress_window))
    thread.start()

def select_file_and_transcribe():
    """Select file and start transcription with progress bar."""
    root = Tk()
    root.withdraw()
    file_path = filedialog.askopenfilename(
        title="Select a video or audio file",
        filetypes=[
            ("Media files", "*.mp4 *.mov *.avi *.mkv *.mp3 *.wav *.m4a"),
            ("All files", "*.*"),
        ],
    )
    if file_path:
        start_transcription(file_path)
        root.mainloop()  # Keep GUI alive until progress window is closed
    else:
        messagebox.showwarning("No File Selected", "Please select a file to continue.")

if __name__ == "__main__":
    select_file_and_transcribe()
