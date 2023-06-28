import os
import sys
import pytest
import json
import csv
import openpyxl

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from src.export_records import ReportExporter


def test_export_txt(tmpdir):
    output_directory = str(tmpdir)
    exporter = ReportExporter(output_directory)

    meeting_name = "Meeting 1"
    summary = "Meeting summary"
    follow_ups = "Follow-up actions"

    exporter.export_txt(meeting_name, summary, follow_ups)

    expected_file_path = os.path.join(output_directory, f"{meeting_name}.txt")
    assert os.path.exists(expected_file_path)

    with open(expected_file_path, "r", encoding="utf-8") as file:
        content = file.read()
        assert f"#{meeting_name}\n\n" in content
        assert "##會議重點\n" in content
        assert summary in content
        assert "\n\n##後續行動\n" in content
        assert follow_ups in content


def test_export_doc(tmpdir):
    output_directory = str(tmpdir)
    exporter = ReportExporter(output_directory)

    meeting_name = "Meeting 1"
    summary = "Meeting summary"
    follow_ups = "Follow-up actions"

    exporter.export_doc(meeting_name, summary, follow_ups)

    expected_file_path = os.path.join(output_directory, f"{meeting_name}.doc")
    assert os.path.exists(expected_file_path)

    with open(expected_file_path, "r", encoding="utf-8") as file:
        content = file.read()
        assert f"#{meeting_name}\n\n" in content
        assert "##會議重點\n" in content
        assert summary in content
        assert "\n\n##後續行動\n" in content
        assert follow_ups in content


def test_export_pdf(tmpdir):
    output_directory = str(tmpdir)
    exporter = ReportExporter(output_directory)

    meeting_name = "Meeting 1"
    summary = "Meeting summary"
    follow_ups = "Follow-up actions"

    exporter.export_pdf(meeting_name, summary, follow_ups)

    expected_file_path = os.path.join(output_directory, f"{meeting_name}.pdf")
    assert os.path.exists(expected_file_path)


def test_export_json(tmpdir):
    output_directory = str(tmpdir)
    exporter = ReportExporter(output_directory)

    meeting_name = "Meeting 1"
    summary = "Meeting summary"
    follow_ups = "Follow-up actions"

    exporter.export_json(meeting_name, summary, follow_ups)

    expected_file_path = os.path.join(output_directory, f"{meeting_name}.json")
    assert os.path.exists(expected_file_path)

    with open(expected_file_path, "r") as file:
        data = json.load(file)
        assert data["meeting_name"] == meeting_name
        assert data["summary"] == summary
        assert data["follow_ups"] == follow_ups


def test_export_xlsx(tmpdir):
    output_directory = str(tmpdir)
    exporter = ReportExporter(output_directory)

    meeting_name = "Meeting 1"
    follow_ups = "Follow-up actions"

    exporter.export_xlsx(meeting_name, follow_ups)

    expected_file_path = os.path.join(output_directory, f"{meeting_name}.xlsx")
    assert os.path.exists(expected_file_path)

    workbook = openpyxl.load_workbook(expected_file_path)
    sheet = workbook.active

    assert sheet.title == f"{meeting_name}_待辦事項"
    assert sheet["A1"].value == "事項"
    assert sheet["B1"].value == "負責人"
    assert sheet["C1"].value == "簽名"

    follow_ups_items = follow_ups.split("\n")
    follow_ups_items = [
        item.strip("- ") for item in follow_ups_items if item.strip("- ")
    ]

    for row, item in enumerate(follow_ups_items, start=2):
        assert sheet[f"A{row}"].value == item


def test_export_csv(tmpdir):
    output_directory = str(tmpdir)
    exporter = ReportExporter(output_directory)

    meeting_name = "Meeting 1"
    follow_ups = "Follow-up actions"

    exporter.export_csv(meeting_name, follow_ups)

    expected_file_path = os.path.join(output_directory, f"{meeting_name}.csv")
    assert os.path.exists(expected_file_path)

    with open(expected_file_path, "r", newline="") as csvfile:
        reader = csv.reader(csvfile)
        header = next(reader)
        assert header == ["事項", "負責人", "簽名"]

        follow_ups_items = follow_ups.split("\n")
        follow_ups_items = [
            item.strip("- ") for item in follow_ups_items if item.strip("- ")
        ]

        for row, item in enumerate(follow_ups_items, start=2):
            assert [item, "", ""] == next(reader)
