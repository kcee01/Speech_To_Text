# Install required packages first:
# pip install whisper moviepy
import os
os.environ["CUDA_VISIBLE_DEVICES"] = ""  # Disable GPU
import whisper
from moviepy.editor import VideoFileClip
import os

def generate_subtitles(input_file, output_srt="subtitles.srt"):
    """
    Generates subtitles from video or audio file and saves them in SRT format.
    """
    # Load Whisper model (choose "base" for a balance between speed & accuracy)
    model = whisper.load_model("base")

    # Extract audio if input is a video
    if input_file.lower().endswith((".mp4", ".mov", ".avi", ".mkv")):
        video = VideoFileClip(input_file)
        audio_path = "temp_audio.wav"
        video.audio.write_audiofile(audio_path, verbose=False, logger=None)
    else:
        audio_path = input_file

    # Transcribe audio
    result = model.transcribe(audio_path)

    # Convert seconds to SRT timestamp
    def format_timestamp(seconds):
        h = int(seconds // 3600)
        m = int((seconds % 3600) // 60)
        s = int(seconds % 60)
        ms = int((seconds - int(seconds)) * 1000)
        return f"{h:02}:{m:02}:{s:02},{ms:03}"

    # Write SRT file
    with open(output_srt, "w", encoding="utf-8") as f:
        for i, segment in enumerate(result["segments"], start=1):
            start = format_timestamp(segment["start"])
            end = format_timestamp(segment["end"])
            text = segment["text"].strip()
            f.write(f"{i}\n{start} --> {end}\n{text}\n\n")

    print(f"✅ Subtitles saved as: {output_srt}")

    # Cleanup temporary audio
    if input_file.lower().endswith((".mp4", ".mov", ".avi", ".mkv")):
        os.remove(audio_path)

# Example usage
if __name__ == "__main__":
    file_path = "example_video.mp4"  # Replace with your video/audio file
    generate_subtitles(file_path)
