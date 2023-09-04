"""
SpeechToTextConverter

This module provides a SpeechToTextConverter class with functionalities for converting speech to text.

It includes the following functionalities:
- Converting an audio file to MP3 format
- Splitting an audio file into segments
- Performing speech-to-text conversion using the Whisper ASR API or the Whisper package
- Calculating transcript usage

Usage:
Instantiate the SpeechToTextConverter class with the file URL, model, and API key.
Call the speech_to_text() method to perform speech-to-text conversion and obtain the extracted text.

Example:
converter = SpeechToTextConverter(file_url="audio.wav", model="api", api_key="your_api_key")
transcript = converter.speech_to_text()
print("Extracted Text:", transcript)
audio_minutes, cost = converter.get_transcript_usage()
print("Audio Minutes:", audio_minutes)
print("Total Cost:", cost)
"""
import os
import math
import logging
import shutil
import whisper
from typing import Tuple
from pydub import AudioSegment
import openai

logging.basicConfig(level=logging.INFO)


class SpeechToTextConverter:
    """
    SpeechToTextConverter class provides methods for converting speech to text.

    It uses the OpenAI API for performing speech-to-text conversion.

    Attributes:
        file_url (str): The URL of the audio file to be converted.
        model (str): The OpenAI model to be used for conversion (e.g., "gpt-3.5-turbo").
        api_key (str): The API key for accessing the OpenAI API.
    """

    def __init__(self, file_url: str, model: str, api_key: str):
        """
        Initialize a SpeechToTextConverter instance.

        Args:
            file_url (str): The URL of the audio file to be converted.
            model (str): The OpenAI model to be used for conversion (e.g., "gpt-3.5-turbo").
            api_key (str): The API key for accessing the OpenAI API.
        """
        self.model = model
        self.file_url = file_url
        self.audio_minutes = 0
        openai.api_key = api_key

    @staticmethod
    def _convert_to_mp3(file_path: str, remove_flag: bool = False) -> Tuple[str, bool]:
        """
        Convert an audio file to MP3 format and return the path of the converted file.

        Args:
            file_path (str): The path of the audio file to be converted.
            remove_flag (bool, optional): A flag indicating whether the original file should be removed after conversion. Defaults to False.

        Raises:
            ValueError: If the provided file type is unsupported.

        Returns:
            Tuple[str, bool]: A tuple containing the path of the converted MP3 file and the remove flag.
        """
        try:
            if file_path.lower().endswith((".m4a", ".wav", ".mp4")):
                remove_flag = True
                audio = AudioSegment.from_file(file_path)

                dir_name, base_name = os.path.split(file_path)
                base_name = os.path.splitext(base_name)[0]
                mp3_path = os.path.join(dir_name, base_name + ".mp3")

                audio.export(mp3_path, format="mp3")

                logging.info("Successfully Converted to MP3: %s", mp3_path)
                return mp3_path, remove_flag
            elif file_path.lower().endswith(".mp3"):
                return file_path, remove_flag
            else:
                raise ValueError("Unsupported file type")
        except Exception as error:
            logging.error(str(error))

    @staticmethod
    def _split_audio(file_path: str, duration: int = 900) -> str:
        """
        Split an audio file into segments and save them as MP3 files.

        Args:
            file_path (str): The path of the audio file to be split.
            duration (int, optional): The duration of each audio segment in seconds. Defaults to 900.

        Returns:
            str: The path of the directory containing the split audio segments.
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

    def _clear_tempfile(self, audio_dir, mp3_path, remove_flag):
        """
        Clear temporary audio files and directories.

        Args:
            audio_dir (str): The path of the directory containing temporary audio segment files.
            mp3_path (str): The path of the temporary MP3 audio file.
            remove_flag (bool): A flag indicating whether to remove the MP3 audio file.
        """
        if remove_flag:
            os.remove(mp3_path)
        shutil.rmtree(audio_dir)

    def _call_whisper_api(self, audios_path: str) -> str:
        """
        Perform speech-to-text conversion using the OpenAI Whisper ASR API on a directory of audio segments.

        Args:
            audios_path (str): The path of the directory containing audio segment files.

        Returns:
            str: The extracted text from the transcribed audio segments.
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
        logging.info("Complete speech to text: %s", extracted_text)

        path = os.path.dirname(audios_path)
        base_name = os.path.basename(audios_path).replace("_segments", "")
        transcriptions_path = os.path.join(path, base_name + "_transcript.txt")
        with open(transcriptions_path, "w", encoding="utf-8") as file:
            file.write(extracted_text)

        return extracted_text

    def _call_whisper_oss(self, audio_path: str) -> str:
        """
        Perform speech-to-text conversion using the Open Speech Service (OSS) Whisper ASR model on an audio file.

        Args:
            audio_path (str): The path of the audio file to be transcribed.

        Returns:
            str: The extracted text from the transcribed audio.
        """
        try:
            model = whisper.load_model(self.model)
            result = model.transcribe(audio_path)
            transcriptions = result["text"]
            logging.info("Complete speech to text: %s", transcriptions)
            path = os.path.dirname(audio_path)
            base_name = os.path.basename(audio_path)
            file_name = os.path.splitext(base_name)[0]
            transcript_path = os.path.join(path, f"{file_name}_transcript.txt")
            with open(transcript_path, "w", encoding="utf-8") as file:
                file.write(transcriptions)
            return transcriptions
        except Exception as error:
            logging.error("Error occurred during transcription: %s", str(error))
            raise

    def get_audio_minutes(self) -> int:
        """Calculate the duration of an audio file in minutes.

        Args:
            None

        Raises:
            FileNotFoundError: If the specified audio file cannot be found.

        Returns:
            int: The duration of the audio file in minutes.
        """
        try:
            audio = AudioSegment.from_file(self.file_url)
        except FileNotFoundError as error:
            raise FileNotFoundError("Can't found audio file.") from error

        duration_seconds = len(audio) / 1000
        duration_minutes = math.ceil(duration_seconds / 60)
        return duration_minutes

    def get_transcript_cost(self) -> float:
        """Calculate the transcript usage.

        Returns:
            Tuple[float, float]: A tuple containing the audio minutes
            and the total cost.
        """
        return self.audio_minutes * 0.006

    def speech_to_text(self) -> str:
        """
        Perform speech-to-text conversion using either the Whisper ASR API or the Whisper package.

        Returns:
            str: The extracted text from the transcribed audio.
        """
        if self.model == "whisper-1":
            logging.info("Use whisper api")
            mp3_path, remove_flag = self._convert_to_mp3(self.file_url)
            audio_path = self._split_audio(mp3_path)
            transcript = self._call_whisper_api(audio_path)
            self.audio_minutes = self.get_audio_minutes()
            self._clear_tempfile(audio_path, mp3_path, remove_flag)
            return transcript
        logging.info("Use whisper package")
        return self._call_whisper_oss(self.file_url)
