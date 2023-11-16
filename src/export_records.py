"""
Export Meeting Reports

This module provides a class for exporting meeting reports to various file formats, 
such as text and JSON. The ReportExporter class takes in the meeting name, summary, 
and usage details (if available), and exports them to a text or JSON file in the 
specified output directory. If no output directory is provided, 
it defaults to the parent directory of this file. 
The class also sets up logging with a default level of INFO.

Example:
    exporter = ReportExporter(
        meeting_name = "Meeting 1",
        summary = "Summary of the meeting...", 
        output_path = "YOUR_PATH",
        usage = {Usage details...},
        logging_level = logging.INFO
    )
    exporter.export_txt(show_cost = True)
    exporter.export_json()
"""

import os
import json
import logging
from typing import Optional


class ReportExporter:
    """
    A class for exporting meeting summaries and usage information to text and JSON files.
    """

    def __init__(
        self,
        meeting_name: str,
        summary: str,
        output_path: str,
        usage: Optional[str] = None,
        logging_level: int = logging.INFO,
    ):
        """
        Initializes the class with the given parameters.

        Args:
            meeting_name (str): The name of the meeting.
            summary (str): A summary of the meeting.
            output_path (str): The path where the output file will be saved.
            usage (str, optional): The usage of this class. Defaults to None.
            logging_level (int, optional): The level of logging. Defaults to logging.INFO.

        Raises:
            ValueError: If the meeting name or summary is not a string.
            ValueError: If the output path is not None and not a string.
        """
        if not isinstance(meeting_name, str) or not isinstance(summary, str):
            raise ValueError("Meeting name and summary must be strings.")
        if output_path is not None and not isinstance(output_path, str):
            raise ValueError("Output path must be a string.")

        if not meeting_name:
            meeting_name = "會議記錄"

        if output_path is None:
            output_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.output_path = output_path
        self.meeting_name = meeting_name
        self.summary = summary
        self.usage = usage
        logging.basicConfig(level=logging_level)

    def export_txt(self, show_cost: bool = False):
        """
        Exports the meeting summary to a text file.

        Args:
            show_cost (bool, optional): If True, the cost information will be included in the text file. Defaults to False.

        Raises:
            Exception: If there is an error in exporting the text file.
        """
        try:
            filename = f"{self.meeting_name}.txt"
            filepath = os.path.join(self.output_path, filename)
            with open(filepath, "w", encoding="utf-8") as file:
                file.write(f"#{self.meeting_name}\n\n")
                file.write("##會議重點\n")
                file.write(self.summary)
                if show_cost:
                    file.write("\n\n##費用資訊\n")
                    file.write(str(self.usage))
            logging.info(f"Successfully exported text file: {filepath}")
        except Exception as e:
            logging.warning(f"Failed to export text file: {e}")

    def export_json(self):
        """
        Exports the meeting summary to a JSON file.

        Raises:
            Exception: If there is an error in exporting the JSON file.
        """
        try:
            filename = f"{self.meeting_name}.json"
            filepath = os.path.join(self.output_path, filename)
            data = {
                "meeting_name": self.meeting_name,
                "summary": self.summary,
            }
            if self.usage:
                data["usage"] = self.usage
            with open(filepath, "w", encoding="utf-8") as json_file:
                json.dump(data, json_file)
            logging.info(f"Successfully exported JSON file: {filepath}")
        except Exception as e:
            logging.warning(f"Failed to export JSON file: {e}")
