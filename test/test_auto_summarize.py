import os
import sys
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from src.auto_summarize import ReportGenerator


def test_get_report_usage_with_values():
    report_generator = ReportGenerator()
    report_generator.prompt_tokens = 6000
    report_generator.completion_tokens = 1800
    report_generator.total_cost = 1.22398
    (
        prompt_tokens,
        completion_tokens,
        total_tokens,
        total_cost,
    ) = report_generator.get_report_usage()
    assert prompt_tokens == 6000
    assert completion_tokens == 1800
    assert total_tokens == 7800
    assert total_cost == 1.22398


def test_get_report_usage_with_default_values():
    report_generator = ReportGenerator()
    (
        prompt_tokens,
        completion_tokens,
        total_tokens,
        total_cost,
    ) = report_generator.get_report_usage()
    assert prompt_tokens == 0
    assert completion_tokens == 0
    assert total_tokens == 0
    assert total_cost == 0


def test_generate_report(mocker):
    return
