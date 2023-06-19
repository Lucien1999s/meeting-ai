import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pytest
from src.auto_summarize2 import ReportGenerator
from unittest import mock
from unittest.mock import patch

def test_report_generator_init():
    with mock.patch("src.auto_summarize2.openai") as mock_openai:
        mock_openai.api_key = "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"
        report_generator = ReportGenerator()
        
        assert report_generator.model == "gpt-3.5-turbo-16k"
        assert report_generator.prompt_tokens == 0
        assert report_generator.completion_tokens == 0
        assert mock_openai.api_key == "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"

def test_call_openai():

    report_generator = ReportGenerator()

    with mock.patch("openai.ChatCompletion.create") as mock_create:
        mock_create.return_value = {
            "usage": {"prompt_tokens": 10, "completion_tokens": 20},
            "choices": [
                {
                    "message": {
                        "content": "Generated response"
                    }
                }
            ]
        }

        response = report_generator._call_openai(
            prompt="User prompt",
            system_prompt="System prompt",
            temperature=0.8,
            max_tokens=100
        )

        assert response == "Generated response"
        assert report_generator.prompt_tokens == 10
        assert report_generator.completion_tokens == 20

def test_chunk_transcript():
    transcript = "This is a test transcript. It contains some text that needs to be chunked into smaller parts."
    chunk_size = 4000

    expected_chunks = [
        "This is a test transcript. It contains some text that needs to be chunked into smaller parts."
    ]
    with mock.patch("builtins.print") as mock_print:
        chunks = ReportGenerator._chunk_transcript(transcript, chunk_size)
        assert chunks == expected_chunks

        # 驗證print函數是否正確調用
        assert mock_print.call_count == 2
        mock_print.assert_any_call("Split to", len(expected_chunks), " chunks.")
        mock_print.assert_any_call("Successfully chunked transcripts.")


@pytest.fixture
def mock_translate():
    with patch('pygtrans.Translate') as mock_translate:
        yield mock_translate.return_value

def test_sumy(mock_translate):
    # 创建一个 ReportGenerator 对象
    report_generator = ReportGenerator()

    # 设置 Translate 类的 mock 实例
    translate_instance = mock_translate
    translate_instance.translate.return_value.translatedText = "This is the translated text."

    # 设置输入参数和预期结果
    chinese_texts = ["这是中文文本1", "这是中文文本2"]
    expected_summaries = ["这是翻译后的摘要1", "这是翻译后的摘要2"]

    # 调用被测试的方法
    actual_summaries = report_generator._sumy(chinese_texts)

    # 断言结果是否与预期一致
    assert actual_summaries == expected_summaries

    # 断言 Translate 类的相关方法是否被正确调用
    translate_instance.translate.assert_called_with("这是中文文本1", target="en")
    translate_instance.translate.assert_called_with("这是中文文本2", target="en")
    translate_instance.translate.assert_called_with("This is the translated text.", target="zh-TW")