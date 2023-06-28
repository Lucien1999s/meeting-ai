"""
This module provides a ReportGenerator class for generating meeting reports using the OpenAI API.

It includes the following functionalities:
- Generating summaries based on meeting transcripts
- Generating follow-ups based on meeting transcripts

Usage:
1. Initialize the ReportGenerator object.
2. Call the `generate_report` method to generate a meeting report.

Example:
    generator = ReportGenerator()
    summary, follow_ups = generator.generate_report(meeting_transcript)
"""
import os
import time
import logging
from typing import Tuple
import openai
from openai import OpenAIError
import tiktoken
from dotenv import load_dotenv
from sumy.parsers.plaintext import PlaintextParser
from sumy.nlp.tokenizers import Tokenizer
from sumy.summarizers.lsa import LsaSummarizer
from pygtrans import Translate


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
    def _chunk_transcript(transcript: str, chunk_size: int = 4000) -> list:
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

    @staticmethod
    def _sumy_transcript(chinese_texts, num_sentences=23):
        """Generates summaries for a list of transcripts texts using the Sumy library.

        Args:
            chinese_texts (list[str]): A list of Chinese texts to be summarized.
            num_sentences (int, optional): The number of sentences to include in the summary.
                Defaults to 3.

        Returns:
            list[str]: A list of aggregated_strings corresponding to the input Chinese texts.

        Raises:
            ValueError: If the input `chinese_texts` is not a list.
        """
        if not isinstance(chinese_texts, list):
            raise ValueError("Input 'chinese_texts' must be a list of strings.")

        translator = Translate()
        aggregated_strings = []

        for chinese_text in chinese_texts:
            english_text = translator.translate(
                chinese_text, target="en"
            ).translatedText
            parser = PlaintextParser.from_string(english_text, Tokenizer("english"))
            summarizer = LsaSummarizer()
            summary = summarizer(parser.document, num_sentences)

            summary_text = " ".join(str(sentence) for sentence in summary)
            translated_summary = translator.translate(
                summary_text, target="zh-TW"
            ).translatedText
            aggregated_strings.append(translated_summary)
        logging.info("Aggregated: %s", aggregated_strings)

        return aggregated_strings

    def _generate_summary(self, aggregated_strings: str) -> str:
        """
        Generates a summary based on the aggregated strings.

        Args:
            aggregated_strings (str): The aggregated strings from the meeting records.

        Returns:
            str: The generated summary as a string.
        """
        content = """
        會議紀錄：
        「{aggregated_strings}」
        你要從以上會議紀錄摘要出重點討論的事項之重點說明
        你的回應格式：

        1.[事件標題]：
        - [事件重點簡短說明]
        2.[事件標題]：
        - [事件重點簡短說明]
        
        我要你潤飾文字和修正錯字，並且寫易讀性高的回應
        你會統整重要的項目，盡量讓重點說明數量簡潔
        你的回應：
        """
        prompt = content.format(aggregated_strings=aggregated_strings)
        system_prompt = "你是一個會議紀錄分析師，你會根據會議紀錄來條列出會議中的重點說明"
        summary = self._call_openai_api(
            prompt=prompt, system_prompt=system_prompt, temperature=0.1, max_tokens=1200
        )
        logging.info("Successfully generate summary.")
        return summary

    def _generate_follow_ups(self, aggregated_strings: str) -> str:
        """
        Generates follow ups based on the aggregated strings.

        Args:
            aggregated_strings (str): The aggregated strings from the meeting records.

        Returns:
            str: The generated follow ups as a string.
        """
        content = """
        會議紀錄：
        「{aggregated_strings}」
        你要根據以上會議紀錄來摘要出會議後要做的重點事項
        我要你只給出重要的要做的事
        你會以該公司員工的角度寫要做的事情
        你的回應格式：

        - [要做的重點事項]
        
        我要你潤飾文字和修正錯字，並且寫易讀性高的回應
        你只統整重要的事情，並讓要做的事情數量簡潔
        你的回應：
        """
        prompt = content.format(aggregated_strings=aggregated_strings)
        system_prompt = "你是一個會議紀錄分析師，你會根據會議紀錄來條列出會議中提到會議後需要做的重點事項"
        follow_ups = self._call_openai_api(
            prompt=prompt, system_prompt=system_prompt, temperature=0.1, max_tokens=1000
        )
        logging.info("Successfully generate follow ups.")
        return follow_ups

    @staticmethod
    def _process_string(input_str: str) -> str:
        """
        Processes the input string by extracting lines before
        the last line starting with a hyphen.

        Args:
            input_str (str): The input string to be processed.

        Returns:
            str: The processed string.
        """
        lines = input_str.split("\n")
        last_line_index = None

        for i in range(len(lines) - 1, -1, -1):
            if lines[i].startswith("-"):
                last_line_index = i
                break

        if last_line_index is not None:
            processed_lines = lines[: last_line_index + 1]
            processed_str = "\n".join(processed_lines)
            input_str = processed_str

        lines = input_str.split("\n")
        unique_lines = []

        for line in lines:
            if not any(
                line in unique_line or unique_line in line
                for unique_line in unique_lines
            ):
                unique_lines.append(line)

        return "\n".join(unique_lines)

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

    def generate_report(self, meeting_transcript: str) -> Tuple[str, str]:
        """Generates a report based on the meeting transcript.

        Args:
            meeting_transcript (str): The meeting transcript as a string.

        Returns:
            Tuple[str, str]: A tuple containing the generated summary and follow-ups as strings.
        """
        transcript_chunks = self._chunk_transcript(meeting_transcript)
        aggregated_strings = self._sumy_transcript(transcript_chunks)
        summary = self._process_string(self._generate_summary(aggregated_strings))
        follow_ups = self._process_string(self._generate_follow_ups(aggregated_strings))

        return summary, follow_ups
