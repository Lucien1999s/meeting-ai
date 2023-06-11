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
from typing import List
from src.record_usage import UsageRecorder
from dotenv import load_dotenv

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
        self.model = "gpt-3.5-turbo"
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
        self.prompt_tokens += prompt_tokens
        self.completion_tokens += completion_tokens
        return response["choices"][0]["message"]["content"]

    @staticmethod
    def _chunk_transcript(transcript: str, chunk_size: int = 1800) -> list:
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

        print("Successfully chunked transcripts.")
        return transcript_chunks

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
            這是一份會議記錄逐字稿，幫我記錄討論的重點內容成300字重點摘要敘述：
    
            [會議記錄]
            {transcript_chunks}

            詳細記錄所有該會議記錄中提到的所有資訊成重點內容300字摘要敘述
            """
            prompt = content.format(transcript_chunks=transcript_chunks[i])
            system_prompt = "你是一個專門統整會議記錄摘要的專家"
            try:
                res = self._call_openai(
                    prompt=prompt,
                    system_prompt=system_prompt,
                    temperature=0.3,
                    max_tokens=600,
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

    def _generate_highlight(self, aggregated_strings: str) -> str:
        """Generates a professional meeting content description by reorganizing the aggregated strings.

        Args:
            aggregated_strings (str): Aggregated strings of meeting summary.

        Returns:
            str: Professional meeting content description.
        """
        content = """
        -以下是一個會議紀錄摘要列表，他們是從會議記錄中分段摘要出來的結果
        -你看完整個會議摘要後，要為這些會議記錄摘要列表重新統整起來寫一個850字的專業會議重點敘述

        會議紀錄摘要列表：
        [
        {aggregated_strings}
        ]
        -在你產的專業文章中，必須避免使用像「在第一個摘要中」這樣的描述方式，而應該使用「在此會議中」等更通用的表述
        -必須要用句號結尾
        -必須邏輯清楚的來寫整個會議紀錄的所有討論內容
        -格式上，應以專業報告形式，分成三段來寫：1.敘述討論內容2.總結重點3.適當結論，這樣才能提升閱讀性
        請遵守上述要求，以下請產生850字專業分段會議重點紀錄文：
        """
        prompt = content.format(aggregated_strings=aggregated_strings)
        system_prompt = "你是一個專門為會議記錄進行逐項整理並摘要的專家"
        highlight = self._call_openai(
            prompt=prompt, system_prompt=system_prompt, temperature=0.2, max_tokens=1700
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
        -以下是一個會議紀錄摘要列表，他們是從會議記錄中分段摘要出來的結果
        -你看完整個會議摘要後，從這些會議記錄摘要列表當中找出所有待辦事項
        -必須根據我要的格式羅列出待辦事項的事件名稱
        -必須細分所有的待辦事項，越細越好，越多越好

        會議紀錄摘要列表：
        [
        {aggregated_strings}
        ]
        你的回應格式：
        -----
        1.
        標題：
        2.
        標題：
        ...
        -----
        必須要按照格式為每一項標記數字,且有標題和說明
        待辦事項的每項必須都是很細的單個分工項目
        你產生的逐項會議待辦事項：
        """
        prompt = content.format(aggregated_strings=aggregated_strings)
        system_prompt = "你是一個專門從會議記錄中找出待辦事項並分析整理的專家"
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
        -請你看完所有待辦事項後，針對每個待辦事項給予建議的未來行動規劃
        -未來行動規劃就是如果要完成該項任務，可以從哪裡開始著手
        待辦事項：
        [
        {todo_list}
        ]

        你的格式應該如下：
        -----
        1.
        標題：
        建議：
        2.
        標題：
        建議：
        ...
        -----
        必須要按照格式為每一項標記1234...,且有標題和建議
        且建議不能包含該待辦事項的說明欄位的內容，必須要是針對該待辦事項的推薦行動規劃，越新奇且有用的建議越好
        你產生的逐項待辦事項行動規劃表：
        """
        prompt = content.format(todo_list=todo_list)
        system_prompt = "你是一個針對會議紀錄待辦事項提出好建議的專家"
        recommandations = self._call_openai(
            prompt=prompt, system_prompt=system_prompt, temperature=0.9, max_tokens=1500
        )
        print("Successfully generate recommandations.")
        return recommandations

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
        aggregated_strings = self._summarize_transcript_chunks(transcript_chunks)
        highlight = self._generate_highlight(aggregated_strings)
        todo_list = self._generate_todo(aggregated_strings)
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

        prompt_tokens = self.prompt_tokens
        completion_tokens = self.completion_tokens

        recorder = UsageRecorder()

        recorder.prompt_tokens = prompt_tokens
        recorder.completion_tokens = completion_tokens

        return report
