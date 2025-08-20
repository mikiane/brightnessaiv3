import libs.lib__transformers as lib__transformers
import os
import sys

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python script_name.py <input_audio_file>")
        exit(1)

    audio_filename = sys.argv[1]
    
    # Convertissez l'audio en mp3 si nécessaire
    mp3_filename = lib__transformers.convert_to_mp3(audio_filename)

    output_filename = os.path.splitext(audio_filename)[0] + ".txt"

    transcript = lib__transformers.transcribe_audio(mp3_filename)
    lib__transformers.save_transcript(str(transcript), output_filename)

    print(f"Transcription saved to {output_filename}")
