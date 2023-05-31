from src.meeting_assistant.speech_to_text import SpeechToTextConverter
from src.meeting_assistant.auto_summarize import MeetingReportGenerator


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
    file_url = "https://drive.google.com/file/d/1-g_Zj2IFbV_4BOCU78dCbU5nx8wd5SfE/view?usp=sharing"

    stt_converter = SpeechToTextConverter()
    text_result_path = stt_converter.speech_to_text_go(file_url)

    report_generator = MeetingReportGenerator()
    meeting_report = report_generator.generate_report("會議名稱", text_result_path)

    print(meeting_report)


if __name__ == "__main__":
    main()
