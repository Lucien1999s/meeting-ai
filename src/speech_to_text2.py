import whisper

model = whisper.load_model("small")
result = model.transcribe("/Users/lucienlin/pyProjects/lucien-ai-meeting/data/test.mp3")
print(result["text"])