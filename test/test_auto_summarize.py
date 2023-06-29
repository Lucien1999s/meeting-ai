import os
import sys
import pytest
from openai import OpenAIError

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from src.auto_summarize import ReportGenerator


def test_get_report_usage_with_values():
    generator = ReportGenerator()
    generator.prompt_tokens = 6000
    generator.completion_tokens = 1800
    generator.total_cost = 1.22398
    (
        prompt_tokens,
        completion_tokens,
        total_tokens,
        total_cost,
    ) = generator.get_report_usage()
    assert prompt_tokens == 6000
    assert completion_tokens == 1800
    assert total_tokens == 7800
    assert total_cost == 1.22398


def test_get_report_usage_with_default_values():
    generator = ReportGenerator()
    (
        prompt_tokens,
        completion_tokens,
        total_tokens,
        total_cost,
    ) = generator.get_report_usage()
    assert prompt_tokens == 0
    assert completion_tokens == 0
    assert total_tokens == 0
    assert total_cost == 0


def test_generate_report(mocker):
    generator = ReportGenerator()
    expect_value = "我需要做一個測試程式"
    meeting_transcript = "我正在做一個測試程式該程式非常需要好好靜下心來學習並實作"
    generator._chunk_transcript = lambda transcript: expect_value
    generator._sumy_transcript = lambda chinese_text: expect_value
    generator._process_string = lambda result: expect_value

    mock_result = mocker.patch("src.auto_summarize.openai.ChatCompletion.create")
    mock_result.return_value = {
        "choices": [{"message": {"content": expect_value}}],
        "usage": {"prompt_tokens": 20, "completion_tokens": 30},
    }
    summary, follow_ups = generator.generate_report(meeting_transcript)

    assert summary == expect_value
    assert follow_ups == expect_value


def test_generate_report_with_error(mocker):
    generator = ReportGenerator()
    meeting_transcript = "我正在做一個測試程式該程式非常需要好好靜下心來學習並實作"

    mocker.patch(
        "src.auto_summarize.openai.ChatCompletion.create",
        side_effect=OpenAIError("API error"),
    )

    with pytest.raises(OpenAIError):
        generator.generate_report(meeting_transcript)
