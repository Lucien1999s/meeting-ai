import argparse
import whisper

parser = argparse.ArgumentParser(description='Download Whisper models.')
parser.add_argument('--model', type=str, help='The model to be downloaded')
args = parser.parse_args()

if args.model == 'all':
    models = ["base", "medium", "small", "tiny"]
else:
    models = [args.model]

for model in models:
    whisper.load_model(model, download_root="src/whisper_model")

print(f"The {', '.join(models)} model(s) have been downloaded to the src/whisper_model directory.")
