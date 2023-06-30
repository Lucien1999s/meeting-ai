"""
This module provides a ReportGenerator class for generating meeting reports using the OpenAI API.

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
    ReportGenerator class provides methods for generating meeting reports using OpenAI API.

    Attributes:
        model (str): The model used for report generation.
    """

    def __init__(self):
        """Initializes a ReportGenerator object.

        Sets the default values for the prompt tokens, completion tokens, and total cost.
        The OpenAI API key is retrieved from the environment variable OPENAI_API_KEY.
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
            max_tokens (int): The maximum number of tokens in the generated response.

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
            chunk_size (int, optional): The maximum size of each chunk. Defaults to 4000.

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

    def _generate_summary(self, processed_transcripts: list) -> str:
        """
        Generates a summary based on the processed transcripts.

        Args:
            processed_transcripts (str): The aggregated strings from the meeting records.

        Returns:
            str: The generated summary as a string.
        """
        content = """
        會議紀錄：
        「{processed_transcripts}」
        你的任務是從以上會議紀錄摘要出討論的事件和相應事件的說明敘述段落
        要詳細記錄討論到的事件，說明敘述段落要詳細記錄
        會議摘要格式：
        1.[事件標題]：
        會議中提到此事件...
        2.[事件標題]：
        會議中提到此事件...
        
        我要你將相關的小項目歸類成同一個大項目且內容要詳細
        我要你潤飾文字和修正錯字，並且寫易讀性高的會議摘要
        你的回應以此開頭：1 ...
        """
        prompt = content.format(processed_transcripts=processed_transcripts)
        system_prompt = "你是一個會議紀錄分析師，你會根據會議紀錄來條列出會議中的說明敘述段落"
        summary = self._call_openai_api(
            prompt=prompt, system_prompt=system_prompt, temperature=0.2, max_tokens=2000
        )
        logging.info("Successfully generate summary.")
        return summary

    @staticmethod
    def _process_string(input_str: str) -> str:
        """
        Processes the input string by extracting lines before
        the last empty line, if the next line does not start with a digit.

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
        if model == "gpt-3.5-turbo":
            return (prompt_tokens / 1000) * 0.0015 + (completion_tokens / 1000) * 0.002
        return (prompt_tokens / 1000) * 0.003 + (completion_tokens / 1000) * 0.004

    def _count_tokens(self, content, model="gpt-3.5-turbo-0613"):
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
            print("Warning: model not found. Using cl100k_base encoding.")
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
        elif "gpt-3.5-turbo" in model:
            print(
                "Warning: gpt-3.5-turbo may update over time. Returning num tokens assuming gpt-3.5-turbo-0613."
            )
            return self._count_tokens(messages, model="gpt-3.5-turbo-0613")
        elif "gpt-4" in model:
            print(
                "Warning: gpt-4 may update over time. Returning num tokens assuming gpt-4-0613."
            )
            return self._count_tokens(messages, model="gpt-4-0613")
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
            Tuple[int, int, int, float]: A tuple containing the prompt tokens, completion tokens,
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
            Tuple[str, str]: A tuple containing the generated summary and follow-ups as strings.
        """
        transcript_chunks = self._chunk_transcript(meeting_transcript)
        processed_transcripts = self._process_transcripts(transcript_chunks)
        summary = self._process_string(self._generate_summary(processed_transcripts))

        return summary
