import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import pytest
from src.auto_summarize import ReportGenerator
import builtins

def test_report_generator_init(mocker):
    mocker.patch("src.auto_summarize2.openai")
    mocker.patch.object(ReportGenerator, "openai", create=True)
    ReportGenerator.openai.api_key = "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"

    report_generator = ReportGenerator()
    
    assert report_generator.model == "gpt-3.5-turbo-16k"
    assert report_generator.prompt_tokens == 0
    assert report_generator.completion_tokens == 0
    assert ReportGenerator.openai.api_key == "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"


def test_call_openai(mocker):
    report_generator = ReportGenerator()

    mocker.patch("openai.ChatCompletion.create", return_value={
        "usage": {"prompt_tokens": 10, "completion_tokens": 20},
        "choices": [
            {
                "message": {
                    "content": "Generated response"
                }
            }
        ]
    })

    response = report_generator._call_openai(
        prompt="User prompt",
        system_prompt="System prompt",
        temperature=0.8,
        max_tokens=100
    )

    assert response == "Generated response"
    assert report_generator.prompt_tokens == 10
    assert report_generator.completion_tokens == 20


def test_chunk_transcript(mocker):
    transcript = "This is a test transcript. It contains some text that needs to be chunked into smaller parts."
    chunk_size = 4000

    expected_chunks = [
        "This is a test transcript. It contains some text that needs to be chunked into smaller parts."
    ]
    mocker.patch("builtins.print")
    chunks = ReportGenerator._chunk_transcript(transcript, chunk_size)
    assert chunks == expected_chunks

    assert builtins.print.call_count == 2
    builtins.print.assert_any_call("Split to", len(expected_chunks), " chunks.")
    builtins.print.assert_any_call("Successfully chunked transcripts.")
