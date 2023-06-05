"""
Main code: Extracts text from an audio file and generates a meeting report.

This function performs the following steps:
1. Retrieves the audio file from the specified URL.
2. Converts the speech to text using the SpeechToTextConverter class.
3. Generates a meeting report using the MeetingReportGenerator class.
4. Prints the meeting report.

Args:
    None

Returns:
    None
"""
from src.speech_to_text import SpeechToTextConverter
from src.auto_summarize import MeetingReportGenerator
import json
import os


def main():
    """
    Main function: Extracts text from an audio file and generates a meeting report.

    This function performs the following steps:
    1. Retrieves the audio file from the specified URL.
    2. Converts the speech to text using the SpeechToTextConverter class.
    3. Generates a meeting report using the MeetingReportGenerator class.
    4. Prints the meeting report.

    Args:
        None

    Returns:
        None
    """
    # Load config from JSON file
    config_path = "config.json"
    with open(config_path) as config_file:
        config = json.load(config_file)

    file_url = config["file_url"]
    meeting_name = config["meeting_name"]

    if not os.path.exists(file_url):
        print("File not found:", file_url)
        return

    converter = SpeechToTextConverter()
    transcript = converter.speech_to_text_go(file_url)

    report_generator = MeetingReportGenerator()
    meeting_report = report_generator.generate_report(meeting_name, transcript)

    print(meeting_report)


if __name__ == "__main__":
    main()
