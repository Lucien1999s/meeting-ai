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
from src.auto_summarize import ReportGenerator
from src.record_usage import UsageRecorder
import json
import os


def main():
    """
    Main function: Extracts text from an audio file and generates a meeting report.

    This function performs the following steps:
    1. Retrieves the audio file from the specified URL.
    2. Converts the speech to text using the SpeechToTextConverter class.
    3. Generates a meeting report using the ReportGenerator class.
    4. Prints the meeting report.

    Args:
        None

    Returns:
        None
    """
    config_path = "config.json"
    with open(config_path) as config_file:
        config = json.load(config_file)

    file_url = config["file_url"]
    meeting_name = config["meeting_name"]

    if not os.path.exists(file_url):
        print("File not found:", file_url)
        return

    transcript_file = os.path.join(
        os.path.dirname(file_url),
        os.path.basename(file_url).replace(
            os.path.splitext(file_url)[1], "_transcript.txt"
        ),
    )
    if os.path.exists(transcript_file):
        with open(transcript_file, "r") as transcript_file:
            transcript = transcript_file.read()
    else:
        converter = SpeechToTextConverter()
        transcript = converter.speech_to_text_go(file_url)

    report_file = os.path.join(
        os.path.dirname(file_url),
        os.path.basename(file_url).replace(
            os.path.splitext(file_url)[1], "_report.txt"
        ),
    )
    if os.path.exists(report_file):
        with open(report_file, "r") as report_file:
            report = report_file.read()
    else:
        report_generator = ReportGenerator()
        report = report_generator.generate_report(transcript, file_url, meeting_name)

    usage_recoder = UsageRecorder()
    audio_minutes, transcript_cost = usage_recoder.get_transcript_usage()
    (
        prompt_tokens,
        completion_tokens,
        total_tokens,
        report_cost,
    ) = usage_recoder.get_report_usage()

    usage_info = (
        "\n轉音檔分鐘數： "
        + str(audio_minutes)
        + "\n逐字稿總花費： "
        + str(transcript_cost)
        + " USD\n\n"
        + "Prompt總用量： "
        + str(prompt_tokens)
        + " tokens\nCompletion總用量： "
        + str(completion_tokens)
        + " tokens\n"
        + "總用量： "
        + str(total_tokens)
        + " tokens\nAI報告總花費："
        + str(report_cost)
        + " USD"
    )

    print("逐字稿\n\n", transcript)
    print("AI報告\n\n", report)
    print("使用量和費用\n\n", usage_info)


if __name__ == "__main__":
    main()
