"""
This module provides a ReportGenerator class for generating meeting
reports using the OpenAI API.

It includes the following functionalitie:
- Generating summaries based on meeting transcripts

Usage:
1. Initialize the ReportGenerator object.
2. Call the `generate_report` method to generate a meeting report.

Example:
    generator = ReportGenerator()
    summary = generator.generate_report(meeting_transcript)
"""
import os
import time
import logging
from typing import Tuple
import openai
from openai import OpenAIError
import tiktoken
from dotenv import load_dotenv

load_dotenv()
logging.basicConfig(level=logging.INFO)


class ReportGenerator:
    """
    ReportGenerator class provides methods for generating
    meeting reports using OpenAI API.

    Attributes:
        model (str): The model used for report generation.
    """

    def __init__(self):
        """Initializes a ReportGenerator object.

        Sets the default values for the prompt tokens,
        completion tokens, and total cost.
        The OpenAI API key is retrieved from
        the environment variable OPENAI_API_KEY.
        """
        self.prompt_tokens = 0
        self.completion_tokens = 0
        self.total_cost = 0
        openai.api_key = os.environ.get("OPENAI_API_KEY")

    def _call_openai_api(
        self, prompt: str, system_prompt: str, temperature: float, max_tokens: int
    ) -> str:
        """Calls the OpenAI API for chat completion and returns the response.

        Args:
            prompt (str): The user's prompt for chat completion.
            system_prompt (str): The system's prompt for chat completion.
            temperature (float): Controls the randomness of the response.
            max_tokens (int): The maximum number of tokens in the
            generated response.

        Returns:
            str: The generated chat response.

        Raises:
            OpenAIError: If there is an error while calling the OpenAI API.
        """
        token_count = (
            self._count_tokens(prompt) + self._count_tokens(system_prompt) + max_tokens
        )
        model = "gpt-3.5-turbo-16k" if token_count > 4095 else "gpt-3.5-turbo"

        for retry in range(3):
            try:
                response = openai.ChatCompletion.create(
                    model=model,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": prompt},
                    ],
                    temperature=temperature,
                    max_tokens=max_tokens,
                )
                prompt_tokens = response["usage"]["prompt_tokens"]
                completion_tokens = response["usage"]["completion_tokens"]
                cost = self._count_cost(model, prompt_tokens, completion_tokens)
                res = response["choices"][0]["message"]["content"]
                self.prompt_tokens += prompt_tokens
                self.completion_tokens += completion_tokens
                self.total_cost += cost

                logging.info("Use model: %s", model)
                logging.info("Prompt tokens: %f", prompt_tokens)
                logging.info("Completion tokens: %f", completion_tokens)
                logging.info("Cost: %f USD", cost)
                logging.info(res)

                return res
            except OpenAIError as error:
                logging.error("Error: %s", error)
                if retry == 2:
                    logging.error(
                        "Failed to generate a response after 3 attempts. Aborting."
                    )
                    raise
                logging.warning("Retrying (%d/3) after 10 seconds...", retry + 1)
                time.sleep(10)
        return ""

    @staticmethod
    def _chunk_transcript(transcript: str, chunk_size: int = 6000) -> list:
        """Splits the transcript into chunks of a specified size.

        Args:
            transcript (str): The transcript to be chunked.
            chunk_size (int, optional): The maximum size of each chunk.
            Defaults to 6000.

        Returns:
            list: A list of transcript chunks.
        """
        transcript_chunks = []
        current_chunk = ""
        current_length = 0

        for char in transcript:
            if current_length < chunk_size:
                current_chunk += char
                if "\u4e00" <= char <= "\u9fff":
                    current_length += 1
            else:
                transcript_chunks.append(current_chunk)
                current_chunk = char
                current_length = 1

        if current_chunk:
            transcript_chunks.append(current_chunk)

        logging.info("Split into %d chunks.", len(transcript_chunks))
        logging.info("Successfully chunked transcripts.")
        return transcript_chunks

    def _process_transcripts(self, transcript_chunks: list) -> list:
        """
        Processes the transcripts chunks and generates descriptive
        paragraphs for meeting records.

        Args:
            transcript_chunks (list): List of transcript chunks.

        Returns:
            list: Processed transcripts as descriptive paragraphs.
        """
        content = """
        會議逐字稿：
        「{transcript_chunk}」
        你的任務是將以上會議逐字稿寫成800字長篇會議紀錄敘述段落
        我要你詳細記錄所有提到的事項和重要內容
        格式是敘述式段落
        你的回應以此開頭：在這次會議中...
        """
        processed_transcripts = []
        for transcript_chunk in transcript_chunks:
            prompt = content.format(transcript_chunk=transcript_chunk)
            system_prompt = "你是一個會議逐字稿整理專家，專門將會議逐字稿內容寫成會議紀錄敘述段落"
            processed_transcript = self._call_openai_api(
                prompt=prompt,
                system_prompt=system_prompt,
                temperature=0.1,
                max_tokens=1200,
            )
            processed_transcript = processed_transcript.replace("\n", "")
            processed_transcripts.append(processed_transcript)
        logging.info("Successfully processed transcripts.")
        return processed_transcripts

    def _generate_paragraph(self, processed_transcripts: list) -> str:
        """
        Generates paragraphs based on the processed transcripts.

        Args:
            processed_transcripts (list): The processed transcripts list from
            the meeting records.

        Returns:
            str: The generated paragraphs as a string.
        """
        content = """
        以下是一個會議紀錄
        你看完整個會議錄後，要為這些會議記錄摘要列表重新統整起來寫一個長篇專業會議敘述文
        會議紀錄：
        「{processed_transcripts}」
        必須邏輯清楚的來寫整個會議紀錄的所有討論內容
        格式上，應以專業報告形式，段落式書寫
        你的回應以此開頭：在此次會議中...
        """
        prompt = content.format(processed_transcripts=processed_transcripts)
        system_prompt = "你是一個專門為會議記錄進行整理並寫一個長篇專業敘述文的專家"
        paragraphs = self._call_openai_api(
            prompt=prompt, system_prompt=system_prompt, temperature=0.1, max_tokens=3000
        )
        logging.info("Successfully generate paragraphs.")
        return paragraphs


    def _generate_summary(self, paragraphs: str) -> str:
        """
        Generates a summary based on paragraphs.

        Args:
            paragraphs (str): The summaries paragraphs from
            the meeting records.

        Returns:
            str: The generated summary as a string.
        """
        content = """
        會議紀錄：
        「{paragraphs}」
        你的任務是從以上會議紀錄摘要出討論的事件和相應事件的重點敘述
        根據討論內容來數字逐列事件，要重點敘述該事件的重點
        根據會議紀錄中的每件事情適當分類說明

        會議摘要格式：
        1.[事件標題]：
        - 事件重點說明...
        2.[事件標題]：
        - 事件重點說明...

        我要你潤飾文字和修正錯字，並且寫易讀性高的會議摘要
        你的回應以此開頭：1 ...
        """
        prompt = content.format(paragraphs=paragraphs)
        system_prompt = "你是一個會議紀錄分析師，你會根據會議紀錄來數字條列出會議中的事件並重點敘述每一項事件"
        summary = self._call_openai_api(
            prompt=prompt, system_prompt=system_prompt, temperature=0.2, max_tokens=1500
        )
        logging.info("Successfully generate summary.")
        return summary

    @staticmethod
    def _process_string(input_str: str) -> str:
        """
        Process the input string and return the processed string.

        Args:
            input_str (str): The input string to be processed.

        Returns:
            str: The processed string.
        """
        input_str = input_str.replace("[", "").replace("]", "")
        lines = input_str.split("\n")
        last_empty_line_index = None

        for i in range(len(lines) - 1, -1, -1):
            if lines[i].strip() == "":
                last_empty_line_index = i
                break

        if last_empty_line_index is not None and last_empty_line_index < len(lines) - 1:
            next_line = lines[last_empty_line_index + 1].strip()
            if not next_line[0].isdigit():
                output_str = "\n".join(lines[:last_empty_line_index])
            else:
                output_str = input_str
        else:
            output_str = input_str

        return output_str

    @staticmethod
    def _count_cost(
        model: str, prompt_tokens: float, completion_tokens: float
    ) -> float:
        """
        Count the cost of using the language model based on the model type and token counts.

        Args:
            model (str): The name of the language model.
            prompt_tokens (float): The number of tokens in the prompt.
            completion_tokens (float): The number of tokens in the completion.

        Returns:
            float: The calculated cost.
        """
        if model == "gpt-3.5-turbo":
            return (prompt_tokens / 1000) * 0.0015 + (completion_tokens / 1000) * 0.002
        return (prompt_tokens / 1000) * 0.003 + (completion_tokens / 1000) * 0.004

    def _count_tokens(self, content: str, model: str = "gpt-3.5-turbo-0613") -> int:
        """
        Returns the number of tokens used by a list of messages.

        Args:
            content (str): The content of the message.
            model (str, optional): The name of the language model. Defaults to "gpt-3.5-turbo-0613".

        Returns:
            int: The number of tokens used by the messages.

        Raises:
            NotImplementedError: If the specified model is not implemented.
        """
        messages = [
            {
                "role": "user",
                "content": content,
            },
        ]
        try:
            encoding = tiktoken.encoding_for_model(model)
        except KeyError:
            logging.warning("Warning: model not found. Using cl100k_base encoding.")
            encoding = tiktoken.get_encoding("cl100k_base")
        if model in {
            "gpt-3.5-turbo-0613",
            "gpt-3.5-turbo-16k-0613",
            "gpt-4-0314",
            "gpt-4-32k-0314",
            "gpt-4-0613",
            "gpt-4-32k-0613",
        }:
            tokens_per_message = 3
            tokens_per_name = 1
        elif model == "gpt-3.5-turbo-0301":
            tokens_per_message = 4
            tokens_per_name = -1
        else:
            raise NotImplementedError(
                f"""num_tokens_from_messages() is not implemented for model {model}."""
            )
        num_tokens = 0
        for message in messages:
            num_tokens += tokens_per_message
            for key, value in message.items():
                num_tokens += len(encoding.encode(value))
                if key == "name":
                    num_tokens += tokens_per_name
        num_tokens += 3
        return num_tokens

    def get_report_usage(self) -> Tuple[int, int, int, float]:
        """Calculate the report usage.

        Returns:
            Tuple[int, int, int, float]: A tuple containing
            the prompt tokens, completion tokens,
            total tokens, and total cost.
        """
        prompt_tokens = self.prompt_tokens
        completion_tokens = self.completion_tokens
        total_tokens = prompt_tokens + completion_tokens
        total_cost = self.total_cost

        return prompt_tokens, completion_tokens, total_tokens, total_cost

    def generate_report(self, meeting_transcript: str) -> str:
        """Generates a report based on the meeting transcript.

        Args:
            meeting_transcript (str): The meeting transcript as a string.

        Returns:
            str: The generated report.
        """
        transcript_chunks = self._chunk_transcript(meeting_transcript)
        processed_transcripts = self._process_transcripts(transcript_chunks)
        paragraphs = self._generate_paragraph(processed_transcripts)
        summary = self._process_string(self._generate_summary(paragraphs))
        return summary
