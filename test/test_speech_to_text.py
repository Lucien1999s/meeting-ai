import os
import sys
import pytest
from unittest.mock import patch

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from src.speech_to_text import SpeechToTextConverter


@pytest.fixture
def converter():
    return SpeechToTextConverter()


@pytest.fixture
def mock_file_path():
    with patch("src.speech_to_text.os.path.abspath", return_value="/mock/file/path"):
        yield


def test_get_transcript_usage(converter):
    converter.audio_minutes = 10
    expected_cost = 0.006 * converter.audio_minutes

    audio_minutes, cost = converter.get_transcript_usage()

    assert audio_minutes == converter.audio_minutes
    assert cost == expected_cost


def test_speech_to_text_api(mocker, converter, tmpdir, mock_file_path):
    file_path = "/mock/file/path"  # 使用模擬的文件路徑
    use_api = True
    expected_transcript = "This is a test transcript."
    expected_audio_minutes = 90

    test_folder = tmpdir.mkdir("audio_segments")
    mp3_file = test_folder.join("test_audio.mp3")
    mp3_file.write("Test audio content")

    converter._convert_to_mp3 = lambda file_path: str(mp3_file)
    converter._split_audio = lambda file_path: str(test_folder)

    mock_transcribe = mocker.patch("src.speech_to_text.openai.Audio.transcribe")
    mock_transcribe.return_value = {"text": expected_transcript}

    converter._calculate_audio_minutes = lambda audio_path: expected_audio_minutes

    result = converter.speech_to_text(file_path, use_api)
    result = result.replace("\n", " ")

    assert result == expected_transcript
    assert converter.audio_minutes == expected_audio_minutes

    mock_transcribe.assert_called_once_with(converter.api_model, mocker.ANY)

    assert os.path.exists(str(test_folder))


def test_speech_to_text_oss(mocker, converter, mock_file_path):
    file_path = "/mock/file/path"  # 使用模擬的文件路徑
    use_api = False
    expected_transcript = "This is a test transcript."

    mock_transcribe = mocker.patch.object(converter, "_call_whisper_oss")
    mock_transcribe.return_value = expected_transcript

    result = converter.speech_to_text(file_path, use_api)
    assert result == expected_transcript

    mock_transcribe.assert_called_once_with(file_path)
