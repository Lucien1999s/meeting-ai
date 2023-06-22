"""
This module provides a SpeechToTextConverter class for converting 
speech to text using the OpenAI API.

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
import logging
from typing import Tuple
from pydub import AudioSegment
import openai
import whisper
from dotenv import load_dotenv

load_dotenv()
logging.basicConfig(level=logging.INFO)

class SpeechToTextConverter:
    """
    SpeechToTextConverter class provides methods for converting speech to text.

    It uses the OpenAI API for performing speech-to-text conversion.

    Attributes:
        model (str): The model used for transcription.
    """

    def __init__(self):
        """
        Initializes a new instance of the SpeechToTextConverter class.

        The constructor sets the default model to "whisper-1" and loads 
        the OpenAI API key from the environment.
        """
        self.model = "whisper-1"
        self.audio_minutes = 0
        openai.api_key = os.environ.get("OPENAI_API_KEY")

    def _convert_to_mp3(self, file_path: str) -> str:
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

                logging.info("Converted to MP3: %s", mp3_path)
                file_path = mp3_path
        except FileNotFoundError:
            logging.error("File not found: %s", file_path)
        except OSError as error:
            logging.error("An error occurred while converting to MP3: %s", str(error))
        except ValueError as error:
            logging.error("An error occurred while converting to MP3: %s", str(error))

        logging.info("Successfully converted to MP3")
        return file_path


    @staticmethod
    def _split_audio(file_path: str, duration: int = 900) -> str:
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

        logging.info("Audio split completely. Saved in: %s", output_dir)
        return output_dir

    def _call_whisper_api(self, audios_path: str) -> str:
        """
        Performs speech-to-text conversion on segmented audio files and generates a text file.

        Args:
            audios_path (str): The path of the directory containing the segmented audio files.

        Returns:
            str: The extracted text from all transcriptions.
        """
        path = os.path.dirname(audios_path)
        base_name = os.path.basename(audios_path).replace("_segments", "")
        transcriptions_path = os.path.join(path, base_name + "_transcript.txt")

        transcriptions = []

        for file_name in sorted(os.listdir(audios_path)):
            if file_name.endswith(".mp3"):
                input_file = os.path.join(audios_path, file_name)
                with open(input_file, "rb") as audio_file:
                    transcript = openai.Audio.transcribe(self.model, audio_file)
                    transcription = transcript["text"].replace(" ", "\n")
                    transcriptions.append(transcription)

        with open(transcriptions_path, "w", encoding="utf-8") as file:
            file.write("\n".join(transcriptions))

        extracted_text = "\n".join(transcriptions)
        logging.info("Complete speech to text: %s", extracted_text)
        return extracted_text

    def _call_whisper_package(self, audio_path: str) -> str:
        """
        Transcribes the audio file using the Whisper package.

        Args:
            audio_path (str): The path to the audio file.

        Returns:
            str: The transcribed text.
        """
        try:
            model = whisper.load_model("small")
            transcript = model.transcribe(audio_path)
            logging.info("Transcript: %s", transcript)
            return transcript
        except Exception as error:
            logging.error("Error occurred during transcription: %s", str(error))
            raise


    def _calculate_audio_minutes(self, audio_path: str) -> int:
        """Calculate the duration of an audio file in minutes.

        Args:
            audio_path (str): The path of the audio file.

        Raises:
            FileNotFoundError: If the specified audio file cannot be found.

        Returns:
            int: The duration of the audio file in minutes.
        """
        try:
            audio = AudioSegment.from_file(audio_path)
        except FileNotFoundError as error:
            raise FileNotFoundError("Can't found audio file.") from error

        duration_seconds = len(audio) / 1000
        duration_minutes = math.ceil(duration_seconds / 60)
        return duration_minutes

    def get_transcript_usage(self) -> Tuple[float, float]:
        """Calculate the transcript usage.

        Returns:
            Tuple[float, float]: A tuple containing the audio minutes and the total cost.
        """
        audio_minutes = self.audio_minutes
        cost = audio_minutes * 0.006

        return audio_minutes, cost

    def speech_to_text(self, file_path: str, use_package: bool) -> str:
        """
        Performs speech-to-text conversion on an audio file.

        Args:
            file_path (str): The path of the audio file to be converted.

        Returns:
            str: The transcript content.
        """
        if use_package:
            logging.info("Use whisper package")
            return self._call_whisper_package(file_path)
        
        logging.info("Use whisper api")
        mp3_path = self._convert_to_mp3(file_path)
        audio_path = self._split_audio(mp3_path)
        transcript = self._call_whisper_api(audio_path)
        self.audio_minutes = self._calculate_audio_minutes(mp3_path)
        
        return transcript
