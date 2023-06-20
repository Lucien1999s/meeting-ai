# AI meeting minutes automation


## Overview

In order to realize the automation of meeting records, this project will hand over the recorded audio files to AI technology to automatically transcribe verbatim manuscripts and generate reports such as analysis and key arrangement. In order to free up the time and energy spent by manpower on meeting minutes.

## Project Structure

```
.
├── README.md
├── config.json
├── .env.example
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

### 2. Set up .env with .env.example


### 3. Set up config.json


### 4. Install requirements

```bash
pip install -r requirements.txt
```

### 5. Launch it

```bash
python main.py
```

## Features

### 1. Speech to text (generate transcript txt file):

Input audio files (mp3, m4a, wav) will be automatically converted to verbatim.

### 2. Generate highlight of meeting minutes

Analyze and generate highlight of meeting minutes based on verbatim transcripts of meeting minutes.

### 3. Generate progress list 

Generate a progress list by analyzing and categorizing completed and pending tasks from meeting transcripts.

### 4. Give smart suggestions

Give smart suggestions based on pending tasks.