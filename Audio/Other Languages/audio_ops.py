import os
from pydub import AudioSegment

def attenuate_audio(audio_path: str, attenuation_db: int) -> AudioSegment:
    """Reduces the volume of the audio file by a given decibel value."""
    audio = AudioSegment.from_file(audio_path)
    return audio - attenuation_db

def generate_sequences(shock: AudioSegment, no_shock: AudioSegment, beat: AudioSegment) -> dict[str, AudioSegment]:
    """Generates audio sequences in three specified orders."""
    return {
        "SNS": shock + beat + no_shock + beat + shock + beat,
        "NSN": no_shock + beat + shock + beat + no_shock + beat,
        "SNN": shock + beat + no_shock + beat + no_shock + beat
    }

def process_language_audio(language_dir: str, beat_path: str, output_dir: str, 
                           attenuation_languages: list[str], attenuation_db: int = 3) -> None:
    # Load the beat audio
    beat = AudioSegment.from_file(beat_path)

    # Create main output directory
    os.makedirs(output_dir, exist_ok=True)

    # Initialize counter for filenames
    file_counter = 7

    # Iterate over language directories
    for idx, language in enumerate(sorted(os.listdir(language_dir)), start=2):
        lang_path = os.path.join(language_dir, language)

        if os.path.isdir(lang_path):
            shock_path = None
            no_shock_path = None

            # Find shock and no_shock files with supported extensions
            for file_name in os.listdir(lang_path):
                if file_name.startswith("shock") and file_name.split(".")[-1] in ["mp3", "m4a", "ogg"]:
                    shock_path = os.path.join(lang_path, file_name)
                if file_name.startswith("no_shock") and file_name.split(".")[-1] in ["mp3", "m4a", "ogg"]:
                    no_shock_path = os.path.join(lang_path, file_name)

            # Ensure both shock and no_shock files exist
            if shock_path and no_shock_path:
                shock = AudioSegment.from_file(shock_path)
                no_shock = AudioSegment.from_file(no_shock_path)

                # Attenuate audio if the language matches specific criteria
                if any(lang in language.lower() for lang in attenuation_languages):
                    shock = attenuate_audio(shock_path, attenuation_db)
                    no_shock = attenuate_audio(no_shock_path, attenuation_db)

                # Generate audio sequences
                sequences = generate_sequences(shock, no_shock, beat)

                # Create language-specific directory
                language_output_dir = os.path.join(output_dir, f"{idx}_{language}")
                os.makedirs(language_output_dir, exist_ok=True)

                # Save sequences to output directory
                for order, audio in sequences.items():
                    filename = f"{file_counter:04d}_{language}_{order}.wav"
                    output_path_main = os.path.join(output_dir, filename)
                    output_path_sub = os.path.join(language_output_dir, filename)

                    audio.set_frame_rate(44100).export(output_path_main, format="wav")
                    audio.set_frame_rate(44100).export(output_path_sub, format="wav")

                    print(f"Generated: {output_path_main}")

                    file_counter += 1
            else:
                print(f"Missing 'shock' or 'no_shock' in {lang_path}")

# Specify paths
parent_dir = "Data"  # Replace with your parent directory path
beat_file = os.path.join(parent_dir, "100bpm.mp3")
output_directory = "outputs"  # Replace with your desired output directory
attenuation_languages = ["telugu", "tamil", "malayalam", "english"]

# Run the function
process_language_audio(parent_dir, beat_file, output_directory, attenuation_languages)