"""
Report Generation Module

This module provides a ReportGenerator class for generating meeting reports using the OpenAI API.

The ReportGenerator class includes the following methods:

- generate_report(meeting_transcript: str) -> Tuple[str, str, str]: Generates a meeting report by summarizing the given meeting transcript.
- _call_openai(prompt: str, system_prompt: str, temperature: float, max_tokens: int) -> str: Calls the OpenAI API to generate a response based on the given prompt.
- _chunk_transcript(transcript: str, chunk_size: int = 1800) -> list: Splits the transcript into chunks of a specified size.
- _summarize_transcript_chunks(transcript_chunks: List[str]) -> List[str]: Summarizes the transcript chunks and generates an aggregated summary.
- _generate_highlight(aggregated_strings: str) -> str: Generates a professional meeting content description by reorganizing the aggregated strings.
- _generate_todo(aggregated_strings: str) -> str: Generates a list of meeting todos by extracting them from the aggregated strings.
- _generate_recommendations(todo_list: str) -> str: Generates recommendations for each item in the todo list.

Usage:
1. Initialize a ReportGenerator object.
2. Call the generate_report() method with the meeting transcript as input to generate the meeting report.

Example:
    generator = ReportGenerator()
    highlight, todo_list, recommendations = generator.generate_report(meeting_transcript)

"""

import os
import time
import openai
import tiktoken
from typing import List
from typing import Tuple
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
        """
        Initializes the object.

        This method sets the model to "gpt-3.5-turbo" and sets the OpenAI API key using
        the environment variable "OPENAI_API_KEY".
        """
        self.model = "gpt-3.5-turbo-16k"
        self.prompt_tokens = 0
        self.completion_tokens = 0
        openai.api_key = os.environ.get("OPENAI_API_KEY")

    def _call_openai(
        self, prompt: str, system_prompt: str, temperature: float, max_tokens: int
    ) -> str:
        """Calls the OpenAI API to generate a response based on the given prompt.

        Args:
            prompt (str): The user prompt.
            system_prompt (str): The system prompt.
            temperature (float): Controls the randomness of the output. Higher values result in more random responses.
            max_tokens (int): The maximum number of tokens to generate in the response.

        Returns:
            str: The generated response.
        """
        response = openai.ChatCompletion.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt},
            ],
            temperature=temperature,
            max_tokens=max_tokens,
        )
        prompt_tokens = response["usage"]["prompt_tokens"]
        completion_tokens = response["usage"]["completion_tokens"]
        res = response["choices"][0]["message"]["content"]
        self.prompt_tokens += prompt_tokens
        self.completion_tokens += completion_tokens
        print("Prompt:",prompt_tokens)
        print("Completion:",completion_tokens)
        print(res)
        return res

    @staticmethod
    def _chunk_transcript(transcript: str, chunk_size: int = 4000) -> list:
        """Splits the transcript into chunks of a specified size.

        Args:
            transcript (str): The transcript to be chunked.
            chunk_size (int, optional): The maximum size of each chunk. Defaults to 1800.

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

        print("How many:",len(transcript_chunks))
        # print(transcript_chunks)
        print("Successfully chunked transcripts.")
        return transcript_chunks
    
    @staticmethod
    def _sumy(chinese_texts, num_sentences=25):
        """Generates summaries for a list of Chinese texts using Sumy library.

        Args:
            chinese_texts (list[str]): A list of Chinese texts to be summarized.
            num_sentences (int, optional): The number of sentences to include in the summary. Defaults to 3.

        Returns:
            list[str]: A list of summaries corresponding to the input Chinese texts.

        Raises:
            ValueError: If the input `chinese_texts` is not a list.

        Notes:
            - This method uses the Sumy library for text summarization.
            - Each Chinese text in the input list will be translated to English, summarized in English using Sumy,
            and then translated back to Chinese.
        """
        if not isinstance(chinese_texts, list):
            raise ValueError("Input 'chinese_texts' must be a list of strings.")

        translator = Translate()
        summaries = []

        for chinese_text in chinese_texts:
            english_text = translator.translate(chinese_text, target='en').translatedText
            parser = PlaintextParser.from_string(english_text, Tokenizer("english"))
            summarizer = LsaSummarizer()
            summary = summarizer(parser.document, num_sentences)

            summary_text = " ".join(str(sentence) for sentence in summary)
            translated_summary = translator.translate(summary_text, target='zh-TW').translatedText
            summaries.append(translated_summary)
        print(summaries)

        return summaries


    def _summarize_transcript_chunks(self, transcript_chunks: List[str]) -> List[str]:
        """Summarizes the transcript chunks and generates aggregated summaries.

        Args:
            transcript_chunks (List[str]): A list of transcript chunks.

        Returns:
            List[str]: A list of aggregated summaries.

        Raises:
            openai.error.RateLimitError: If the rate limit for the OpenAI API is reached.
        """
        aggregated_strings = []
        rate_limit_reached = True

        for i in range(len(transcript_chunks)):
            content = """
            -這是一份會議記錄逐字稿
            -我要你將逐字稿中的內容轉換成1000個中文字的不分段長篇敘述
    
            [會議記錄逐字稿]
            「{transcript_chunks}」

            -我要你「詳細記錄所有」該會議記錄中提到的所有資訊
            1000個中文字的不分段長篇敘述：
            """
            prompt = content.format(transcript_chunks=transcript_chunks[i])
            system_prompt = "你是一個專門統整會議記錄摘要的專家"
            try:
                res = self._call_openai(
                    prompt=prompt,
                    system_prompt=system_prompt,
                    temperature=0.3,
                    max_tokens=2200,
                )
                aggregated_strings.append(res)
            except openai.error.RateLimitError:
                rate_limit_reached = True
                print("Rate limit reached. Waiting for 25 seconds...")
                time.sleep(25)
                continue

        if rate_limit_reached:
            print("Rate limit reached. Resuming execution.")

        print("Successfully summarize every chunks.")
        return aggregated_strings
    
    def _count_tokens(self,content, model="gpt-3.5-turbo-0301"):
        """Returns the number of tokens used by a list of messages."""
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

    def _generate_highlight(self, aggregated_strings: str) -> str:
        """Generates a professional meeting content description by reorganizing the aggregated strings.

        Args:
            aggregated_strings (str): Aggregated strings of meeting summary.

        Returns:
            str: Professional meeting content description.
        """
        content = """
        -以下是一個會議紀錄摘要，是從會議記錄中分段摘要出來的結果
        -我要你先看完以下會議紀錄摘要

        會議紀錄摘要：
        [
        {aggregated_strings}
        ]
        -你要你根據這份摘要重寫一份會議紀錄重點整理文章，並且分成三到四個段落書寫，使可讀性更高
        -我要你使用「在此會議中」的表述角度來書寫
        -敘述文內容邏輯必須清楚、語句和段落必須通順流暢且避免頻繁重複使用同一助詞
        以下是你新產生的「會議紀錄重點整理文章」內容：
        """
        prompt = content.format(aggregated_strings=aggregated_strings)
        system_prompt = "你是一個專門為會議記錄摘要進行排版優化和內容整理的專家"
        highlight = self._call_openai(
            prompt=prompt, system_prompt=system_prompt, temperature=0.2, max_tokens=2500
        )
        print("Successfully generate highlight.")
        return highlight

    def _generate_todo(self, aggregated_strings: str) -> str:
        """Generates a list of meeting todos by extracting them from the aggregated strings.

        Args:
            aggregated_strings (str): Aggregated strings of meeting summary.

        Returns:
            str: Meeting todos with event names.
        """
        content = """
        -以下是一個會議紀錄摘要，他們是從會議記錄中摘要出來的結果
        -待辦事項：意思是會議紀錄中提到會議後要去做的事情
        -我要你列出會議紀錄中提到的待辦事項

        會議紀錄摘要：
        [
        {aggregated_strings}
        ]
        你認為以上有提到哪些接下來要去做的待辦事項？
        -我要你用數字條列待辦事項
        -我要你記住「要去做的事情」才是待辦事項
        以下是你產生的數字條列會議待辦事項：
        """
        prompt = content.format(aggregated_strings=aggregated_strings)
        system_prompt = "你是一個專門從會議記錄中找出待辦事項並給予適當標題的專家"
        todo_list = self._call_openai(
            prompt=prompt, system_prompt=system_prompt, temperature=0.3, max_tokens=700
        )
        print("Successfully generate todo list.")
        time.sleep(10)
        return todo_list

    def _generate_recommendations(self, todo_list: str) -> str:
        """Generates recommendations for each item in the todo list.

        Args:
            todo_list (str): List of meeting todos.

        Returns:
            str: Recommendations for each todo item.
        """
        content = """
        -以下是所有會議紀錄的待辦事項
        -我要你針對每個待辦事項給予智能建議
        -智能建議是指如果要完成該項任務，可以從哪裡開始著手
        待辦事項：
        [
        {todo_list}
        ]
        -我要你用數字條列的方式給我[待辦事項和智能建議]，其餘的不要多說
        -必須要是針對該待辦事項的智能建議，我要新奇和有用的智能建議
        以下是你產生的逐項待辦事項智能建議之內容：
        """
        prompt = content.format(todo_list=todo_list)
        system_prompt = "你是一個針對會議紀錄待辦事項提出好建議的專家"
        recommandations = self._call_openai(
            prompt=prompt, system_prompt=system_prompt, temperature=0.9, max_tokens=3000
        )
        print("Successfully generate recommandations.")
        return recommandations
    
    def get_report_usage(self) -> Tuple[int, int, int, float]:
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
        # aggregated_strings = self._summarize_transcript_chunks(transcript_chunks)
        aggregated_strings = self._sumy(transcript_chunks)
        highlight = self._generate_highlight(aggregated_strings)
        todo_list = self._generate_todo(highlight)
        recommendations = self._generate_recommendations(todo_list)

        report = (
            meeting_name
            + "\n\n"
            + "會議紀錄摘要:\n"
            + highlight
            + "\n\n"
            + "待辦事項和智能建議:\n"
            + recommendations
        )
        report_dir = os.path.dirname(file_path)
        report_file_name = os.path.basename(file_path).replace(
            os.path.splitext(file_path)[1], "_report.txt"
        )
        report_file_path = os.path.join(report_dir, report_file_name)

        with open(report_file_path, "w") as report_file:
            report_file.write(report)
        # report= ""
        # print(aggregated_strings)
        return report

if __name__ == "__main__":
    r = ReportGenerator()
