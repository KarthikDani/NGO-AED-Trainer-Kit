import os
from pydub import AudioSegment

# Define input and output folders
input_folder = "outputs"
output_folder = "wav_outputs"

# Ensure output folder exists
os.makedirs(output_folder, exist_ok=True)

# Convert all .mp3 files to .wav
for filename in os.listdir(input_folder):
    if filename.endswith(".mp3"):
        mp3_path = os.path.join(input_folder, filename)
        wav_path = os.path.join(output_folder, f"{os.path.splitext(filename)[0]}.wav")

        # Load and convert
        audio = AudioSegment.from_mp3(mp3_path)
        audio.export(wav_path, format="wav")

        print(f"Converted: {mp3_path} -> {wav_path}")

print("Conversion complete!")
