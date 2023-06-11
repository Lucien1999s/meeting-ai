"""
UsageRecorder class records and calculates usage information.

This module provides the UsageRecorder class, which can be used to record and calculate usage information for various tasks. It includes the following functionalities:

- Calculation of transcript usage
- Calculation of report usage

Usage:
1. Initialize an instance of the UsageRecorder class.
2. Use the class methods to calculate the usage or retrieve the calculated usage.

Example:
    # Initialize the UsageRecorder
    recorder = UsageRecorder()

    # Calculate transcript usage
    transcript_minutes, transcript_cost = recorder.get_transcript_usage()

    # Calculate report usage
    prompt_tokens, completion_tokens, total_tokens, report_cost = recorder.get_report_usage()

"""

from typing import Tuple


class UsageRecorder:
    """UsageRecorder class records and calculates usage information.

    Attributes:
        prompt_tokens (int): The number of prompt tokens.
        completion_tokens (int): The number of completion tokens.
        audio_minutes (float): The duration of the audio in minutes.
    """

    def __init__(self):
        """Initialize the UsageRecorder object.

        This method sets the initial values of prompt_tokens, completion_tokens, and audio_minutes to 0.
        """
        self.audio_minutes = 0
        self.prompt_tokens = 0
        self.completion_tokens = 0

    def _calculate_transcript_usage(self) -> Tuple[float, float]:
        """Calculate the transcript usage.

        Returns:
            Tuple[float, float]: A tuple containing the audio minutes and the total cost.

        """
        audio_minutes = self.audio_minutes
        cost = audio_minutes * 0.006

        return audio_minutes, cost

    def _calculate_report_usage(self) -> Tuple[int, int, int, float]:
        """Calculate the report usage.

        Returns:
            Tuple[int, int, int, float]: A tuple containing the prompt tokens, completion tokens,
            total tokens, and cost.

        """
        prompt_tokens = self.prompt_tokens
        completion_tokens = self.completion_tokens
        total_tokens = prompt_tokens + completion_tokens
        cost = (total_tokens / 1000) * 0.002

        return prompt_tokens, completion_tokens, total_tokens, cost

    def get_transcript_usage(self) -> Tuple[float, float]:
        """Get the transcript usage.

        Returns:
            Tuple[float, float]: A tuple containing the audio minutes and the total cost.

        """
        return self._calculate_transcript_usage()

    def get_report_usage(self) -> Tuple[int, int, int, float]:
        """Get the report usage.

        Returns:
            Tuple[int, int, int, float]: A tuple containing the prompt tokens, completion tokens,
            total tokens, and cost.

        """
        return self._calculate_report_usage()
