"""
Export Meeting Reports

This script provides a `ReportExporter` class that handles exporting meeting reports to various file formats.

Usage:
    1. Import the `ReportExporter` class from this module.
    2. Create an instance of `ReportExporter` by specifying the output directory.
    3. Call the appropriate export methods to export meeting reports to different formats.

Example:
    from report_exporter import ReportExporter

    # Create an instance of ReportExporter with the output directory
    exporter = ReportExporter(output_directory='/path/to/output')

    # Export meeting summary and follow-up actions to a text file
    exporter.export_txt(meeting_name='Meeting 1', summary='Meeting summary...', follow_ups='Follow-up actions...')

    # Export meeting summary and follow-up actions to a DOC file
    exporter.export_doc(meeting_name='Meeting 1', summary='Meeting summary...', follow_ups='Follow-up actions...')

    # Export meeting summary and follow-up actions to a PDF file
    exporter.export_pdf(meeting_name='Meeting 1', summary='Meeting summary...', follow_ups='Follow-up actions...')

    # Export meeting summary and follow-up actions to a JSON file
    exporter.export_json(meeting_name='Meeting 1', summary='Meeting summary...', follow_ups='Follow-up actions...')

    # Export follow-up actions to an XLSX file
    exporter.export_xlsx(meeting_name='Meeting 1', follow_ups='Follow-up actions...')

    # Export follow-up actions to a CSV file
    exporter.export_csv(meeting_name='Meeting 1', follow_ups='Follow-up actions...')
"""
import os
import json
import csv
import openpyxl
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

    def export_txt(self, meeting_name, summary, follow_ups):
        """
        Exports the meeting summary and follow-up actions to a text file.

        Args:
            meeting_name (str): The name of the meeting.
            summary (str): The summary of the meeting.
            follow_ups (str): The follow-up actions from the meeting.
        """
        filename = f"{meeting_name}.txt"
        filepath = os.path.join(self.output_directory, filename)
        with open(filepath, "w", encoding="utf-8") as file:
            file.write(f"#{meeting_name}\n\n")
            file.write("##會議重點\n")
            file.write(summary)
            file.write("\n\n##後續行動\n")
            file.write(follow_ups)

    def export_doc(self, meeting_name, summary, follow_ups):
        """
        Exports the meeting summary and follow-up actions to a DOC file.

        Args:
            meeting_name (str): The name of the meeting.
            summary (str): The summary of the meeting.
            follow_ups (str): The follow-up actions from the meeting.
        """
        filename = f"{meeting_name}.doc"
        filepath = os.path.join(self.output_directory, filename)
        with open(filepath, "w", encoding="utf-8") as file:
            file.write(f"#{meeting_name}\n\n")
            file.write("##會議重點\n")
            file.write(summary)
            file.write("\n\n##後續行動\n")
            file.write(follow_ups)

    def export_pdf(self, meeting_name, summary, follow_ups):
        """
        Exports the meeting summary and follow-up actions to a PDF file.

        Args:
            meeting_name (str): The name of the meeting.
            summary (str): The summary of the meeting.
            follow_ups (str): The follow-up actions from the meeting.
        """
        filename = f"{meeting_name}.pdf"
        filepath = os.path.join(self.output_directory, filename)

        summary_items = summary.split("\n")
        follow_ups_items = follow_ups.split("\n")

        summary_html = (
            "\n".join(
                [f"<p>{item.strip()}</p>" for item in summary_items if item.strip()]
            )
            + "\n"
        )
        follow_ups_html = "\n".join(
            [f"<p>{item.strip()}</p>" for item in follow_ups_items if item.strip()]
        )

        html_content = f"""
        <html>
            <head>
                <title>{meeting_name}</title>
            </head>
            <body>
                <h1>{meeting_name}</h1>
                <h2>會議重點</h2>
                {summary_html}
                <h2>後續行動</h2>
                {follow_ups_html}
            </body>
        </html>
        """

        HTML(string=html_content).write_pdf(filepath)

    def export_json(self, meeting_name, summary, follow_ups):
        """
        Exports the meeting summary and follow-up actions to a JSON file.

        Args:
            meeting_name (str): The name of the meeting.
            summary (str): The summary of the meeting.
            follow_ups (str): The follow-up actions from the meeting.
        """
        filename = f"{meeting_name}.json"
        filepath = os.path.join(self.output_directory, filename)

        data = {
            "meeting_name": meeting_name,
            "summary": summary,
            "follow_ups": follow_ups,
        }

        with open(filepath, "w") as json_file:
            json.dump(data, json_file)

    def export_xlsx(self, meeting_name, follow_ups):
        """
        Exports the follow-up actions to an XLSX file.

        Args:
            meeting_name (str): The name of the meeting.
            follow_ups (str): The follow-up actions from the meeting.
        """
        filename = f"{meeting_name}.xlsx"
        filepath = os.path.join(self.output_directory, filename)

        workbook = openpyxl.Workbook()
        sheet = workbook.active

        follow_ups_table_name = f"{meeting_name}_待辦事項"

        sheet.title = follow_ups_table_name
        sheet["A1"] = "事項"
        sheet["B1"] = "負責人"
        sheet["C1"] = "簽名"

        follow_ups_items = follow_ups.split("\n")
        follow_ups_items = [
            item.strip("- ") for item in follow_ups_items if item.strip("- ")
        ]

        for row, item in enumerate(follow_ups_items, start=2):
            sheet[f"A{row}"] = item

        workbook.save(filepath)

    def export_csv(self, meeting_name, follow_ups):
        """
        Exports the follow-up actions to a CSV file.

        Args:
            meeting_name (str): The name of the meeting.
            follow_ups (str): The follow-up actions from the meeting.
        """
        filename = f"{meeting_name}.csv"
        filepath = os.path.join(self.output_directory, filename)

        with open(filepath, "w", newline="") as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(["事項", "負責人", "簽名"])

            follow_ups_items = follow_ups.split("\n")
            follow_ups_items = [
                item.strip("- ") for item in follow_ups_items if item.strip("- ")
            ]

            for item in follow_ups_items:
                writer.writerow([item, "", ""])
