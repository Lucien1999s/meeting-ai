"""
This program includes methods for transcribing, summarizing and exporting meeting minutes. 
It converts a voice file into summary meeting minutes through the user's parameter settings.

It uses:
- `SpeechToTextConverter` for transcription
- `ReportGenerator` for summary
- `ReportExporter` for exporting the summary and usage details

Example:
    meeting_ai(
        meeting_name="Team Meeting", 
        file_path="/path/to/audio/file.wav", 
        api_key="your_openai_api_key",  
        audio_model="base", 
        text_model="gpt-3.5-turbo",
        output_path="/path/to/output",
        save_transcript=True,
        show_txt_cost=True
    )
"""

import os
import logging

from src.speech_to_text import SpeechToTextConverter
from src.auto_summarize import ReportGenerator
from src.export_records import ReportExporter

from dotenv import load_dotenv

load_dotenv()


def meeting_ai(
    meeting_name: str,
    file_path: str,
    api_key: str,
    audio_model: str = "base",
    text_model: str = "gpt-3.5-turbo",
    transcript_path: str = None,
    output_path: str = None,
    save_transcript: bool = False,
    show_txt_cost: bool = False,
    logging_level: int = logging.INFO,
):
    """
    Transcribes a meeting, generates a summary report, and exports the results.

    Args:
        meeting_name (str): The name of the meeting.
        file_path (str): The path to the audio file of the meeting.
        api_key (str): The API key for OpenAI.
        audio_model (str, optional): The model to be used for audio transcription. Defaults to "base".
        text_model (str, optional): The model to be used for text generation. Defaults to "gpt-3.5-turbo".
        transcript_path (str): The path where can read transcript from it, and don't need to use SpeechToTextConverter Class.
        output_path (str, optional): The path where the output files should be saved. Defaults to None.
        save_transcript (bool, optional): If True, the transcript will be saved to the output path. Defaults to False.
        show_txt_cost (bool, optional): If True, the cost of text generation will be shown. Defaults to False.
        logging_level (int, optional): The level of logging to be used. Defaults to logging.INFO.
    """

    # Initial variable and settings
    logging.basicConfig(level=logging_level)
    usage = {}

    # Use the SpeechToTextConverter class to convert speech to text
    if transcript_path:
        with open(transcript_path, "r",encoding="utf-8") as file:
            transcript = file.read()
        usage["audio cost"] = {"audio model": None, "audio minutes": 0}
        logging.info(f"Completed read transcript from {transcript_path}")
    else:
        converter = SpeechToTextConverter(
            file_path=file_path,
            model=audio_model,
            api_key=api_key,
            save_transcript=save_transcript,
            output_path=output_path,
            logging_level=logging_level,
        )
        transcript = converter.speech_to_text()
        usage["audio cost"] = converter.get_audio_usage()

    # Use class ReportGenerator to generate summary reports
    generator = ReportGenerator(
        transcript=transcript,
        model=text_model,
        api_key=api_key,
        logging_level=logging.INFO,
    )
    report = generator.generate_report()
    usage["text cost"] = generator.get_spent_tokens()
    logging.info(f"Report content:{report}")

    # Use class ReportExporter to export the results
    exporter = ReportExporter(
        meeting_name=meeting_name, summary=report, usage=usage, output_path=output_path
    )
    exporter.export_txt(show_cost=show_txt_cost)
    exporter.export_json()


# Example
if __name__ == "__main__":
    # Define by user
    meeting_name = "商業數據力課程摘要"
    file_path = (
        "/Users/lucienlin/Projects/intelligent-world-projects/meeting-ai/data/商業數據力.m4a"
    )
    audio_model = "api"
    text_model = "gpt-3.5-turbo"
    api_key = os.getenv("API_KEY")
    output_path = "/Users/lucienlin/Desktop"
    transcript_path = "/Users/lucienlin/Desktop/商業數據力_transcript.txt"
    save_transcript = True
    show_txt_cost = False
    logging_level = logging.INFO

    # Excute meeting ai
    meeting_ai(
        meeting_name=meeting_name,
        file_path=file_path,
        api_key=api_key,
        audio_model=audio_model,
        text_model=text_model,
        transcript_path=transcript_path,
        output_path=output_path,
        save_transcript=save_transcript,
        show_txt_cost=show_txt_cost,
        logging_level=logging_level,
    )
