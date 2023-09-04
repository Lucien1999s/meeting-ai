"""
Main code: Extracts text from an audio file and generates a meeting report.

This function performs the following steps:
1. Retrieves the audio file from the specified URL.
2. Converts the speech to text using the SpeechToTextConverter class.
3. Generates a meeting report using the MeetingReportGenerator class.
4. Export the meeting report.

Args:
    None

Returns:
    None

Modules:
    - src.speech_to_text: Contains the SpeechToTextConverter class for converting speech to text.
    - src.auto_summarize: Contains the ReportGenerator class for generating meeting reports.
    - src.export_records: Contains the ReportExporter class for exporting reports.

Usage Example:
    # Convert speech to text
    converter = SpeechToTextConverter(file_url, model_selection, api_key)
    transcript = converter.speech_to_text()
    audio_minutes, transcript_cost = converter.get_transcript_usage()

    # Generate meeting report
    report_generator = ReportGenerator(transcript, api_key)
    summary = report_generator.generate_report()

    # Calculate report usage
    prompt_tokens, completion_tokens, total_tokens, report_cost = report_generator.get_report_usage()

    # Export the report
    exporter = ReportExporter(output_url, meeting_name, summary, usage)
    exporter.export_file()
"""
import os
import json
import logging
import openai
from src.speech_to_text import SpeechToTextConverter
from src.auto_summarize import ReportGenerator
from src.export_records import ReportExporter
from dotenv import load_dotenv

load_dotenv()
logging.basicConfig(level=logging.INFO)


def main():
    """
    Main function for generating and exporting meeting reports based on provided configuration.

    This function reads configuration parameters from a JSON file, processes meeting information,
    converts audio to transcript using a speech-to-text converter, generates a meeting report,
    calculates usage metrics, and exports the results in JSON and text formats.

    Raises:
        FileNotFoundError: If the input file specified in the configuration is not found.
    """
    try:
        # Read parameters from json file
        config_path = "config.json"
        with open(config_path, encoding="utf-8") as config_file:
            config = json.load(config_file)

        file_url = config["file_url"]
        output_url = config["output_url"]
        meeting_name = config["meeting_name"]
        model_selection = config["model_selection"]

        if not os.path.exists(file_url):
            raise FileNotFoundError("File not found: " + file_url)

        if not os.path.exists(output_url):
            output_url = os.path.dirname(os.path.abspath(__file__))

    except Exception as e:
        logging.info("An error occurred:", e)
        return

    # Initialize parameters of usage
    costs = {
        "audio_minutes": 0.0,
        "transcript_cost": 0.0,
        "prompt_tokens": 0,
        "completion_tokens": 0,
        "total_tokens": 0,
        "report_cost": 0.0,
    }
    # Audio length threshold
    audio_max_length = 240

    # Get OpenAI API Key
    openai.api_key = os.environ.get("OPENAI_API_KEY")
    api_key = openai.api_key

    # Speech to text
    model = "whisper-1" if model_selection == "api" else "small"
    converter = SpeechToTextConverter(file_url, model, api_key)

    # Make sure if exceed audio max length
    costs["audio_minutes"] = converter.get_audio_minutes()
    if costs["audio_minutes"] > audio_max_length:
        logging.warn("Audio files cannot exceed 4 hours.")
        return

    # Make sure if transcript exist or use speech to text
    transcript_file = os.path.join(
        os.path.dirname(file_url),
        os.path.basename(file_url).replace(
            os.path.splitext(file_url)[1], "_transcript.txt"
        ),
    )
    if os.path.exists(transcript_file):
        # Use existing transcript file
        with open(transcript_file, "r", encoding="utf-8") as transcript_file:
            transcript = transcript_file.read()
    else:
        # Use speech-to-text class
        transcript = converter.speech_to_text()
        costs["transcript_cost"] = converter.get_transcript_cost()

    # Generate report by using ReportGenerator
    report_generator = ReportGenerator(transcript, "gpt-3.5-turbo-16k",api_key)
    summary = report_generator.generate_report()

    # Get usage information
    (
        costs["prompt_tokens"],
        costs["completion_tokens"],
        costs["total_tokens"],
        costs["report_cost"],
    ) = report_generator.get_report_usage()

    logging.info(costs)

    # Export the result by using ReportExporter (json, txt)
    exporter = ReportExporter(output_url, meeting_name, summary, costs)
    exporter.export_file()


if __name__ == "__main__":
    main()
