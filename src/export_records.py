"""
Export Meeting Reports

This script provides a class for exporting meeting reports to various file formats, such as text and JSON.

Usage:
    1. Initialize the `ReportExporter` class with the following arguments:
       - output_directory (str): The directory where the output files will be saved.
       - meeting_name (str): The name of the meeting.
       - summary (str): The summary of the meeting.
       - usage (str): The usage details of the meeting report.

    2. Call the `export_file` method to export the meeting report in both text and JSON formats.

Example:
    # Initialize the ReportExporter class
    exporter = ReportExporter(output_directory="/path/to/output", meeting_name="Meeting 1",
                              summary="Summary of the meeting...", usage="Usage details...")

    # Export the meeting report
    exporter.export_file()
"""

import os
import json
import logging

logging.getLogger("fontTools").setLevel(logging.WARNING)
logging.basicConfig(level=logging.INFO)


class ReportExporter:
    """
    A class that handles exporting meeting reports to various file formats.

    Args:
        output_directory (str): The directory where the output files will be saved.
        meeting_name (str): The name of the meeting.
        summary (str): The summary of the meeting.
        usage (str): The usage details of the meeting report.
    """

    def __init__(self, output_directory, meeting_name, summary, usage):
        """
        Initialize the ReportExporter class.

        Args:
            output_directory (str): The directory where the output files will be saved.
            meeting_name (str): The name of the meeting.
            summary (str): The summary of the meeting.
            usage (str): The usage details of the meeting report.
        """
        self.output_directory = output_directory
        self.meeting_name = meeting_name
        self.summary = summary
        self.usage = usage

    def _export_text(self):
        """
        Export the meeting report to a text file.
        """
        filename = f"{self.meeting_name}.txt"
        filepath = os.path.join(self.output_directory, filename)
        with open(filepath, "w", encoding="utf-8") as file:
            file.write(f"#{self.meeting_name}\n\n")
            file.write("##會議重點\n")
            file.write(self.summary)

    def _export_json(self):
        """
        Export the meeting report to a JSON file.
        """
        filename = f"{self.meeting_name}.json"
        filepath = os.path.join(self.output_directory, filename)
        data = {
            "meeting_name": self.meeting_name,
            "summary": self.summary,
            "usage": self.usage,
        }
        with open(filepath, "w", encoding="utf-8") as json_file:
            json.dump(data, json_file)

    def export_file(self):
        """
        Export the meeting report to both text and JSON formats.
        """
        self._export_text()
        self._export_json()
