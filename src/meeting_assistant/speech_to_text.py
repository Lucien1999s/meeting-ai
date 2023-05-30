from pydub import AudioSegment
import openai
import math
import os
from dotenv import load_dotenv

load_dotenv()


class SpeechToTextConverter:
    def __init__(self):
        self.model = "whisper-1"
        openai.api_key = os.environ.get("OPENAI_API_KEY")

    def convert_to_mp3(self, file_path):
        """
        Converts an audio file to MP3 format.

        Args:
            file_path (str): The path of the audio file to be converted.
        
        Returns:
            None. Changes are made directly. 

        """

    def split_audio(self, file_path, duration=900):
        """
        Splits an audio file into segments.

        Args:
            file_path (str): The path of the audio file to be split.
            duration (int, optional): _description_. Defaults to 900.

        Returns:
            str: The path of the directory containing the segmented audio files.

        """

    def speech_to_text(self, audios_path):
        """
        Performs speech-to-text conversion on segmented audio files and generates a text file.

        Args:
            audios_path (str): The path of the directory containing the segmented audio files.

        Returns:
            str: The path of the generated text file.

        """

    def speech_to_text_go(self, file_path):
        """
        Performs speech-to-text conversion on an audio file.

        Args:
            file_path (str): The path of the audio file to be converted.

        Returns:
            str: The path of the generated text file.
            
        """
