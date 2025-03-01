import os
from pydub import AudioSegment

def amplify_and_resample(input_dir: str, output_dir: str, amplification_db: int = 5, target_rate: int = 22050) -> None:
    """Amplifies and resamples all .wav files in a directory."""

    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)

    # Process all .wav files
    for file_name in os.listdir(input_dir):
        if file_name.endswith(".wav"):
            input_path = os.path.join(input_dir, file_name)
            output_path = os.path.join(output_dir, file_name)

            # Load and amplify the audio
            audio = AudioSegment.from_wav(input_path)
            amplified_audio = audio + amplification_db

            # Resample to the target rate
            resampled_audio = amplified_audio.set_frame_rate(target_rate)

            # Export the processed audio
            resampled_audio.export(output_path, format="wav")

            print(f"Processed: {output_path}")

# Paths
input_directory = "Data"  # Replace with your input directory
output_directory = "Outputs"  # Replace with your output directory

# Run the function
amplify_and_resample(input_directory, output_directory, amplification_db=10, target_rate=22050)