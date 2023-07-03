"""
Export Meeting Reports

This script provides a `ReportExporter` class that
handles exporting meeting reports to various file formats.

Usage:
    1. Import the `ReportExporter` class from this module.
    2. Create an instance of `ReportExporter` by specifying
       the output directory.
    3. Call the appropriate export methods to export meeting
       reports to different formats.

Example:
    from report_exporter import ReportExporter

    # Create an instance of ReportExporter with the output directory
    exporter = ReportExporter(output_directory='/path/to/output')

    # Export meeting summary to a text file
    exporter.export_txt(meeting_name='Meeting 1', summary='Meeting ...')

    # Export meeting summary to a DOC file
    exporter.export_doc(meeting_name='Meeting 1', summary='Meeting ...')

    # Export meeting summary to a PDF file
    exporter.export_pdf(meeting_name='Meeting 1', summary='Meeting ...')

    # Export meeting summary to a JSON file
    exporter.export_json(meeting_name='Meeting 1', summary='Meeting ...')
"""
import os
import json
import logging
from weasyprint import HTML

logging.getLogger("fontTools").setLevel(logging.WARNING)
logging.basicConfig(level=logging.INFO)


class ReportExporter:
    """
    A class that handles exporting meeting reports to various file formats.

    Args:
        output_directory (str): The directory where the output files will be saved.
    """

    def __init__(self, output_directory):
        """
        Initializes a ReportExporter object.

        Args:
            output_directory (str): The directory where the output files will be saved.
        """
        self.output_directory = output_directory

    def export_txt(self, meeting_name, summary):
        """
        Exports the meeting summary to a text file.

        Args:
            meeting_name (str): The name of the meeting.
            summary (str): The summary of the meeting.
        """
        filename = f"{meeting_name}.txt"
        filepath = os.path.join(self.output_directory, filename)
        with open(filepath, "w", encoding="utf-8") as file:
            file.write(f"#{meeting_name}\n\n")
            file.write("##會議重點\n")
            file.write(summary)

    def export_doc(self, meeting_name, summary):
        """
        Exports the meeting summary to a DOC file.

        Args:
            meeting_name (str): The name of the meeting.
            summary (str): The summary of the meeting.
        """
        filename = f"{meeting_name}.doc"
        filepath = os.path.join(self.output_directory, filename)
        with open(filepath, "w", encoding="utf-8") as file:
            file.write(f"#{meeting_name}\n\n")
            file.write("##會議重點\n")
            file.write(summary)

    def export_pdf(self, meeting_name, summary):
        """
        Exports the meeting summary to a PDF file.

        Args:
            meeting_name (str): The name of the meeting.
            summary (str): The summary of the meeting.
        """
        filename = f"{meeting_name}.pdf"
        filepath = os.path.join(self.output_directory, filename)

        summary_lines = summary.split("\n")

        summary_html = ""
        for line in summary_lines:
            if line.strip() and line.strip()[0].isdigit():
                summary_html += f"<p><strong>{line.strip()}</strong></p>"
            else:
                summary_html += f"<p>{line.strip()}</p>"

        summary_html += "\n"
        html_content = f"""
        <html>
            <head>
                <title>{meeting_name}</title>
            </head>
            <body>
                <h1>{meeting_name}</h1>
                <h2>會議重點</h2>
                {summary_html}
            </body>
        </html>
        """

        HTML(string=html_content).write_pdf(filepath)

    def export_json(self, meeting_name, summary):
        """
        Exports the meeting summary to a JSON file.

        Args:
            meeting_name (str): The name of the meeting.
            summary (str): The summary of the meeting.
        """
        filename = f"{meeting_name}.json"
        filepath = os.path.join(self.output_directory, filename)

        data = {
            "meeting_name": meeting_name,
            "summary": summary,
        }

        with open(filepath, "w", encoding="utf-8") as json_file:
            json.dump(data, json_file)
