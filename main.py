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
import os
import json
from src.speech_to_text import SpeechToTextConverter
from src.auto_summarize import ReportGenerator


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
    with open(config_path, encoding="utf-8") as config_file:
        config = json.load(config_file)

    file_url = config["file_url"]
    meeting_name = config["meeting_name"]
    use_api = config["use_api"]

    if not os.path.exists(file_url):
        print("File not found:", file_url)
        return

    (
        audio_minutes,
        transcript_cost,
        prompt_tokens,
        completion_tokens,
        total_tokens,
        report_cost,
    ) = (0.0, 0.0, 0, 0, 0, 0.0)

    transcript_file = os.path.join(
        os.path.dirname(file_url),
        os.path.basename(file_url).replace(
            os.path.splitext(file_url)[1], "_transcript.txt"
        ),
    )
    if os.path.exists(transcript_file):
        with open(transcript_file, "r", encoding="utf-8") as transcript_file:
            transcript = transcript_file.read()
    else:
        converter = SpeechToTextConverter()
        transcript = converter.speech_to_text(file_url,use_api)
        audio_minutes, transcript_cost = converter.get_transcript_usage()

    report_file = os.path.join(
        os.path.dirname(file_url),
        os.path.basename(file_url).replace(
            os.path.splitext(file_url)[1], "_report.txt"
        ),
    )
    if os.path.exists(report_file):
        with open(report_file, "r", encoding="utf-8") as report_file:
            report = report_file.read()
    else:
        report_generator = ReportGenerator()
        report = report_generator.generate_report(transcript, file_url, meeting_name)
        (
            prompt_tokens,
            completion_tokens,
            total_tokens,
            report_cost,
        ) = report_generator.get_report_usage()

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

    print(report)
    print("使用量和費用\n\n", usage_info)


if __name__ == "__main__":
    main()
