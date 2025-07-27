"""Generates reports from meeting transcripts using OpenAI's ChatCompletion API.

This class provides a convenient interface for processing meeting transcripts and generating detailed reports.

Attributes:
    transcript (str): The input meeting transcript to be processed.
    model (str): The name of the model to be used for processing the transcript.
    api_key (str): The API key for accessing the processing service.

Methods:
    generate_report(): Generates a report from the transcript data.
    _count_tokens(content, model): Counts the number of tokens in the given content using the specified language model.
    _split_large_text(large_text, max_tokens): Splits a large text into smaller chunks of a specified maximum token length.

Raises:
    NotImplementedError: If the specified model is not supported.

Returns:
    str: The generated report content based on the processed transcript data.

Example:
    generator = ReportGenerator(
        transcript=transcript, 
        model="gpt-3.5-turbo", 
        api_key="sk-...", 
        logging_level=logging.INFO
    )
    report = generator.generate_report()
    print(report)
"""

import re
import math
import logging
from typing import List, Tuple

import tiktoken
from parallel_process_utils.api_parallel_processor import ParallelProcessor


class ReportGenerator:
    """A class for generating reports using OpenAI's ChatCompletion API."""

    def __init__(
        self,
        transcript: str,
        model: str,
        api_key: str,
        logging_level: int = logging.INFO,
    ):
        """
        Initializes the instance with the given transcript, model, and API key.

        Args:
            transcript (str): The transcript to be processed.
            model (str): The name of the model to be used for processing the transcript.
            api_key (str): The API key for accessing the processing service.
            logging_level (int, optional): The logging level for the instance (default is logging.INFO).
        """
        self.transcript = transcript
        self.model = model
        self.prompt_tokens = 0
        self.completion_tokens = 0
        self.api_key = api_key
        logging.basicConfig(level=logging_level)
        self.processor = ParallelProcessor(
            request_url="https://api.openai.com/v1/chat/completions",
            api_key=self.api_key,
            model=self.model,
            logging_level="CRITICAL",
            timeout=10,
        )
        self.model_limit = self._get_model_limit()

    def _openai_parallel_request(
        self,
        prompt_list: list,
        system_prompt_list: list,
        max_token: int = 1000,
        temperature: float = 0.0,
        max_attempts: int = 3,
    ) -> list:
        """
        Use the Parallel-Processor package to send parallel requests to the OpenAI API and return responses from the assistant.
        If the response structure is unexpected, the function will attempt to call the API again, up to a maximum number of attempts.

        Args:
            prompt_list (list): A list of prompts for the assistant.
            system_prompt_list (list): A list of system prompts for the assistant.
            max_token (int, optional): The maximum number of tokens that the model can generate. Defaults to 1000.
            temperature (float, optional): The temperature parameter for the model, controlling the randomness of the output. Defaults to 0.0.
            max_attempts (int, optional): The maximum number of attempts to call the API if the response structure is unexpected. Defaults to 3.

        Returns:
            list: A list of the assistant's responses.
        """
        for attempt in range(max_attempts):
            requests_data = [
                {
                    "model": self.model,
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": prompt},
                    ],
                    "max_tokens": max_token,
                    "temperature": temperature,
                }
                for prompt, system_prompt in zip(prompt_list, system_prompt_list)
            ]
            response = self.processor.parallel_request(requests_data=requests_data)
            logging.info(f"parallel response:{response}")

            try:
                # Extract assistant's responses
                assistant_responses = [
                    item[2]["choices"][0]["message"]["content"] for item in response
                ]

                # Calculate total prompt tokens and completion tokens
                self.prompt_tokens += sum(
                    item[2]["usage"]["prompt_tokens"] for item in response
                )
                self.completion_tokens += sum(
                    item[2]["usage"]["completion_tokens"] for item in response
                )

                return assistant_responses
            except Exception as e:
                logging.error(f"Attempt {attempt+1} failed with error: {e}")
                if attempt + 1 == max_attempts:
                    raise e

    def _get_model_limit(self) -> int:
        """
        This method is used to get the maximum context length (in tokens) that a specific OpenAI model can handle.
        It sends a request with an intentionally large number of tokens, then parses the error message to find the model's limit.

        Returns:
            int: The maximum context length (in tokens) that the model can handle.

        Raises:
            ValueError: If the error message does not contain the expected information.
        """
        # Set up logging
        logger = logging.getLogger(__name__)
        logger.setLevel(logging.ERROR)
        handler = logging.StreamHandler()
        handler.setFormatter(
            logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
        )
        logger.addHandler(handler)

        requests_data = [
            {
                "model": self.model,
                "messages": [
                    {"role": "user", "content": "Hello"},
                ],
                "max_tokens": 1000000000,
                "temperature": 0.1,
            }
        ]
        try:
            response = self.processor.parallel_request(requests_data=requests_data)
            error_message = response[0][2]["error"]["message"]
            match = re.search(
                r"This model's maximum context length is (\d+)", error_message
            )
            if match:
                max_context_length = int(match.group(1))- 100
                logging.info(max_context_length)
                return max_context_length
            else:
                raise ValueError(
                    "Could not find the model's maximum context length in the error message."
                )
        except Exception as e:
            logger.error(
                f"An error occurred while trying to get the model's maximum context length: {e}"
            )
            raise

    def _best_choice_split(self, split_data: str) -> Tuple[List[str], bool]:
        """
        Splits the input data into chunks based on the model's token limit.

        This function calculates the total tokens in the input data and splits it into chunks. Each chunk is 
        designed to be within the model's token limit when combined with completion and prompt tokens. If the 
        total tokens are within the model limit, the function returns the whole transcript. The function also 
        adjusts the size of other chunks if the last chunk is smaller than the minimum chunk length.

        Args:
            split_data (str): The input data to be split into chunks.

        Returns:
            list: A list of chunks obtained from the input data.
            bool: A boolean value indicating whether the total tokens are within the model limit.
        """

        # Constants for completion and prompt tokens, and minimum chunk length
        COMPLETION_TOKEN = 1000
        PROMPT_TOKEN = 200
        CHUNK_MIN_LENGTH = 1000
        pass_limit = False

        # Calculate total tokens in the transcript including completion and prompt tokens
        transcript_token = self._count_tokens(split_data)
        total_tokens = transcript_token + COMPLETION_TOKEN + PROMPT_TOKEN
        logging.info(f"tokens:{transcript_token}")
        logging.info(f"tokens:{total_tokens}")
        # If total tokens are within the model limit, return the whole transcript
        if total_tokens + 1000 < self.model_limit:
            logging.info(f"Chunk length: 1, pass limit: {total_tokens + 1000} tokens")
            pass_limit = True
            return [split_data], pass_limit

        # Calculate the maximum number of tokens that can be used for the transcript in each chunk
        available_chunk_space = self.model_limit - COMPLETION_TOKEN - PROMPT_TOKEN

        # Calculate the number of tokens in the last chunk
        last_chunk_space = transcript_token % available_chunk_space

        # If the last chunk is smaller than the minimum chunk length, adjust the size of other chunks
        if last_chunk_space < CHUNK_MIN_LENGTH:
            space_for_remaining_chunks = transcript_token - CHUNK_MIN_LENGTH
            best_chunk = math.ceil(
                space_for_remaining_chunks / (transcript_token // available_chunk_space)
            )
        else:
            best_chunk = available_chunk_space

        # Split the transcript into chunks
        chunks = self._split_large_text(large_text=split_data, max_tokens=best_chunk)
        logging.info(f"Best chunk size:{best_chunk} tokens")
        logging.info(f"Chunk length:{len(chunks)}")
        return chunks, pass_limit

    def _preprocess_chunks(self, chunks: list) -> list:
        """
        This method preprocesses the given chunks of transcripts and converts them into a list of summaries.

        Args:
            chunks (list): A list of transcript chunks to be preprocessed.

        Returns:
            summary_list (list): A list of preprocessed summaries corresponding to the input chunks.

        The function logs the start and successful completion of the preprocessing task.
        """
        logging.info("Start preprocessing transcripts.")
        CONTENT = """會議逐字稿：\n「{chunk}」\n你的任務是將以上會議逐字稿寫成1000字長篇會議紀錄敘述段落，\
        我要你詳細記錄所有提到的事項和重要內容，格式是敘述式段落，你的回應以此開頭：在這次會議中...
        """
        prompt_list = [CONTENT.format(chunk=c) for c in chunks]
        system_prompt_list = [
            "你是一個會議逐字稿整理專家，專門將會議逐字稿內容寫成會議紀錄敘述段落" for _ in range(len(chunks))
        ]
        summary_list = self._openai_parallel_request(
            prompt_list=prompt_list, system_prompt_list=system_prompt_list
        )
        logging.info("Transcript preprocessed successfully.")
        return summary_list

    def _generate_report_content(self, data: str) -> str:
        """
        This method generates a report content from the given data.

        Args:
            data (str): The data to be processed into a report.

        Returns:
            report_content (str): The generated report content based on the input data.

        The function logs the successful generation of the report content.
        """
        logging.info("Start generating report content.")
        content = """會議紀錄：\n「{data}」\n你的任務是從以上會議紀錄摘要出討論的事件和相應事件的重點敘述，根據討論內容來數字逐列事件，要重點敘述該事件的重點\
        根據會議紀錄中的每件事情適當分類說明\n會議摘要格式：\n1.[事件標題]：\n- 事件重點說明...\n2.[事件標題]：\n- 事件重點說明...\
        \n我要你潤飾文字和修正錯字，並且寫易讀性高的會議摘要\n你的回應以此開頭：1 ..."""
        prompt = content.format(data=data)
        system_prompt = "你是一個會議紀錄分析師，你會根據會議紀錄來數字條列出會議中的事件並重點敘述每一項事件"
        report_content = self._openai_parallel_request(
            prompt_list=[prompt],
            system_prompt_list=[system_prompt],
            max_token=2000,
        )
        logging.info("Summary generated successfully.")
        return report_content

    def get_spent_tokens(self) -> dict:
        """
        Retrieves the usage statistics of the instance.

        Returns:
            dict: A dictionary with keys 'prompt tokens' and 'completion tokens', and their respective usage counts as values.
        """
        return {
            "text model": self.model,
            "prompt tokens": self.prompt_tokens,
            "completion tokens": self.completion_tokens,
        }

    def generate_report(self) -> str:
        """
        Generates a summary report based on the transcript data.

        This function calculates the best method to split the transcript data into chunks. 
        It keeps digesting the data until it reaches a specific size. 
        Then, it uses specific prompts to generate summary reports in a specific format.

        Returns:
            str: The first element of the generated report content.
        """
        # Calculate the best cutting method and keep digesting to a specific size
        chunks, _ = self._best_choice_split(split_data=self.transcript)
        while True:
            summary_list = self._preprocess_chunks(chunks=chunks)
            chunks, pass_limit = self._best_choice_split(split_data="".join(summary_list))
            if pass_limit:
                break
        # Use specific prompts to generate summary reports in specific formats
        report_content = self._generate_report_content(data=str(chunks))
        return report_content[0]

    @staticmethod
    def _count_tokens(content: str, model: str = "gpt-3.5-turbo-0613") -> int:
        """
        Count the number of tokens in the given content using the specified language model.

        Args:
            content (str): The content to count tokens for.
            model (str, optional): The language model to use (default is "gpt-3.5-turbo-0613").

        Returns:
            int: The total number of tokens in the content.

        Raises:
            NotImplementedError: If the specified model is not supported.
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

    @staticmethod
    def _split_large_text(large_text: str, max_tokens: int) -> list:
        """
        Splits a large text into smaller chunks of a specified maximum token length.

        Args:
            large_text (str): The large text that needs to be split into smaller chunks.
            max_tokens (int): The maximum number of tokens that each chunk of text can contain.

        Returns:
            list: A list of text chunks, each containing no more than the specified maximum number of tokens.
        """
        enc = tiktoken.get_encoding("cl100k_base")
        tokenized_text = enc.encode(large_text)
        chunks = []
        current_chunk = []
        current_length = 0
        for token in tokenized_text:
            current_chunk.append(token)
            current_length += 1
            if current_length >= max_tokens:
                chunks.append(enc.decode(current_chunk).rstrip(" .,;"))
                current_chunk = []
                current_length = 0
        if current_chunk:
            chunks.append(enc.decode(current_chunk).rstrip(" .,;"))
        return chunks
