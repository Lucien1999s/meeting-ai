

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

    def _call_openai(
        self, prompt: str, system_prompt: str, temperature: float, max_tokens: int
    ) -> str:
        """"""
        if self._count_tokens(prompt) + self._count_tokens(system_prompt) + max_tokens > 4000:
            model = "gpt-3.5-turbo-16k"
        else:
            model = "gpt-3.5-turbo"
        retries = 0
        while retries < 3:
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
                cost = self._count_cost(model,prompt_tokens,completion_tokens)
                res = response["choices"][0]["message"]["content"]
                self.prompt_tokens += prompt_tokens
                self.completion_tokens += completion_tokens
                self.total_cost += cost
                print("Use model:", model)
                print("Prompt:", prompt_tokens)
                print("Completion:", completion_tokens)
                print("Cost: ",cost," USD")
                print(res)
                return res
            except OpenAIError as e:
                print("Error:", e)
                retries += 1
                if retries == 3:
                    print("Failed to generate a response after 3 attempts. Aborting.")
                    raise
                else:
                    print(f"Retrying ({retries}/3) after 10 seconds...")
                    time.sleep(10)

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

        print("Split to", len(transcript_chunks), " chunks.")
        print("Successfully chunked transcripts.")
        return transcript_chunks
    
    @staticmethod
    def _count_cost(model: str,prompt_tokens: float,completion_tokens: float) -> float:
        if model == "gpt-3.5-turbo":
            return (prompt_tokens/1000) * 0.0015 + (completion_tokens/1000) * 0.002
        else:
            return (prompt_tokens/1000) * 0.003 + (completion_tokens/1000) * 0.004

    def _count_tokens(self,content: str, model="gpt-3.5-turbo-0301") -> int:
        """
        Returns the number of tokens used by a list of messages.

        Args:
            content (str): The content of the message.
            model (str, optional): The name of the language model. Defaults to "gpt-3.5-turbo-0301".

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
            encoding = tiktoken.get_encoding("cl100k_base")
        if model == "gpt-3.5-turbo":
            return self._count_tokens(messages, model="gpt-3.5-turbo-0301")
        elif model == "gpt-4":
            return self._count_tokens(messages, model="gpt-4-0314")
        elif model == "gpt-3.5-turbo-0301":
            tokens_per_message = 4  
            tokens_per_name = -1  
        elif model == "gpt-4-0314":
            tokens_per_message = 3
            tokens_per_name = 1
        else:
            raise NotImplementedError("error")
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
    def _sumy(chinese_texts, num_sentences=25):
        """Generates summaries for a list of Chinese texts using the Sumy library.

        Args:
            chinese_texts (list[str]): A list of Chinese texts to be summarized.
            num_sentences (int, optional): The number of sentences to include in the summary.
                Defaults to 3.

        Returns:
            list[str]: A list of summaries corresponding to the input Chinese texts.

        Raises:
            ValueError: If the input `chinese_texts` is not a list.
        """
        if not isinstance(chinese_texts, list):
            raise ValueError("Input 'chinese_texts' must be a list of strings.")

        translator = Translate()
        summaries = []

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
            summaries.append(translated_summary)
        print(summaries)

        return summaries

    def _generate_summary(self, aggregated_strings: str) -> str:
        """
        Generates a highlight based on the aggregated strings.

        Args:
            aggregated_strings (str): The aggregated strings from the meeting records.

        Returns:
            str: The generated highlight as a string.
        """
        content = """
        會議紀錄：
        「{aggregated_strings}」
        你要從以上會議紀錄摘要出重點討論的事項之重點說明
        你的回應格式：

        1.[事件標題]：
        - [事件重點說明]
        
        我要你潤飾文字和修正錯字，並且寫易讀性高的回應
        你的回應：
        """
        prompt = content.format(aggregated_strings=aggregated_strings)
        system_prompt = "你是一個會議紀錄分析師，你會根據會議紀錄來條列出會議中的重點說明"
        highlight = self._call_openai(
            prompt=prompt, system_prompt=system_prompt, temperature=0.1, max_tokens=1000
        )
        print("Successfully generate highlight.")
        return highlight

    def _generate_follow_ups(self, aggregated_strings: str) -> str:
        """
        Generates a progress report based on the aggregated strings.

        Args:
            aggregated_strings (str): The aggregated strings from the meeting records.

        Returns:
            str: The generated progress report as a string.
        """
        content = """
        會議紀錄：
        「{aggregated_strings}」
        你要根據以上會議紀錄來摘要出會議後要做的重點事項
        你的回應格式：

        - [要做的重點事項]
        
        我要你潤飾文字和修正錯字，並且寫易讀性高的回應
        你的回應：
        """
        prompt = content.format(aggregated_strings=aggregated_strings)
        system_prompt = "你是一個會議紀錄分析師，你會根據會議紀錄來條列出會議中提到會議後需要做的重點事項"
        todo_list = self._call_openai(
            prompt=prompt, system_prompt=system_prompt, temperature=0.1, max_tokens=1000
        )
        print("Successfully generate progress.")
        time.sleep(10)
        return todo_list

    def get_report_usage(self) -> Tuple[int, int, int, float]:
        """Calculate the report usage.

        Returns:
            Tuple[int, int, int, float]: A tuple containing the prompt tokens, completion tokens,
            total tokens, and cost.
        """
        prompt_tokens = self.prompt_tokens
        completion_tokens = self.completion_tokens
        total_tokens = prompt_tokens + completion_tokens
        total_cost = self.total_cost

        return prompt_tokens, completion_tokens, total_tokens, total_cost
    
    @staticmethod
    def _process_string(input_str: str) -> str:
        lines = input_str.split("\n")
        last_line_index = None

        for i in range(len(lines)-1, -1, -1):
            if lines[i].startswith("-"):
                last_line_index = i
                break

        if last_line_index is not None:
            processed_lines = lines[:last_line_index+1]
            processed_str = "\n".join(processed_lines)
            return processed_str
        else:
            return input_str


    def generate_report(
        self, meeting_transcript: str, file_path: str, meeting_name: str
    ) -> str:
        """Generates a meeting report based on the meeting transcript and saves it to a file.

        Args:
            meeting_transcript (str): Transcript of the meeting.
            file_path (str): File path to save the report.
            meeting_name (str): Name of the meeting.

        Returns:
            str: The generated meeting report.
        """
        transcript_chunks = self._chunk_transcript(meeting_transcript)
        aggregated_strings = self._sumy(transcript_chunks)
        summary = self._process_string(self._generate_summary(aggregated_strings))
        follow_ups = self._process_string(self._generate_follow_ups(aggregated_strings))

        report = (
            meeting_name
            + "\n\n"
            + "會議重點:\n"
            + summary
            + "\n\n"
            + "後續行動：\n"
            + follow_ups
        )
        report_dir = os.path.dirname(file_path)
        report_file_name = os.path.basename(file_path).replace(
            os.path.splitext(file_path)[1], "_report.txt"
        )
        report_file_path = os.path.join(report_dir, report_file_name)

        with open(report_file_path, "w", encoding="utf-8") as report_file:
            report_file.write(report)

        return report
