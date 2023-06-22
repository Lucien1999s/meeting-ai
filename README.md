# AI meeting minutes automation


## Overview

In order to realize the automation of meeting records, this project will hand over the recorded audio files to AI technology to automatically transcribe verbatim manuscripts and generate reports such as analysis and key arrangement. In order to free up the time and energy spent by manpower on meeting minutes.

## Project Structure

```
.
├── README.md
├── config.json
├── main.py
├── requirements.txt
├── src
│   ├── auto_summarize.py
│   └── speech_to_text.py
└── test
```

## Quick Start

### 1. Clone project

```bash
git clone git@github.com:Lucien1999s/ai-meeting-project.git
```

### 2. Install requirements

```bash
pip install -r requirements.txt
```

### 3. Set up .env with .env.example

```bash
OPENAI_API_KEY = "Your_OpenAI_API_Key"
```

### 4. Set up config.json

```bash
{
    "file_url": "Your_Audio_File_path",
    "meeting_name": "Your_Meeting_Title",
    "use_package": true
}
```

- use_package: A boolean value indicating whether to use the Whisper package. Set it to true if you want to use the Whisper package for transcription, or set it to false to use the Whisper API ,the default is true.

### 5. Launch it

```bash
python main.py
```

## Features

### 1. Speech to text (generate transcript txt file):

Input audio files (mp3, m4a, wav) will be automatically converted to verbatim.

### 2. Generate summary of meeting minutes

Analyze and generate summary of meeting minutes based on transcripts of meeting minutes.

### 3. Generate follow ups 

Analyze and generate follow ups of meeting minutes based on transcripts of meeting minutes.
