from flask import Flask, request, jsonify
import logging
from dotenv import load_dotenv
from src.ai_meeting_generator import run

app = Flask(__name__)

@app.route('/api', methods=['POST'])
def api():
    data = request.get_json()
    load_dotenv()

    run(
        meeting_name=data.get("meeting_name", "Team Meeting"), 
        file_path=data.get("file_path"), 
        api_key=data.get("api_key"),  
        audio_model=data.get("audio_model", "base"), 
        text_model=data.get("text_model", "gpt-3.5-turbo"),
        output_path=data.get("output_path", None),
        transcript_path=data.get("transcript_path", None),
        save_transcript=data.get("save_transcript", True),
        show_txt_cost=data.get("show_txt_cost", True),
        logging_level = logging.INFO
    )

    return jsonify({"message": "Meeting transcript generated successfully!"}), 200

if __name__ == '__main__':
    app.run(debug=True)
