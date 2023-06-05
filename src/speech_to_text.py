"""
This module provides a SpeechToTextConverter class for converting speech to text using the OpenAI API.

It includes the following functionalities:
- Conversion of audio files to MP3 format
- Splitting audio files into segments
- Performing speech-to-text conversion on segmented audio files

Usage:
1. Initialize the SpeechToTextConverter object.
2. Call the `speech_to_text_go` method to convert an audio file to text.

Example:
    converter = SpeechToTextConverter()
    text_result = converter.speech_to_text_go(file_path)

"""
import os
import math
from pydub import AudioSegment
import openai
from dotenv import load_dotenv

load_dotenv()


class SpeechToTextConverter:
    """
    SpeechToTextConverter class provides methods for converting speech to text.

    It uses the OpenAI API for performing speech-to-text conversion.

    Attributes:
        model (str): The model used for transcription.
    """

    def __init__(self):
        self.model = "whisper-1"
        openai.api_key = os.environ.get("OPENAI_API_KEY")

    def _convert_to_mp3(self, file_path):
        """
        Converts an audio file to MP3 format.

        Args:
            file_path (str): The path of the audio file to be converted.

        Returns:
            file_path (str): The path of the mp3 audio file.

        """
        try:
            if file_path.lower().endswith((".m4a", ".wav")):
                audio = AudioSegment.from_file(file_path)

                dir_name, base_name = os.path.split(file_path)
                base_name = os.path.splitext(base_name)[0]
                mp3_path = os.path.join(dir_name, base_name + ".mp3")

                audio.export(mp3_path, format="mp3")

                print("Converted to MP3:", mp3_path)
                file_path = mp3_path
        except FileNotFoundError:
            print("File not found:", file_path)
        except Exception as e:
            print("An error occurred while converting to MP3:", str(e))

        return file_path

    @staticmethod
    def _split_audio(file_path, duration=900):
        """
        Splits an audio file into segments.

        Args:
            file_path (str): The path of the audio file to be split.
            duration (int, optional): _description_. Defaults to 900.

        Returns:
            str: The path of the directory containing the segmented audio files.

        """
        audio_data = AudioSegment.from_file(file_path, format="mp3")
        num_segments = math.ceil(audio_data.duration_seconds / duration)

        output_dir = os.path.join(
            os.path.dirname(file_path),
            f"{os.path.splitext(os.path.basename(file_path))[0]}_segments",
        )
        os.makedirs(output_dir, exist_ok=True)

        for i in range(num_segments):
            start = i * duration * 1000
            end = (i + 1) * duration * 1000
            if end > len(audio_data):
                end = len(audio_data)
            segment = audio_data[start:end]
            output_path = os.path.join(output_dir, f"segment{i+1}.mp3")
            segment.export(output_path, format="mp3")

        print("Audio split completely. Saved in:", output_dir)
        return output_dir

    def _speech_to_text(self, audios_path):
        """
        Performs speech-to-text conversion on segmented audio files and generates a text file.

        Args:
            audios_path (str): The path of the directory containing the segmented audio files.

        Returns:
            str: The extracted text from all transcriptions.

        """
        transcriptions = []

        for file_name in sorted(os.listdir(audios_path)):
            if file_name.endswith(".mp3"):
                input_file = os.path.join(audios_path, file_name)
                with open(input_file, "rb") as audio_file:
                    transcript = openai.Audio.transcribe(self.model, audio_file)
                    transcription = transcript["text"].replace(" ", "\n")
                    transcriptions.append(transcription)

        extracted_text = "\n".join(transcriptions)
        print("Complete speech to text")
        return extracted_text

    def speech_to_text_go(self, file_path):
        """
        Performs speech-to-text conversion on an audio file.

        Args:
            file_path (str): The path of the audio file to be converted.

        Returns:
            str: The transcript content.

        """
        mp3_path = self._convert_to_mp3(file_path)
        audio_path = self._split_audio(mp3_path)
        return self._speech_to_text(audio_path)
