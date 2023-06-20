"""
This module provides a ReportGenerator class for generating meeting reports using the OpenAI API.

It includes the following functionalities:
- Calling the OpenAI API to generate responses based on prompts
- Chunking transcripts into smaller segments
- Summarizing Chinese texts using the Sumy library
- Generating professional meeting content descriptions
- Extracting meeting progress from aggregated strings
- Generating recommendations for each uncomplete task

Usage:
1. Initialize the ReportGenerator object.
2. Call the generate_report method to generate a meeting report based on the meeting transcript.

Example:
    generator = ReportGenerator()
    report = generator.generate_report(meeting_transcript, file_path, meeting_name)

"""

import os
import time
from typing import Tuple
import openai
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

        Sets the default values for the model, prompt tokens, and completion tokens.
        The OpenAI API key is retrieved from the environment variable OPENAI_API_KEY.
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
            temperature (float): Controls the randomness of the output.
                Higher values result in more random responses.
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
        print("Prompt:", prompt_tokens)
        print("Completion:", completion_tokens)
        print(res)
        return res

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

    def _generate_highlight(self, aggregated_strings: str) -> str:
        """
        Generates a highlight based on the aggregated strings.

        Args:
            aggregated_strings (str): The aggregated strings from the meeting records.

        Returns:
            str: The generated highlight as a string.
        """
        content = """
        我要你先閱讀以下會議紀錄：
        「{aggregated_strings}」
        你的任務是根據此公司的會議紀錄提供一段概覽
        你的格式應該如下：
        [一段概覽]
        我要你遵照以上格式要求來提供一段概覽
        你的回應：
        """
        prompt = content.format(aggregated_strings=aggregated_strings)
        system_prompt = "你是一個會議紀錄摘要師，是專門寫出邏輯清晰易讀性強的概覽的摘要師"
        highlight = self._call_openai(
            prompt=prompt, system_prompt=system_prompt, temperature=0.2, max_tokens=1000
        )
        print("Successfully generate highlight.")
        return highlight

    def _generate_progress(self, aggregated_strings: str) -> str:
        """
        Generates a progress report based on the aggregated strings.

        Args:
            aggregated_strings (str): The aggregated strings from the meeting records.

        Returns:
            str: The generated progress report as a string.
        """
        content = """
        我要你先閱讀以下會議紀錄：
        「{aggregated_strings}」
        你的任務是從這個公司的會議紀錄中，列出有完成的事情或專案和待完成的事情或專案，並提供相應的事件敘述
        你列出的每個事項都要有明確的敘述
        你的格式應該如下：

        完成事項：
        - [某完成事件的敘述]
        - [某完成事件的敘述]
        ...

        待完成事項：
        - [某待完成事件的敘述]
        - [某待完成事件的敘述]
        ...
        完成的事項不應該和待完成事項有重疊的事項
        事項與事項之間不支持有過於類似的內容，若有類似的內容請合併為同一項事項
        我要你遵照以上格式要求條列提供完成事項和待完成事項
        你的回應：
        """
        prompt = content.format(aggregated_strings=aggregated_strings)
        system_prompt = "你是一個會議紀錄分析師，專門找到會議紀錄中已經完成的事項和待完成的事項"
        todo_list = self._call_openai(
            prompt=prompt, system_prompt=system_prompt, temperature=0.2, max_tokens=700
        )
        print("Successfully generate progress.")
        time.sleep(10)
        return todo_list

    def _generate_recommendations(self, progress: str) -> str:
        """
        Generates intelligent recommendations for each pending task based on the progress.

        Args:
            progress (str): The progress report containing completed and pending tasks.

        Returns:
            str: The generated recommendations for each pending task as a string.
        """
        content = """
        以下是所有會議紀錄的完成事項和待完成事項
        我要你針對每個待完成事項給予智能建議
        智能建議是指如果要完成該項任務，可以從哪裡開始著手
        完成事項和待完成事項：
        [
        {progress}
        ]
        我要你用數字條列的方式給我[待完成事項和智能建議]，其餘的不要多說
        必須要是針對該待完成事項的智能建議，我要新奇和有用的智能建議
        以下是你產生的逐項待完成事項智能建議之內容：
        """
        prompt = content.format(progress=progress)
        system_prompt = "你是一個針對會議紀錄待完成事項提出好建議的專家"
        recommandations = self._call_openai(
            prompt=prompt, system_prompt=system_prompt, temperature=0.9, max_tokens=2500
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
        aggregated_strings = self._sumy(transcript_chunks)
        highlight = self._generate_highlight(aggregated_strings)
        progress = self._generate_progress(aggregated_strings)
        recommendations = self._generate_recommendations(progress)

        report = (
            meeting_name
            + "\n\n"
            + "會議紀錄概要:\n"
            + highlight
            + "\n\n"
            + "進度：\n"
            + progress
            + "\n\n"
            + "智能建議:\n"
            + recommendations
        )
        report_dir = os.path.dirname(file_path)
        report_file_name = os.path.basename(file_path).replace(
            os.path.splitext(file_path)[1], "_report.txt"
        )
        report_file_path = os.path.join(report_dir, report_file_name)

        with open(report_file_path, "w", encoding="utf-8") as report_file:
            report_file.write(report)

        return report
