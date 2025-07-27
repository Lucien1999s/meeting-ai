"""
This class provides functionality to convert audio files to text using either the OpenAI API or local models.

Raises:
    FileNotFoundError: If the specified audio file cannot be found.

Returns:
    str: The transcription result.

Examples:
    converter = SpeechToTextConverter(
        file_path="YOUR_AUDIO_FILE_PATH",
        api_key="OPENAI_API_KEY",
        model="base",
        output_path="TRANSCRIPT_STORE_PATH",
        save_transcript=True,
        logging_level=logging.CRITICAL
    )
    transcript= converter.speech_to_text()
"""

import os
import math
import logging
import shutil
from typing import Tuple, Optional

import openai
import whisper
from openai import OpenAI
from pydub import AudioSegment


class SpeechToTextConverter:
    """
    This class provides functionality to convert audio files to text using either the OpenAI API or local models.
    """

    def __init__(
        self,
        file_path: str,
        api_key: str,
        output_path: str,
        model: str = "base",
        save_transcript: bool = False,
        logging_level: int = logging.INFO,
    ):
        """
        Initializes the class with the provided parameters.

        Args:
            file_path (str): The path to the audio file to be transcribed.
            api_key (str): The API key for OpenAI.
            output_path (str): The path where the output transcript should be saved.
            model (str, optional): The model to be used for transcription. Defaults to "base".
            save_transcript (bool, optional): If True, the transcript will be saved to the output path. Defaults to False.
            logging_level (int, optional): The level of logging to be used. Defaults to logging.INFO.
        """
        if output_path is None:
            output_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.file_path = file_path
        self.model = model
        self.save_transcript = save_transcript
        self.output_path = output_path
        self.audio_minutes = 0
        openai.api_key = api_key
        logging.basicConfig(level=logging_level)

    def _convert_by_api(self) -> str:
        """
        Converts the speech in the audio file to text using the OpenAI API.

        Returns:
            str: The transcribed text from the audio file.
        """
        # Convert the specified audio file to mp3,
        mp3_path, remove_mp3 = self._convert_to_mp3(self.file_path)
        mp3_dir_path = self._split_audio(mp3_path)

        # Traverse mp3 audio file folder
        client = OpenAI()
        transcript_list = []
        for file_name in sorted(os.listdir(mp3_dir_path)):
            # The audio file currently to be converted
            input_file = os.path.join(mp3_dir_path, file_name)
            # Convert speech to text and add the results to the transcript list
            transcript_list.append(
                client.audio.transcriptions.create(
                    model="whisper-1", file=open(input_file, "rb")
                ).text
            )

        # Merge all results in list
        combined_transcript = "\n".join(transcript_list)
        logging.info("Complete speech to text: %s", combined_transcript)

        # Save the transcription results as txt file
        if self.save_transcript:
            # path = os.path.dirname(mp3_dir_path)
            base_name = os.path.basename(mp3_dir_path).replace("_segments", "")
            transcriptions_path = os.path.join(
                self.output_path, base_name + "_transcript.txt"
            )
            with open(transcriptions_path, "w", encoding="utf-8") as file:
                file.write(combined_transcript)

        # Clear temporary audio files
        self._clear_tempfile(mp3_dir_path, mp3_path, remove_mp3)

        return combined_transcript

    def _convert_by_model(self, model: str) -> str:
        """
        Converts the speech in the audio file to text using the specified model.

        Args:
            model (str): The name of the model to be used for transcription.

        Returns:
            str: The transcribed text from the audio file.

        Raises:
            Exception: If an error occurs during transcription.
        """
        try:
            # Load model data from the folder whisper_model of the same layer
            current_file_path = os.path.dirname(os.path.realpath(__file__))
            model_path = os.path.join(current_file_path, "whisper_model")

            # Use the specified model to convert speech to text
            model = whisper.load_model(model, download_root=model_path)
            result = model.transcribe(self.file_path)
            transcript = result["text"]
            logging.info("Complete speech to text: %s", transcript)

            # Save the transcription results as txt file
            if self.save_transcript:
                # path = os.path.dirname(self.file_path)
                base_name = os.path.basename(self.file_path)
                file_name = os.path.splitext(base_name)[0]
                transcript_path = os.path.join(
                    self.output_path, f"{file_name}_transcript.txt"
                )
                with open(transcript_path, "w", encoding="utf-8") as file:
                    file.write(transcript)

            return transcript
        except Exception as error:
            logging.error("Error occurred during transcription: %s", str(error))
            raise

    def get_audio_usage(self) -> dict:
        """Calculate the duration of an audio file in minutes.

        Args:
            None

        Raises:
            FileNotFoundError: If the specified audio file cannot be found.

        Returns:
            dict: The duration of the audio file in minutes and audio model type.
        """
        try:
            audio = AudioSegment.from_file(self.file_path)
        except FileNotFoundError as error:
            raise FileNotFoundError("Can't found audio file.") from error

        duration_seconds = len(audio) / 1000
        duration_minutes = math.ceil(duration_seconds / 60)
        return {"audio model": self.model, "audio minutes": duration_minutes}

    def speech_to_text(self) -> str:
        """
        Converts speech to text using either the API or local models.

        Args:
            None

        Returns:
            str: The transcription result.

        Raises:
            ValueError: If the model is not 'api' or one of 'tiny', 'base', 'small', 'medium'.
        """
        if self.model == "api":
            logging.info("Converting speech to text using API...")
            return self._convert_by_api()
        elif self.model in ["tiny", "base", "small", "medium"]:
            logging.info(f"Converting speech to text using {self.model} model...")
            return self._convert_by_model(model=self.model)
        else:
            e = f"Invalid model: {self.model}. Model should be 'api' or one of 'tiny', 'base', 'small', 'medium'."
            logging.error(e)
            raise ValueError(e)

    @staticmethod
    def _convert_to_mp3(file_path: str) -> Tuple[Optional[str], bool]:
        """
        Converts a given audio file to MP3 format.

        This method checks if the file exists and is in a supported format. If the file is not in MP3 format, it converts the file to MP3.

        Args:
            file_path (str): The path of the file to be converted.

        Returns:
            Tuple[Optional[str], bool]: A tuple containing the path of the converted MP3 file (or None if the conversion failed), and a boolean indicating whether the original file was converted to MP3.
        """
        remove_mp3 = False

        # Check if the file exists
        if not os.path.isfile(file_path):
            logging.error(f"File does not exist: {file_path}")
            return None, remove_mp3

        # Check if the file is already in mp3 format
        if file_path.lower().endswith(".mp3"):
            logging.info(f"The file is already in MP3 format: {file_path}")
            return file_path, remove_mp3

        # Check if the file is in a supported format
        supported_formats = [".mp4", ".mpeg", ".mpga", ".m4a", ".wav", ".webm"]
        if not any(file_path.lower().endswith(fmt) for fmt in supported_formats):
            logging.error(f"Unsupported file formats: {file_path}")
            return None, remove_mp3

        # Convert files to mp3 format
        try:
            audio = AudioSegment.from_file(file_path)
            mp3_path = os.path.splitext(file_path)[0] + ".mp3"
            audio.export(mp3_path, format="mp3")
        except Exception as e:
            logging.error(f"An error occurred while converting the file: {e}")
            return None, remove_mp3

        logging.info(f"File converted to MP3 format: {mp3_path}")
        return mp3_path, True

    @staticmethod
    def _split_audio(mp3_path: str, duration: int = 900) -> str:
        """
        Split an audio file into segments and save them as MP3 files.

        Args:
            file_path (str): The path of the audio file to be split.
            duration (int, optional): The duration of each audio segment in seconds. Defaults to 900.

        Returns:
            str: The path of the directory containing the split audio segments.
        """
        try:
            audio_data = AudioSegment.from_file(mp3_path, format="mp3")
            num_segments = math.ceil(audio_data.duration_seconds / duration)

            output_dir = os.path.join(
                os.path.dirname(mp3_path),
                f"{os.path.splitext(os.path.basename(mp3_path))[0]}_segments",
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
        except Exception as e:
            logging.error(f"Failed to split audio: {e}")

    @staticmethod
    def _clear_tempfile(audios_dir: str, mp3_path: str, remove_flag: bool) -> None:
        """
        Clear temporary audio files and directories.

        Args:
            audios_dir (str): The path of the directory containing temporary audio segment files.
            mp3_path (str): The path of the temporary MP3 audio file.
            remove_flag (bool): A flag indicating whether to remove the MP3 audio file.

        Returns:
            None
        """
        try:
            if remove_flag:
                os.remove(mp3_path)
                logging.info(f"Successfully removed temporary MP3 file: {mp3_path}")
            shutil.rmtree(audios_dir)
            logging.info(
                f"Successfully removed temporary audio directory: {audios_dir}"
            )
        except Exception as e:
            logging.error(f"Failed to clear temporary files: {e}")
