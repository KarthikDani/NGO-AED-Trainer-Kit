import os
from pydub import AudioSegment

def attenuate_audio(audio_path, attenuation_db):
    """Reduces the volume of the audio file by a given decibel value."""
    audio = AudioSegment.from_file(audio_path)
    return audio - attenuation_db

def generate_sequences(shock, no_shock, beat):
    """Generates audio sequences in three specified orders."""
    return {
        "SNS": shock + beat + no_shock + beat + shock + beat,
        "NSN": no_shock + beat + shock + beat + no_shock + beat,
        "SNN": shock + beat + no_shock + beat + no_shock + beat
    }

def process_language_audio(language_dir, beat_path, output_dir, attenuation_languages, 
                           attenuation_db=3):
    # Load the beat audio
    beat = AudioSegment.from_file(beat_path)

    # Iterate over language directories
    for language in os.listdir(language_dir):
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

                # Save sequences to output directory
                for order, audio in sequences.items():
                    output_path = os.path.join(output_dir, f"{language}_{order}.mp3")
                    audio.export(output_path, format="mp3")
                    print(f"Generated: {output_path}")
            else:
                print(f"Missing 'shock' or 'no_shock' in {lang_path}")

# Specify paths
parent_dir = "."  # Replace with your parent directory path
beat_file = os.path.join(parent_dir, "100bpm.mp3")
output_directory = "outputs"  # Replace with your desired output directory
attenuation_languages = ["telugu", "tamil", "malayalam", "english"]

# Create output directory if it doesn't exist
os.makedirs(output_directory, exist_ok=True)

# Run the function
process_language_audio(parent_dir, beat_file, output_directory, attenuation_languages)
