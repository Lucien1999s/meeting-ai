from pydub import AudioSegment
import openai
import math
import os
from dotenv import load_dotenv

load_dotenv()


class SpeechToTextConverter:
    def __init__(self):
        self.model = "whisper-1"
        openai.api_key = os.environ.get("OPENAI_API_KEY")

    def convert_to_mp3(self, file_path):
        """
        Converts an audio file to MP3 format.

        Args:
            file_path (str): The path of the audio file to be converted.
        
        Returns:
            None. Changes are made directly. 

        """
        if os.path.isdir(file_path):
            for file_name in os.listdir(file_path):
                sub_file_path = os.path.join(file_path, file_name)
                self.convert_to_mp3(sub_file_path)
        elif not file_path.lower().endswith(".mp3"):
            audio = AudioSegment.from_file(file_path)

            dir_name = os.path.dirname(file_path)
            base_name = os.path.splitext(os.path.basename(file_path))[0]
            mp3_path = os.path.join(dir_name, base_name + ".mp3")

            audio.export(mp3_path, format="mp3")

            print("Converted to MP3:", mp3_path)

    def split_audio(self, file_path, duration=900):
        """
        Splits an audio file into segments.

        Args:
            file_path (str): The path of the audio file to be split.
            duration (int, optional): _description_. Defaults to 900.

        Returns:
            str: The path of the directory containing the segmented audio files.

        """
        wav_file = None
        for file_name in os.listdir(file_path):
            if file_name.lower().endswith(".mp3"):
                wav_file = os.path.join(file_path, file_name)
                break

        if not wav_file:
            print("Can't find MP3 file")
            return

        audio_data = AudioSegment.from_file(wav_file, format="mp3")
        num_segments = math.ceil(audio_data.duration_seconds / duration)

        output_dir = os.path.join(file_path, "segments")
        os.makedirs(output_dir, exist_ok=True)

        for i in range(num_segments):
            start = i * duration * 1000
            end = min(start + duration * 1000, len(audio_data))
            segment = audio_data[start:end]
            output_path = os.path.join(output_dir, f"segment{i+1}.mp3")
            segment.export(output_path, format="mp3")

        print("Audio split completely. Saved in:", output_dir)
        return output_dir

    def speech_to_text(self, audios_path):
        """
        Performs speech-to-text conversion on segmented audio files and generates a text file.

        Args:
            audios_path (str): The path of the directory containing the segmented audio files.

        Returns:
            str: The path of the generated text file.

        """
        transcriptions = []

        for file_name in sorted(os.listdir(audios_path)):
            if file_name.endswith(".mp3"):
                input_file = os.path.join(audios_path, file_name)
                with open(input_file, "rb") as audio_file:
                    transcript = openai.Audio.transcribe(self.model, audio_file)
                    transcription = transcript["text"].replace(" ", "\n")
                    transcriptions.append(transcription)
        path = os.path.dirname(audios_path)
        base_name = os.path.basename(path)
        transcriptions_path = os.path.join(path, base_name + ".txt")
        with open(transcriptions_path, "w") as f:
            f.write("\n".join(transcriptions))

        print("Complete speech to text")
        return transcriptions_path

    def speech_to_text_go(self, file_path):
        """
        Performs speech-to-text conversion on an audio file.

        Args:
            file_path (str): The path of the audio file to be converted.

        Returns:
            str: The path of the generated text file.
            
        """
        data_path = os.path.dirname(file_path)
        self.convert_to_mp3(file_path)
        audio_path = self.split_audio(data_path)
        return self.speech_to_text(audio_path)
