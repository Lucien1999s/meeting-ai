import os
import sys
import pytest
import json

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from src.export_records import ReportExporter


def test_export_txt(tmpdir):
    output_directory = str(tmpdir)
    exporter = ReportExporter(output_directory)

    meeting_name = "Meeting 1"
    summary = "Meeting summary"

    exporter.export_txt(meeting_name, summary)

    expected_file_path = os.path.join(output_directory, f"{meeting_name}.txt")
    assert os.path.exists(expected_file_path)

    with open(expected_file_path, "r", encoding="utf-8") as file:
        content = file.read()
        assert f"#{meeting_name}\n\n" in content
        assert "##會議重點\n" in content
        assert summary in content


def test_export_doc(tmpdir):
    output_directory = str(tmpdir)
    exporter = ReportExporter(output_directory)

    meeting_name = "Meeting 1"
    summary = "Meeting summary"

    exporter.export_doc(meeting_name, summary)

    expected_file_path = os.path.join(output_directory, f"{meeting_name}.doc")
    assert os.path.exists(expected_file_path)

    with open(expected_file_path, "r", encoding="utf-8") as file:
        content = file.read()
        assert f"#{meeting_name}\n\n" in content
        assert "##會議重點\n" in content
        assert summary in content


def test_export_pdf(tmpdir):
    output_directory = str(tmpdir)
    exporter = ReportExporter(output_directory)

    meeting_name = "Meeting 1"
    summary = "Meeting summary"

    exporter.export_pdf(meeting_name, summary)

    expected_file_path = os.path.join(output_directory, f"{meeting_name}.pdf")
    assert os.path.exists(expected_file_path)


def test_export_json(tmpdir):
    output_directory = str(tmpdir)
    exporter = ReportExporter(output_directory)

    meeting_name = "Meeting 1"
    summary = "Meeting summary"

    exporter.export_json(meeting_name, summary)

    expected_file_path = os.path.join(output_directory, f"{meeting_name}.json")
    assert os.path.exists(expected_file_path)

    with open(expected_file_path, "r", encoding="utf-8") as file:
        data = json.load(file)
        assert data["meeting_name"] == meeting_name
        assert data["summary"] == summary
