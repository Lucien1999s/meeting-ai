from src.meeting_assistant.speech_to_text import SpeechToTextConverter
from src.meeting_assistant.auto_summarize import TextConverterToReport


def main():
    file_url = "https://drive.google.com/file/d/1-g_Zj2IFbV_4BOCU78dCbU5nx8wd5SfE/view?usp=sharing"

    stt_converter = SpeechToTextConverter()
    text_result_path = stt_converter.speech_to_text_go(file_url)

    report_generator = TextConverterToReport()
    meeting_report = report_generator.generate_report("會議名稱", text_result_path)

    print(meeting_report)


if __name__ == "__main__":
    main()
